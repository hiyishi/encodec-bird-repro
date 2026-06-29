from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
import torchaudio


ENCODEC_SAMPLE_RATE = 24000
ENCODEC_FRAME_RATE = 75.0
KBPS_PER_CODEBOOK = 0.75
BITS_PER_CODE = 10
DEFAULT_ROUTE_QUESTION = "Manual listening gate: does this route audibly beat the same-pack EnCodec anchor?"


@dataclass
class Clip:
    clip_id: str
    wav_path: Path
    split: str = "eval"
    species: str = ""
    group: str = ""


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def clean_dir(path: Path) -> None:
    path = path.resolve()
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_manifest(path: Path) -> list[Clip]:
    base = path.resolve().parent
    rows: list[Clip] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "clip_id" not in reader.fieldnames or "wav_path" not in reader.fieldnames:
            raise ValueError("manifest must contain at least clip_id,wav_path columns")
        for row in reader:
            clip_id = str(row.get("clip_id", "")).strip()
            wav_raw = str(row.get("wav_path", "")).strip()
            if not clip_id or not wav_raw:
                continue
            wav_path = Path(wav_raw)
            if not wav_path.is_absolute():
                wav_path = base / wav_path
            rows.append(
                Clip(
                    clip_id=safe_id(clip_id),
                    wav_path=wav_path.resolve(),
                    split=str(row.get("split", "eval") or "eval").strip(),
                    species=str(row.get("species", "") or "").strip(),
                    group=str(row.get("group", "") or "").strip(),
                )
            )
    if not rows:
        raise ValueError(f"manifest has no usable rows: {path}")
    missing = [str(row.wav_path) for row in rows if not row.wav_path.exists()]
    if missing:
        raise FileNotFoundError("missing wav files:\n" + "\n".join(missing[:20]))
    return rows


def safe_id(text: str) -> str:
    out = []
    for ch in text:
        if ch.isalnum() or ch in ("-", "_", "."):
            out.append(ch)
        else:
            out.append("_")
    value = "".join(out).strip("._")
    return value or "clip"


def make_model(device: str = "auto"):
    from encodec import EncodecModel

    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = EncodecModel.encodec_model_24khz().to(torch.device(device))
    model.eval()
    model.set_target_bandwidth(6.0)
    for param in model.parameters():
        param.requires_grad_(False)
    return model


def read_wav_mono(path: Path) -> tuple[torch.Tensor, int]:
    wav, sr = torchaudio.load(str(path))
    wav = wav.float()
    if wav.shape[0] > 1:
        wav = wav.mean(dim=0, keepdim=True)
    return wav.contiguous(), int(sr)


def trim_seconds(wav: torch.Tensor, sr: int, max_seconds: float) -> torch.Tensor:
    if max_seconds <= 0:
        return wav
    n = min(wav.shape[-1], int(round(max_seconds * sr)))
    return wav[..., :n].contiguous()


def load_for_encodec(clip: Clip, model, max_seconds: float = 0.0) -> tuple[torch.Tensor, torch.Tensor, int]:
    from encodec.utils import convert_audio

    wav, sr = read_wav_mono(clip.wav_path)
    wav = trim_seconds(wav, sr, max_seconds)
    model_wav = convert_audio(wav, sr, model.sample_rate, model.channels).unsqueeze(0)
    model_wav = model_wav.to(next(model.parameters()).device).contiguous()
    return wav.contiguous(), model_wav, sr


def match_length(wav: torch.Tensor, length: int) -> torch.Tensor:
    if wav.shape[-1] > length:
        return wav[..., :length].contiguous()
    if wav.shape[-1] < length:
        return F.pad(wav, (0, length - wav.shape[-1])).contiguous()
    return wav.contiguous()


def resample_to(wav: torch.Tensor, src_sr: int, dst_sr: int) -> torch.Tensor:
    if int(src_sr) == int(dst_sr):
        return wav.contiguous()
    return torchaudio.functional.resample(wav, int(src_sr), int(dst_sr)).contiguous()


def write_wav(path: Path, wav: torch.Tensor | np.ndarray, sr: int) -> None:
    ensure_dir(path.parent)
    if isinstance(wav, np.ndarray):
        tensor = torch.from_numpy(wav.astype(np.float32))
        if tensor.dim() == 1:
            tensor = tensor.unsqueeze(0)
    else:
        tensor = wav.detach().cpu().float()
        if tensor.dim() == 1:
            tensor = tensor.unsqueeze(0)
        if tensor.dim() == 3:
            tensor = tensor.squeeze(0)
    tensor = torch.clamp(tensor, -1.0, 1.0)
    torchaudio.save(str(path), tensor, int(sr))


def encode_layers(model, model_wav: torch.Tensor, k_max: int = 8) -> tuple[torch.Tensor, torch.Tensor]:
    """Return per-layer quantized vectors [K,B,D,T] and codes [K,B,T]."""
    with torch.no_grad():
        emb = model.encoder(model_wav)
        codes_kbt = model.quantizer.vq.encode(emb, n_q=int(k_max))
        layers = []
        for idx in range(int(k_max)):
            layers.append(model.quantizer.vq.layers[idx].decode(codes_kbt[idx]))
        z_layers = torch.stack(layers, dim=0).contiguous()
    return z_layers, codes_kbt.contiguous()


def decode_active_k(model, z_layers: torch.Tensor, active_k: np.ndarray, trim_to: int) -> torch.Tensor:
    active = torch.as_tensor(active_k.astype(np.int64), device=z_layers.device)
    layer_ids = torch.arange(z_layers.shape[0], device=z_layers.device).view(-1, 1, 1, 1)
    mask = (layer_ids < active.view(1, 1, 1, -1)).to(z_layers.dtype)
    with torch.no_grad():
        z_q = (z_layers * mask).sum(dim=0)
        out = model.decoder(z_q)
    return out[..., :trim_to].detach().cpu().contiguous()


def decode_k(model, z_layers: torch.Tensor, k: int, trim_to: int) -> torch.Tensor:
    active = np.full(int(z_layers.shape[-1]), int(k), dtype=np.int16)
    return decode_active_k(model, z_layers, active, trim_to)


def event_mask_from_model_wav(
    model_wav: torch.Tensor,
    frame_count: int,
    quantile: float = 0.75,
    min_ratio: float = 0.08,
    max_ratio: float = 0.20,
    dilate_frames: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    audio = model_wav.detach().cpu().numpy().reshape(-1).astype(np.float32)
    if frame_count <= 0:
        return np.zeros(0, dtype=bool), np.zeros(0, dtype=np.float32)
    chunks = np.array_split(audio, int(frame_count))
    rms = np.array([np.sqrt(np.mean(chunk * chunk) + 1.0e-12) for chunk in chunks], dtype=np.float32)
    zcr_like = np.array([np.mean(np.abs(np.diff(chunk))) if len(chunk) > 1 else 0.0 for chunk in chunks], dtype=np.float32)
    onset = np.maximum(np.diff(np.concatenate([[rms[0]], rms])), 0.0).astype(np.float32)
    score = normalize01(rms) + 0.65 * normalize01(zcr_like) + 0.85 * normalize01(onset)
    q = float(np.clip(quantile, 0.01, 0.99))
    mask = score >= float(np.quantile(score, q))
    min_count = int(math.ceil(float(min_ratio) * frame_count))
    max_count = int(math.floor(float(max_ratio) * frame_count)) if max_ratio > 0 else frame_count
    max_count = max(min_count, min(frame_count, max_count))
    if int(mask.sum()) < min_count:
        idx = np.argsort(score)[-min_count:]
        mask = np.zeros(frame_count, dtype=bool)
        mask[idx] = True
    mask = dilate_bool(mask, int(dilate_frames))
    if int(mask.sum()) > max_count:
        idx = np.argsort(score)[-max_count:]
        trimmed = np.zeros(frame_count, dtype=bool)
        trimmed[idx] = True
        mask = trimmed
    return mask.astype(bool), score.astype(np.float32)


def normalize01(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    lo = float(np.percentile(x, 5))
    hi = float(np.percentile(x, 95))
    if hi <= lo + 1.0e-12:
        return np.zeros_like(x, dtype=np.float32)
    return np.clip((x - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)


def dilate_bool(mask: np.ndarray, radius: int) -> np.ndarray:
    out = np.asarray(mask, dtype=bool).copy()
    if radius <= 0:
        return out
    src = out.copy()
    for shift in range(1, radius + 1):
        out[shift:] |= src[:-shift]
        out[:-shift] |= src[shift:]
    return out


def matched_random_mask(mask: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    count = int(np.sum(mask))
    out = np.zeros_like(mask, dtype=bool)
    if count > 0:
        out[rng.choice(np.arange(len(mask)), size=count, replace=False)] = True
    return out


def matched_background_mask(mask: np.ndarray, score: np.ndarray) -> np.ndarray:
    count = int(np.sum(mask))
    out = np.zeros_like(mask, dtype=bool)
    if count <= 0:
        return out
    eligible = np.where(~mask)[0]
    if len(eligible) < count:
        eligible = np.arange(len(mask))
    ranked = eligible[np.argsort(score[eligible])]
    out[ranked[:count]] = True
    return out


def active_k(base_k: int, event_k: int, mask: np.ndarray) -> np.ndarray:
    out = np.full(len(mask), int(base_k), dtype=np.int16)
    out[np.asarray(mask, dtype=bool)] = int(event_k)
    return out


def run_count(mask: np.ndarray) -> int:
    bits = np.asarray(mask, dtype=np.int8)
    if bits.size == 0:
        return 0
    return int(bits[0] == 1) + int(np.sum((bits[1:] == 1) & (bits[:-1] == 0)))


def rate_for_active_k(active: np.ndarray, duration: float, include_rle_header: bool = True) -> dict[str, Any]:
    mean_k = float(np.mean(active)) if len(active) else 0.0
    code_kbps = KBPS_PER_CODEBOOK * mean_k
    rle_bits = 0
    if include_rle_header and len(active):
        changes = np.concatenate([[True], active[1:] != active[:-1]])
        runs = int(np.sum(changes))
        bits_per_run = 2 * int(math.ceil(math.log2(max(2, len(active))))) + 3
        rle_bits = runs * bits_per_run
    rle_kbps = rle_bits / max(1.0e-9, float(duration)) / 1000.0
    return {
        "mean_active_k": mean_k,
        "code_kbps": code_kbps,
        "rle_header_bits": int(rle_bits),
        "rle_header_kbps": rle_kbps,
        "total_kbps": code_kbps + rle_kbps,
    }


def frame_mask_to_sample_mask(mask: np.ndarray, sample_count: int, sr: int) -> np.ndarray:
    if len(mask) == 0 or sample_count <= 0:
        return np.zeros(max(0, sample_count), dtype=bool)
    idx = np.floor(np.arange(sample_count) * ENCODEC_FRAME_RATE / float(sr)).astype(np.int64)
    idx = np.clip(idx, 0, len(mask) - 1)
    return mask[idx]


def exact_residual_ub(source: torch.Tensor, base: torch.Tensor, frame_mask: np.ndarray, sr: int) -> torch.Tensor:
    source = source.detach().cpu().float()
    base = match_length(base.detach().cpu().float(), source.shape[-1])
    sample_mask = frame_mask_to_sample_mask(frame_mask, source.shape[-1], sr)
    out = base.clone()
    m = torch.from_numpy(sample_mask).to(dtype=torch.bool)
    out[..., m] = source[..., m]
    return out


def select_top_event_frames(full_mask: np.ndarray, score: np.ndarray, extra_kbps: float, reference_kbps: float) -> np.ndarray:
    full_mask = np.asarray(full_mask, dtype=bool)
    out = np.zeros_like(full_mask, dtype=bool)
    count = int(np.sum(full_mask))
    if count <= 0 or extra_kbps <= 0:
        return out
    keep = int(math.ceil(count * min(1.0, float(extra_kbps) / max(1.0e-9, float(reference_kbps)))))
    keep = max(1, min(count, keep))
    eligible = np.where(full_mask)[0]
    ranked = eligible[np.argsort(score[eligible])]
    out[ranked[-keep:]] = True
    return out


def stft_logmag(wav: torch.Tensor, n_fft: int = 1024, hop: int = 256) -> torch.Tensor:
    wav = wav.detach().cpu().float().reshape(-1)
    window = torch.hann_window(n_fft)
    spec = torch.stft(wav, n_fft=n_fft, hop_length=hop, window=window, return_complex=True)
    return torch.log1p(spec.abs()).transpose(0, 1).contiguous()


def resize_mask(mask: np.ndarray, length: int) -> np.ndarray:
    if length <= 0:
        return np.zeros(0, dtype=bool)
    if len(mask) == length:
        return mask.astype(bool)
    if len(mask) == 0:
        return np.zeros(length, dtype=bool)
    idx = np.floor(np.linspace(0, len(mask), num=length, endpoint=False)).astype(np.int64)
    idx = np.clip(idx, 0, len(mask) - 1)
    return mask[idx].astype(bool)


def metric_bundle(source: torch.Tensor, test: torch.Tensor, sr: int, event_mask75: np.ndarray) -> dict[str, float]:
    source = source.detach().cpu().float()
    test = match_length(test.detach().cpu().float(), source.shape[-1])
    ref_lm = stft_logmag(source)
    test_lm = stft_logmag(test)
    n = min(ref_lm.shape[0], test_lm.shape[0])
    ref_lm = ref_lm[:n]
    test_lm = test_lm[:n]
    frame_mask = resize_mask(event_mask75, n)
    if not np.any(frame_mask):
        frame_mask[:] = True
    bg_mask = ~frame_mask
    if not np.any(bg_mask):
        bg_mask[:] = True
    freqs = torch.fft.rfftfreq(1024, d=1.0 / float(sr))
    high = (freqs >= 6000.0) & (freqs <= min(float(sr) / 2.0 - 1.0, 15000.0))
    diff = torch.abs(ref_lm - test_lm)
    event_idx = torch.from_numpy(frame_mask)
    bg_idx = torch.from_numpy(bg_mask)
    event_l1 = float(diff[event_idx].mean().item())
    bg_l1 = float(diff[bg_idx].mean().item())
    event_high = float(diff[event_idx][:, high].mean().item()) if bool(high.any()) else event_l1
    bg_high = float(diff[bg_idx][:, high].mean().item()) if bool(high.any()) else bg_l1
    return {
        "global_logmag_l1": float(diff.mean().item()),
        "event_logmag_l1": event_l1,
        "background_logmag_l1": bg_l1,
        "event_highband_logmag_l1": event_high,
        "background_highband_logmag_l1": bg_high,
        "event_error": 0.65 * event_l1 + 0.35 * event_high,
        "background_error": 0.65 * bg_l1 + 0.35 * bg_high,
    }


def route_row(
    clip: Clip,
    route_id: str,
    route_label: str,
    route_family: str,
    wav_path: Path,
    duration: float,
    sr: int,
    kbps: float,
    notes: str = "",
) -> dict[str, Any]:
    return {
        "clip_id": clip.clip_id,
        "split": clip.split,
        "species": clip.species,
        "group": clip.group,
        "route_id": route_id,
        "route_label": route_label,
        "route_family": route_family,
        "bundle_wav_path": str(wav_path.resolve()),
        "sha256": sha256(wav_path),
        "duration_seconds": duration,
        "sample_rate": int(sr),
        "kbps": float(kbps),
        "question": DEFAULT_ROUTE_QUESTION,
        "notes": notes,
    }


LISTENING_FIELDS = [
    "clip_id",
    "split",
    "species",
    "group",
    "route_id",
    "route_label",
    "route_family",
    "bundle_wav_path",
    "sha256",
    "duration_seconds",
    "sample_rate",
    "kbps",
    "question",
    "notes",
]

METRIC_FIELDS = [
    "clip_id",
    "route_id",
    "route_family",
    "kbps",
    "global_logmag_l1",
    "event_logmag_l1",
    "background_logmag_l1",
    "event_highband_logmag_l1",
    "background_highband_logmag_l1",
    "event_error",
    "background_error",
    "delta_event_error_vs_anchor",
    "delta_background_error_vs_anchor",
]
