#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import common


ROUTES = [
    (2, "E1p5_K2_fixed", "EnCodec K=2 fixed, about 1.5 kbps", 1.5),
    (4, "E3_K4_fixed", "EnCodec K=4 fixed, about 3 kbps", 3.0),
    (8, "E6_K8_fixed", "EnCodec K=8 fixed, about 6 kbps", 6.0),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build current EnCodec anchor WAVs for a manifest.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, required=True)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--max_seconds", type=float, default=0.0)
    parser.add_argument("--include_k1", action="store_true", help="Also render manual K=1, about 0.75 kbps.")
    parser.add_argument("--clean", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.clean:
        common.clean_dir(args.out_dir)
    else:
        common.ensure_dir(args.out_dir)
    clips = common.load_manifest(args.manifest)
    model = common.make_model(args.device)
    routes = list(ROUTES)
    if args.include_k1:
        routes.insert(0, (1, "E0p75_K1_fixed", "EnCodec K=1 fixed, about 0.75 kbps", 0.75))

    listening_rows = []
    metric_rows = []
    rate_rows = []
    for clip in clips:
        source, model_wav, sr = common.load_for_encodec(clip, model, args.max_seconds)
        duration = float(source.shape[-1]) / float(sr)
        z_layers, _codes = common.encode_layers(model, model_wav, k_max=8)
        case_dir = args.out_dir / "review_bundle" / "wavs" / clip.clip_id
        r0_path = case_dir / "R0_original.wav"
        common.write_wav(r0_path, source, sr)
        listening_rows.append(common.route_row(clip, "R0_original", "Original source", "reference", r0_path, duration, sr, 0.0))
        event_mask, _score = common.event_mask_from_model_wav(model_wav, int(z_layers.shape[-1]))

        anchor_metrics = None
        for k, route_id, label, kbps in routes:
            decoded_24 = common.decode_k(model, z_layers, k, model_wav.shape[-1])
            decoded = common.match_length(common.resample_to(decoded_24.squeeze(0), model.sample_rate, sr), source.shape[-1])
            wav_path = case_dir / f"{route_id}.wav"
            common.write_wav(wav_path, decoded, sr)
            listening_rows.append(common.route_row(clip, route_id, label, "fixed_encodec_prefix_k", wav_path, duration, sr, kbps))
            metrics = common.metric_bundle(source, decoded, sr, event_mask)
            if route_id == "E1p5_K2_fixed":
                anchor_metrics = metrics
            metric_rows.append(
                {
                    "clip_id": clip.clip_id,
                    "route_id": route_id,
                    "route_family": "fixed_encodec_prefix_k",
                    "kbps": kbps,
                    **metrics,
                    "delta_event_error_vs_anchor": "" if anchor_metrics is None else metrics["event_error"] - anchor_metrics["event_error"],
                    "delta_background_error_vs_anchor": "" if anchor_metrics is None else metrics["background_error"] - anchor_metrics["background_error"],
                }
            )
            rate_rows.append(
                {
                    "clip_id": clip.clip_id,
                    "route_id": route_id,
                    "n_codebooks": k,
                    "code_kbps": kbps,
                    "duration_seconds": duration,
                    "event_frame_ratio": float(np.mean(event_mask)),
                }
            )

    common.write_csv(args.out_dir / "review_bundle" / "listening_manifest.csv", listening_rows, common.LISTENING_FIELDS)
    common.write_csv(args.out_dir / "metrics.csv", metric_rows, common.METRIC_FIELDS)
    common.write_csv(args.out_dir / "rate_ledger.csv", rate_rows, ["clip_id", "route_id", "n_codebooks", "code_kbps", "duration_seconds", "event_frame_ratio"])
    common.write_json(
        args.out_dir / "summary.json",
        {
            "decision": "anchors_ready_for_listening",
            "clip_count": len(clips),
            "routes": [row[1] for row in routes],
            "promotion_claim_allowed": False,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
