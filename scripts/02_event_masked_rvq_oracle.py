#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import common


EVENT_ROUTES = [
    ("E1p5_event4", "E1.5 base + event K=4", 2, 4),
    ("E1p5_event8", "E1.5 base + event K=8", 2, 8),
    ("E3_event8", "E3 base + event K=8", 4, 8),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Frozen EnCodec event-masked RVQ oracle.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, required=True)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--max_seconds", type=float, default=0.0)
    parser.add_argument("--event_quantile", type=float, default=0.75)
    parser.add_argument("--event_min_ratio", type=float, default=0.08)
    parser.add_argument("--event_max_ratio", type=float, default=0.20)
    parser.add_argument("--event_dilate_frames", type=int, default=1)
    parser.add_argument("--seed", type=int, default=1372)
    parser.add_argument("--clean", action="store_true")
    return parser.parse_args()


def render_route(model, z_layers, source, sr, model_len, clip, case_dir, route_id, label, family, active, event_mask, kbps, anchor_metrics):
    decoded_24 = common.decode_active_k(model, z_layers, active, model_len)
    decoded = common.match_length(common.resample_to(decoded_24.squeeze(0), model.sample_rate, sr), source.shape[-1])
    wav_path = case_dir / f"{route_id}.wav"
    common.write_wav(wav_path, decoded, sr)
    metrics = common.metric_bundle(source, decoded, sr, event_mask)
    metric_row = {
        "clip_id": clip.clip_id,
        "route_id": route_id,
        "route_family": family,
        "kbps": kbps,
        **metrics,
        "delta_event_error_vs_anchor": "" if anchor_metrics is None else metrics["event_error"] - anchor_metrics["event_error"],
        "delta_background_error_vs_anchor": "" if anchor_metrics is None else metrics["background_error"] - anchor_metrics["background_error"],
    }
    return wav_path, metric_row


def main() -> int:
    args = parse_args()
    common.set_seed(args.seed)
    if args.clean:
        common.clean_dir(args.out_dir)
    else:
        common.ensure_dir(args.out_dir)
    clips = common.load_manifest(args.manifest)
    model = common.make_model(args.device)
    listening_rows = []
    metric_rows = []
    rate_rows = []
    verdict_rows = []

    for clip in clips:
        source, model_wav, sr = common.load_for_encodec(clip, model, args.max_seconds)
        duration = float(source.shape[-1]) / float(sr)
        z_layers, _codes = common.encode_layers(model, model_wav, k_max=8)
        frame_count = int(z_layers.shape[-1])
        event_mask, score = common.event_mask_from_model_wav(
            model_wav,
            frame_count,
            quantile=args.event_quantile,
            min_ratio=args.event_min_ratio,
            max_ratio=args.event_max_ratio,
            dilate_frames=args.event_dilate_frames,
        )
        case_dir = args.out_dir / "review_bundle" / "wavs" / clip.clip_id
        r0_path = case_dir / "R0_original.wav"
        common.write_wav(r0_path, source, sr)
        listening_rows.append(common.route_row(clip, "R0_original", "Original source", "reference", r0_path, duration, sr, 0.0))

        anchors: dict[str, dict[str, float]] = {}
        for k, route_id, label, kbps in [
            (2, "E1p5_K2_fixed", "EnCodec K=2 fixed", 1.5),
            (4, "E3_K4_fixed", "EnCodec K=4 fixed", 3.0),
            (8, "E6_K8_fixed", "EnCodec K=8 fixed", 6.0),
        ]:
            active = np.full(frame_count, k, dtype=np.int16)
            wav_path, metric_row = render_route(model, z_layers, source, sr, model_wav.shape[-1], clip, case_dir, route_id, label, "fixed_encodec_prefix_k", active, event_mask, kbps, None)
            anchors[route_id] = {key: metric_row[key] for key in common.METRIC_FIELDS if key in metric_row}
            metric_rows.append(metric_row)
            listening_rows.append(common.route_row(clip, route_id, label, "fixed_encodec_prefix_k", wav_path, duration, sr, kbps))
            rate_rows.append({"clip_id": clip.clip_id, "route_id": route_id, "mean_active_k": k, "code_kbps": kbps, "rle_header_kbps": 0.0, "total_kbps": kbps, "event_frame_ratio": float(np.mean(event_mask))})

        controls = [
            ("", "correct_event", event_mask),
            ("_random", "random_frame_control", common.matched_random_mask(event_mask, args.seed + len(metric_rows))),
            ("_background", "background_frame_control", common.matched_background_mask(event_mask, score)),
        ]
        for base_route, label, base_k, event_k in EVENT_ROUTES:
            anchor_id = "E1p5_K2_fixed" if base_k == 2 else "E3_K4_fixed"
            anchor_metrics = anchors[anchor_id]
            for suffix, control_name, mask in controls:
                route_id = base_route + suffix
                active = common.active_k(base_k, event_k, mask)
                rate = common.rate_for_active_k(active, duration)
                wav_path, metric_row = render_route(
                    model,
                    z_layers,
                    source,
                    sr,
                    model_wav.shape[-1],
                    clip,
                    case_dir,
                    route_id,
                    label if not suffix else f"{label} ({control_name})",
                    "event_masked_rvq",
                    active,
                    event_mask,
                    rate["total_kbps"],
                    anchor_metrics,
                )
                metric_rows.append(metric_row)
                listening_rows.append(common.route_row(clip, route_id, label, "event_masked_rvq", wav_path, duration, sr, rate["total_kbps"], control_name))
                rate_rows.append({"clip_id": clip.clip_id, "route_id": route_id, **rate, "event_frame_ratio": float(np.mean(mask))})

        verdict_rows.append(
            {
                "clip_id": clip.clip_id,
                "E1p5_event4_vs_E1p5": "",
                "E1p5_event8_vs_E1p5": "",
                "E3_event8_vs_E3": "",
                "controls_match_improvement": "",
                "artifact_type": "",
                "promotion_note": "",
            }
        )

    common.write_csv(args.out_dir / "review_bundle" / "listening_manifest.csv", listening_rows, common.LISTENING_FIELDS)
    common.write_csv(args.out_dir / "metrics.csv", metric_rows, common.METRIC_FIELDS)
    common.write_csv(args.out_dir / "rate_ledger.csv", rate_rows, ["clip_id", "route_id", "mean_active_k", "code_kbps", "rle_header_bits", "rle_header_kbps", "total_kbps", "event_frame_ratio"])
    common.write_csv(args.out_dir / "manual_verdict_template.csv", verdict_rows, ["clip_id", "E1p5_event4_vs_E1p5", "E1p5_event8_vs_E1p5", "E3_event8_vs_E3", "controls_match_improvement", "artifact_type", "promotion_note"])
    common.write_json(
        args.out_dir / "summary.json",
        {
            "decision": "event_masked_rvq_oracle_ready_for_listening",
            "clip_count": len(clips),
            "not_candidate_route": True,
            "promotion_claim_allowed_before_listening": False,
            "gate": "event routes must audibly beat fixed anchors and not be matched by random/background controls",
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
