# PS-CX A139.0 Same-Rate Hybrid Budget Oracle

Generated: 2026-06-29

## Decision State

```text
A137 post-hoc RVQ allocation: closed
B1 decoder-only FT: closed
A138.1 neutral FT: pass
A138.2v0 bird-event weighted loss: objective-positive / listening-tie / no-promote
A138.2v1 lambda sweep: not unblocked
A138.3 audible effect calibration: audible effect present / mixed tradeoff / no positive specialization
A139.0 same-rate hybrid budget oracle: UB beats E0.75 variants but loses E1.5 / no-go
A139.1 detail token design: not unblocked
next: A140 decision freeze
```

A139 changes the question from:

```text
Can we make EnCodec 1.5 kbps decode more detail from its existing bits?
```

to:

```text
At the same 1.5 kbps transmission budget, should part of EnCodec's generic RVQ budget
be replaced by bird-event detail bits?
```

## Core Hypothesis

EnCodec is a strong carrier, but its low-rate generic RVQ layers may not be the best use of bits for sparse bird vocalization detail. A139 tests:

```text
baseline:
  EnCodec K=2 ~= 1.5 kbps

candidate family:
  EnCodec K=1 ~= 0.75 kbps
  + bird-event detail budget ~= 0.75 kbps
  total ~= 1.5 kbps
```

This avoids decoder hallucination because future detail bits would be encoder-side measurements from the source audio and counted in the bitrate ledger.

## Artifact

```text
runs/diagnostics/a1390_same_rate_hybrid_budget_oracle_20260629/
```

Routes per heldout failure case:

```text
R0_original
E0p75_K1_fixed
E1p5_K2_fixed
E3_K4_fixed
E0p75_plus_exact_event_residual_UB
E0p75_plus_event_hf_envelope_proto
```

Important implementation boundary:

```text
Official EnCodec 24 kHz API does not expose 0.75 kbps.
A139.0 uses manual K=1 quantizer prefix decode.
```

## Machine Checks

```text
eval cases: 6
mean event ratio: 0.20
detail budget: 0.75 kbps
prototype actual detail kbps mean: 0.5898
prototype under 0.75 detail budget for all cases: true
mean upper-bound delta event error vs E1.5: -1.0297
```

The exact event residual upper bound is intentionally illegal as a candidate:

```text
It injects source residual in event windows.
It only asks whether bird-detail bits could matter at the same budget.
```

Important rate interpretation:

```text
E0p75_plus_exact_event_residual_UB is not a 0.75 kbps route.
It is E0.75 carrier + 0.75 detail budget = 1.5 kbps total.
```

## Listening Verdict

Manual verdict on 2026-06-29:

```text
UB clearly beats the 0.75 kbps carrier variants.
UB still slightly loses to E1p5_K2_fixed.
Therefore A139.0 fails the primary same-rate gate.
```

Conclusion:

```text
A139.0 no-go.
Same-rate replacement of EnCodec's second generic RVQ layer with this form of
event-detail upper bound does not beat the original E1.5 budget allocation.
Do not continue prototype compression under A139.
A139.1 detail token design is not unblocked.
```

Interpretation:

```text
E0.75 carrier + oracle event residual detail <= E1.5 K2
```

This means EnCodec's second RVQ layer is not a freely replaceable generic bit bucket. Even though it is not an explicit bird-detail token, it contributes to naturalness, continuity, and texture stability enough that replacing it with source-derived event residual does not improve the same-rate result.

Do not continue:

```text
more complex event residual
more complex envelope prototype
compressed residual token
E0.75 + side detail as A139.1 same-rate replacement
```

The envelope prototype is legal-ish but deliberately weak:

```text
E0.75 carrier
+ event highband gain envelope
+ event mask header
<= 0.75 kbps detail budget for every case
```

## Gate

Primary go/no-go question:

```text
Does E0p75_plus_exact_event_residual_UB clearly beat E1p5_K2_fixed?
```

This answers:

```text
If the second generic EnCodec RVQ layer budget were replaced by true
source-derived bird-event detail, is there theoretical listening space?
```

The envelope prototype is a secondary observation. It does not decide whether A139 closes.

Strong pass:

```text
UB clearly beats E1.5,
and is close to or better than E3,
and the improvement is bird event clarity / ridge / onset / non-metallic texture.
```

Weak pass:

```text
UB beats E1.5,
but remains clearly worse than E3.

This means same-rate bird-detail replacement has space,
but detail token compression will be hard.
```

Fail:

```text
UB does not beat E1.5.

This closes A139 same-rate hybrid detail replacement.
Do not continue prototype compression.
```

Verdict table fields:

```text
case_id
UB_vs_E1p5: win / tie / lose
UB_vs_E3: better / close / worse
proto_vs_E1p5: win / tie / lose
E0p75_carrier_damage: mild / severe
improvement_type: clarity / ridge / onset / brightness / noise / none
background_damage
promotion_note
```

Review files:

```text
review_bundle/listening_manifest.csv
review_bundle/a1390_manual_verdict_template.csv
rate_ledger.csv
metrics.csv
event_mask_summary.csv
summary.json
```
