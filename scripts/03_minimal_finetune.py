#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import torch
import torch.nn.functional as F

import common


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal neutral EnCodec fine-tune smoke.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, required=True)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--train_split", default="train")
    parser.add_argument("--eval_split", default="eval")
    parser.add_argument("--train_clips", type=int, default=8)
    parser.add_argument("--eval_clips", type=int, default=6)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--chunk_seconds", type=float, default=1.5)
    parser.add_argument("--bandwidths", default="1.5,3.0")
    parser.add_argument("--loss_mode", default="neutral", choices=["neutral", "event"])
    parser.add_argument("--lambda_event", type=float, default=0.25)
    parser.add_argument("--lambda_onset", type=float, default=0.10)
    parser.add_argument("--train_scope", default="decoder", choices=["decoder", "decoder_encoder_note"])
    parser.add_argument("--max_seconds", type=float, default=10.0)
    parser.add_argument("--seed", type=int, default=1381)
    parser.add_argument("--clean", action="store_true")
    return parser.parse_args()


def mrstft_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    loss = pred.new_tensor(0.0)
    for n_fft in [256, 512, 1024]:
        hop = n_fft // 4
        window = torch.hann_window(n_fft, device=pred.device)
        p = torch.stft(pred.squeeze(1), n_fft=n_fft, hop_length=hop, window=window, return_complex=True)
        t = torch.stft(target.squeeze(1), n_fft=n_fft, hop_length=hop, window=window, return_complex=True)
        loss = loss + torch.mean(torch.abs(torch.log1p(p.abs()) - torch.log1p(t.abs())))
    return loss / 3.0


def set_decoder_trainable(model) -> None:
    for param in model.parameters():
        param.requires_grad_(False)
    for param in model.decoder.parameters():
        param.requires_grad_(True)
    model.encoder.eval()
    model.quantizer.eval()
    model.decoder.train()


def reconstruct_decoder_train(model, x: torch.Tensor, bandwidth: float) -> torch.Tensor:
    model.set_target_bandwidth(float(bandwidth))
    with torch.no_grad():
        emb = model.encoder(x)
        q = model.quantizer(emb, model.frame_rate, model.bandwidth)
    return model.decoder(q.quantized)[..., : x.shape[-1]]


def reconstruct_eval(model, x: torch.Tensor, bandwidth: float) -> torch.Tensor:
    model.set_target_bandwidth(float(bandwidth))
    with torch.no_grad():
        frames = model.encode(x)
        out = model.decode(frames)[..., : x.shape[-1]]
    return out.detach().cpu()


def event_weighted_l1(pred: torch.Tensor, target: torch.Tensor, lambda_event: float) -> torch.Tensor:
    frame_count = max(1, int(round(target.shape[-1] / 320)))
    mask, _score = common.event_mask_from_model_wav(target.detach(), frame_count)
    sample_mask = common.frame_mask_to_sample_mask(mask, target.shape[-1], 24000)
    weights = torch.ones_like(target)
    weights[..., torch.from_numpy(sample_mask).to(target.device)] += float(lambda_event)
    return torch.mean(torch.abs(pred - target) * weights)


def onset_region_l1(pred: torch.Tensor, target: torch.Tensor, lambda_onset: float) -> torch.Tensor:
    hop = 320
    n_frames = max(1, int(target.shape[-1] // hop))
    pred_env = pred[..., : n_frames * hop].reshape(pred.shape[0], pred.shape[1], n_frames, hop).abs().mean(dim=-1)
    target_env = target[..., : n_frames * hop].reshape(target.shape[0], target.shape[1], n_frames, hop).abs().mean(dim=-1)
    pred_on = torch.relu(pred_env[..., 1:] - pred_env[..., :-1])
    target_on = torch.relu(target_env[..., 1:] - target_env[..., :-1])
    return float(lambda_onset) * torch.mean(torch.abs(pred_on - target_on))


def crop_or_pad(x: torch.Tensor, samples: int) -> torch.Tensor:
    if x.shape[-1] >= samples:
        start = max(0, (x.shape[-1] - samples) // 2)
        return x[..., start : start + samples].contiguous()
    return F.pad(x, (0, samples - x.shape[-1])).contiguous()


def main() -> int:
    args = parse_args()
    common.set_seed(args.seed)
    if args.clean:
        common.clean_dir(args.out_dir)
    else:
        common.ensure_dir(args.out_dir)
    clips = common.load_manifest(args.manifest)
    train = [c for c in clips if c.split == args.train_split][: args.train_clips]
    eval_clips = [c for c in clips if c.split == args.eval_split][: args.eval_clips]
    if not train:
        train = clips[: args.train_clips]
    if not eval_clips:
        eval_clips = clips[: args.eval_clips]
    model = common.make_model(args.device)
    bandwidths = [float(part) for part in str(args.bandwidths).split(",") if part.strip()]
    train_wavs = [common.load_for_encodec(c, model, args.max_seconds)[1] for c in train]
    chunk_samples = int(round(args.chunk_seconds * model.sample_rate))
    chunks = [crop_or_pad(w, chunk_samples) for w in train_wavs]
    set_decoder_trainable(model)
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr)
    train_log = []
    for step in range(1, args.steps + 1):
        x = chunks[(step - 1) % len(chunks)]
        bw = bandwidths[(step - 1) % len(bandwidths)]
        pred = reconstruct_decoder_train(model, x, bw)
        if args.loss_mode == "event":
            l1 = event_weighted_l1(pred, x, args.lambda_event)
            onset = onset_region_l1(pred, x, args.lambda_onset)
        else:
            l1 = torch.mean(torch.abs(pred - x))
            onset = pred.new_tensor(0.0)
        stft = mrstft_loss(pred, x)
        loss = l1 + 0.35 * stft + onset
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
        opt.step()
        if step == 1 or step == args.steps or step % max(1, args.steps // 4) == 0:
            train_log.append(
                {
                    "step": step,
                    "bandwidth_kbps": bw,
                    "loss": float(loss.detach().cpu()),
                    "l1": float(l1.detach().cpu()),
                    "mrstft": float(stft.detach().cpu()),
                    "onset": float(onset.detach().cpu()),
                    "loss_mode": args.loss_mode,
                }
            )

    model.eval()
    ckpt_path = args.out_dir / "checkpoint" / "minimal_decoder_ft.pt"
    common.ensure_dir(ckpt_path.parent)
    torch.save({"model_state": model.state_dict(), "args": vars(args), "train_log": train_log}, ckpt_path)

    listening_rows = []
    metric_rows = []
    rate_rows = []
    for clip in eval_clips:
        source, model_wav, sr = common.load_for_encodec(clip, model, args.max_seconds)
        duration = float(source.shape[-1]) / float(sr)
        event_mask, _score = common.event_mask_from_model_wav(model_wav, max(1, int(round(model_wav.shape[-1] / 320))))
        case_dir = args.out_dir / "review_bundle" / "wavs" / clip.clip_id
        r0_path = case_dir / "R0_original.wav"
        common.write_wav(r0_path, source, sr)
        listening_rows.append(common.route_row(clip, "R0_original", "Original source", "reference", r0_path, duration, sr, 0.0))
        anchor_metrics = {}
        for bw in bandwidths:
            tag = str(bw).replace(".", "p")
            ft_prefix = "eventloss_ft" if args.loss_mode == "event" else "neutral_ft"
            ft_label = "Event-loss decoder FT" if args.loss_mode == "event" else "Neutral decoder FT"
            ft_family = "eventloss_finetune" if args.loss_mode == "event" else "neutral_finetune"
            for route_prefix, label, family in [
                ("official", f"Official EnCodec {bw:g} kbps", "official_encodec"),
                (ft_prefix, f"{ft_label} {bw:g} kbps", ft_family),
            ]:
                if route_prefix == "official":
                    fresh = common.make_model(args.device)
                    decoded_24 = reconstruct_eval(fresh, model_wav, bw)
                else:
                    decoded_24 = reconstruct_eval(model, model_wav, bw)
                decoded = common.match_length(common.resample_to(decoded_24.squeeze(0), model.sample_rate, sr), source.shape[-1])
                route_id = f"{route_prefix}_{tag}"
                wav_path = case_dir / f"{route_id}.wav"
                common.write_wav(wav_path, decoded, sr)
                listening_rows.append(common.route_row(clip, route_id, label, family, wav_path, duration, sr, bw))
                metrics = common.metric_bundle(source, decoded, sr, event_mask)
                if route_prefix == "official":
                    anchor_metrics[bw] = metrics
                anchor = anchor_metrics.get(bw)
                metric_rows.append(
                    {
                        "clip_id": clip.clip_id,
                        "route_id": route_id,
                        "route_family": family,
                        "kbps": bw,
                        **metrics,
                        "delta_event_error_vs_anchor": "" if anchor is None else metrics["event_error"] - anchor["event_error"],
                        "delta_background_error_vs_anchor": "" if anchor is None else metrics["background_error"] - anchor["background_error"],
                    }
                )
                rate_rows.append({"clip_id": clip.clip_id, "route_id": route_id, "kbps": bw, "checkpoint_path": str(ckpt_path) if route_prefix != "official" else ""})

    common.write_csv(args.out_dir / "train_log.csv", train_log, ["step", "bandwidth_kbps", "loss", "l1", "mrstft", "onset", "loss_mode"])
    common.write_csv(args.out_dir / "review_bundle" / "listening_manifest.csv", listening_rows, common.LISTENING_FIELDS)
    common.write_csv(args.out_dir / "metrics.csv", metric_rows, common.METRIC_FIELDS)
    common.write_csv(args.out_dir / "rate_ledger.csv", rate_rows, ["clip_id", "route_id", "kbps", "checkpoint_path"])
    common.write_csv(
        args.out_dir / "manual_verdict_template.csv",
        [{"clip_id": c.clip_id, "candidate_vs_official": "", "artifact_type": "", "event_clarity": "", "background_damage": "", "promotion_note": ""} for c in eval_clips],
        ["clip_id", "candidate_vs_official", "artifact_type", "event_clarity", "background_damage", "promotion_note"],
    )
    common.write_json(
        args.out_dir / "summary.json",
        {
            "decision": f"minimal_{args.loss_mode}_ft_ready_for_listening",
            "train_clip_count": len(train),
            "eval_clip_count": len(eval_clips),
            "steps": args.steps,
            "train_scope": "decoder_only_minimal_external_repro",
            "loss_mode": args.loss_mode,
            "lambda_event": args.lambda_event,
            "lambda_onset": args.lambda_onset,
            "checkpoint_path": str(ckpt_path.resolve()),
            "promotion_claim_allowed_before_listening": False,
            "gate": "neutral FT must not audibly degrade official EnCodec before any bird-event loss experiment",
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
