# PS-CX A140.1 Marginal Side-Channel Value Oracle

Generated: 2026-06-29

## Decision State

```text
A139.0 same-rate hybrid replacement: no-go
A140.1 marginal side-channel value oracle: listening-tie / no-promote
manual listening date: 2026-06-30
promotion: no
```

A140.1 asks a narrower question than A139:

```text
Given EnCodec K2 at 1.5 kbps is strong,
how much extra encoder-derived bird-detail budget above E1.5
is needed before hard-case bird detail audibly improves?
```

This is not a production codec candidate. The side-channel routes are illegal
upper bounds because they inject exact source residual on selected event frames.
They only measure whether a tiny marginal detail budget is worth designing.

Manual listening verdict:

```text
E1.5 + 0.10 kbps exact-detail UB: no clear audible difference from E1.5
E1.5 + 0.25 kbps exact-detail UB: no clear audible difference from E1.5
E1.5 + 0.50 kbps exact-detail UB: no clear audible difference from E1.5

Promotion:
  no
```

The A140.1 fail gate is therefore triggered. The route does not justify a legal
side-channel token design.

## Artifact

```text
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/
```

Key files:

```text
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/summary.json
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/rate_ledger.csv
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/metrics.csv
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/side_channel_mask_summary.csv
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/review_bundle/listening_manifest.csv
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/review_bundle/a1401_manual_verdict_template.csv
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/review_bundle/a1401_manual_verdict.csv
```

## Routes

Each of the 6 heldout failure cases contains:

```text
R0_original
E1p5_K2_fixed
E1p5_plus_detailUB_0p10
E1p5_plus_detailUB_0p25
E1p5_plus_detailUB_0p50
E3_K4_fixed
```

Budget ledger:

```text
E1p5_K2_fixed:             1.50 kbps
E1p5_plus_detailUB_0p10:   1.60 kbps total
E1p5_plus_detailUB_0p25:   1.75 kbps total
E1p5_plus_detailUB_0p50:   2.00 kbps total
E3_K4_fixed:               3.00 kbps
```

The reference detail budget for the full A139-style event mask is `0.75 kbps`.
A140.1 selects only the top-scored event frames within each smaller marginal
budget:

```text
+0.10 kbps: 13.33% of full event mask
+0.25 kbps: 33.33% of full event mask
+0.50 kbps: 66.67% of full event mask
```

## Machine Checks

```text
eval cases: 6
listening rows: 36
candidate output rows: 30
rate ledger rows: 30
metrics rows: 30
side-channel mask rows: 18
```

Objective event-window error is monotone better than E1.5, but this is only a
readiness signal, not a promotion result:

```text
mean delta event error vs E1.5:
  +0.10 kbps: -0.1603
  +0.25 kbps: -0.4044
  +0.50 kbps: -0.7624
```

Listening remains the primary gate. In the manual listening pass on 2026-06-30,
the objective gains did not translate into obvious perceptual improvement.

## Listening Gate

Strong pass:

```text
E1.5 + 0.10 or +0.25 kbps UB clearly and stably beats E1.5,
without background damage, harshness, or brightness/noise cheating.
```

Weak pass:

```text
Only E1.5 + 0.50 kbps UB clearly beats E1.5.
This means marginal detail has value, but the useful budget is not tiny.
```

Fail:

```text
E1.5 + 0.50 kbps UB does not clearly beat E1.5.
Close EnCodec-compatible enhancement and choose either a strict-1.5 benchmark
paper path or a codec-family reset.
```

Result:

```text
fail / no-promote
```

Manual verdict columns:

```text
case_id
UB0p10_vs_E1p5
UB0p25_vs_E1p5
UB0p50_vs_E1p5
minimum_winning_extra_kbps
UB0p50_vs_E3
improvement_type
background_damage
promotion_note
```

## Interpretation Rules

Do not claim A140.1 proves a usable side-channel before listening.

Do not compare against old A1347 WAVs. The pack contains same-current-path
anchors and references.

Since A140.1 failed, EnCodec K2 at 1.5 kbps should be treated as saturated for
this project's current EnCodec-compatible mechanisms.
