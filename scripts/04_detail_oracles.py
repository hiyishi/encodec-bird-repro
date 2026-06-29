#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import common


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A139/A140 exact-detail upper-bound oracles.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, required=True)
    parser.add_argument("--mode", default="both", choices=["a139", "a140", "both"])
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--max_seconds", type=float, default=0.0)
    parser.add_argument("--extra_budgets", default="0.10,0.25,0.50")
    parser.add_argument("--reference_detail_kbps", type=float, default=0.75)
    parser.add_argument("--event_quantile", type=float, default=0.75)
    parser.add_argument("--event_min_ratio", type=float, default=0.08)
    parser.add_argument("--event_max_ratio", type=float, default=0.20)
    parser.add_argument("--event_dilate_frames", type=int, default=2)
    parser.add_argument("--clean", action="store_true")
    return parser.parse_args()


def add_route(rows, metrics_rows, rate_rows, clip, route_id, label, family, wav_path, source, decoded, sr, duration, kbps, event_mask, anchor_metrics, notes):
    common.write_wav(wav_path, decoded, sr)
    rows.append(common.route_row(clip, route_id, label, family, wav_path, duration, sr, kbps, notes))
    metrics = common.metric_bundle(source, decoded, sr, event_mask)
    metrics_rows.append(
        {
            "clip_id": clip.clip_id,
            "route_id": route_id,
            "route_family": family,
            "kbps": kbps,
            **metrics,
            "delta_event_error_vs_anchor": "" if anchor_metrics is None else metrics["event_error"] - anchor_metrics["event_error"],
            "delta_background_error_vs_anchor": "" if anchor_metrics is None else metrics["background_error"] - anchor_metrics["background_error"],
        }
    )
    rate_rows.append({"clip_id": clip.clip_id, "route_id": route_id, "kbps": kbps, "notes": notes})
    return metrics


def main() -> int:
    args = parse_args()
    if args.clean:
        common.clean_dir(args.out_dir)
    else:
        common.ensure_dir(args.out_dir)
    clips = common.load_manifest(args.manifest)
    model = common.make_model(args.device)
    extra_budgets = [float(part) for part in str(args.extra_budgets).split(",") if part.strip()]
    listening_rows = []
    metric_rows = []
    rate_rows = []
    verdict_rows = []

    for clip in clips:
        source, model_wav, sr = common.load_for_encodec(clip, model, args.max_seconds)
        duration = float(source.shape[-1]) / float(sr)
        z_layers, _codes = common.encode_layers(model, model_wav, k_max=8)
        event_mask, score = common.event_mask_from_model_wav(
            model_wav,
            int(z_layers.shape[-1]),
            quantile=args.event_quantile,
            min_ratio=args.event_min_ratio,
            max_ratio=args.event_max_ratio,
            dilate_frames=args.event_dilate_frames,
        )
        case_dir = args.out_dir / "review_bundle" / "wavs" / clip.clip_id
        r0_path = case_dir / "R0_original.wav"
        common.write_wav(r0_path, source, sr)
        listening_rows.append(common.route_row(clip, "R0_original", "Original source", "reference", r0_path, duration, sr, 0.0))

        decoded_by_k = {}
        metrics_by_route = {}
        for k, route_id, label, kbps in [
            (1, "E0p75_K1_fixed", "EnCodec K=1 fixed, about 0.75 kbps", 0.75),
            (2, "E1p5_K2_fixed", "EnCodec K=2 fixed, about 1.5 kbps", 1.5),
            (4, "E3_K4_fixed", "EnCodec K=4 fixed, about 3 kbps", 3.0),
        ]:
            decoded_24 = common.decode_k(model, z_layers, k, model_wav.shape[-1])
            decoded = common.match_length(common.resample_to(decoded_24.squeeze(0), model.sample_rate, sr), source.shape[-1])
            decoded_by_k[k] = decoded
            anchor = metrics_by_route.get("E1p5_K2_fixed") if route_id != "E1p5_K2_fixed" else None
            metrics_by_route[route_id] = add_route(
                listening_rows,
                metric_rows,
                rate_rows,
                clip,
                route_id,
                label,
                "fixed_encodec_prefix_k",
                case_dir / f"{route_id}.wav",
                source,
                decoded,
                sr,
                duration,
                kbps,
                event_mask,
                anchor,
                "fixed EnCodec prefix-depth anchor",
            )

        if args.mode in ("a139", "both"):
            ub = common.exact_residual_ub(source, decoded_by_k[1], event_mask, sr)
            metrics_by_route["E0p75_plus_exact_event_residual_UB"] = add_route(
                listening_rows,
                metric_rows,
                rate_rows,
                clip,
                "E0p75_plus_exact_event_residual_UB",
                "E0.75 + exact event residual UB, 1.5 kbps total",
                "a139_same_rate_detail_oracle",
                case_dir / "E0p75_plus_exact_event_residual_UB.wav",
                source,
                ub,
                sr,
                duration,
                1.5,
                event_mask,
                metrics_by_route["E1p5_K2_fixed"],
                "Illegal upper bound: source residual injected at event frames; not a candidate bitstream.",
            )

        if args.mode in ("a140", "both"):
            for extra in extra_budgets:
                selected = common.select_top_event_frames(event_mask, score, extra, args.reference_detail_kbps)
                ub = common.exact_residual_ub(source, decoded_by_k[2], selected, sr)
                tag = f"{extra:.2f}".replace(".", "p")
                add_route(
                    listening_rows,
                    metric_rows,
                    rate_rows,
                    clip,
                    f"E1p5_plus_detailUB_{tag}",
                    f"E1.5 + {extra:g} kbps exact-detail UB",
                    "a140_marginal_side_channel_oracle",
                    case_dir / f"E1p5_plus_detailUB_{tag}.wav",
                    source,
                    ub,
                    sr,
                    duration,
                    1.5 + extra,
                    event_mask,
                    metrics_by_route["E1p5_K2_fixed"],
                    "Illegal upper bound: source residual injected at selected event frames; not a candidate bitstream.",
                )

        verdict_rows.append(
            {
                "clip_id": clip.clip_id,
                "A139_UB_vs_E1p5": "",
                "A140_0p10_vs_E1p5": "",
                "A140_0p25_vs_E1p5": "",
                "A140_0p50_vs_E1p5": "",
                "minimum_winning_extra_kbps": "",
                "artifact_type": "",
                "promotion_note": "",
            }
        )

    common.write_csv(args.out_dir / "review_bundle" / "listening_manifest.csv", listening_rows, common.LISTENING_FIELDS)
    common.write_csv(args.out_dir / "metrics.csv", metric_rows, common.METRIC_FIELDS)
    common.write_csv(args.out_dir / "rate_ledger.csv", rate_rows, ["clip_id", "route_id", "kbps", "notes"])
    common.write_csv(args.out_dir / "manual_verdict_template.csv", verdict_rows, ["clip_id", "A139_UB_vs_E1p5", "A140_0p10_vs_E1p5", "A140_0p25_vs_E1p5", "A140_0p50_vs_E1p5", "minimum_winning_extra_kbps", "artifact_type", "promotion_note"])
    common.write_json(
        args.out_dir / "summary.json",
        {
            "decision": "detail_oracles_ready_for_listening",
            "clip_count": len(clips),
            "mode": args.mode,
            "not_candidate_routes": True,
            "promotion_claim_allowed_before_listening": False,
            "gate": "if exact-detail UB does not audibly beat the EnCodec anchor, do not build a legal compressed side-channel for that route",
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
