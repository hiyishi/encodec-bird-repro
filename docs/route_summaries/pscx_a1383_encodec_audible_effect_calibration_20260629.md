# PS-CX A138.3 EnCodec Audible Effect Calibration

Generated: 2026-06-29

## Decision State

```text
A137 post-hoc RVQ allocation: closed
B1 decoder-only FT: closed
A138.1 neutral FT: pass
A138.2v0 bird-event weighted loss: objective-positive / listening-tie / no-promote
A138.2v1 lambda sweep: not unblocked
A138.3 audible effect calibration: audible effect present / mixed tradeoff / no positive specialization
next: A139.0 same-rate hybrid budget oracle
```

A138.3 is not a candidate route. It asks whether the current minimal EnCodec training loop has enough practical leverage to create a clearly audible decoded-output change.

## Question

```text
Can stronger small-data EnCodec FT produce audible changes on train clips,
and what happens on heldout failure cases?
```

## Artifact

```text
runs/diagnostics/a1383_encodec_audible_effect_calibration_20260629/
```

Run setup:

```text
train clips: 8
heldout failure cases: 6
steps: 80
LR: 1e-4
chunk seconds: 2.5
train scope: encoder_decoder
bandwidths: 1.5 / 3.0
objective: neutral reconstruction, no bird-event loss
```

## Machine Checks

```text
train fixed loss:   0.016532 -> 0.014545
heldout fixed loss: 0.020862 -> 0.020256

mean train official-vs-overfit RMS:   0.020445
mean heldout official-vs-overfit RMS: 0.013863

checkpoint save/load: pass
package replay: pass
rate ledger: pass
forbidden source path audit: pass
review bundle: pass
```

The RMS deltas show the stronger FT is not numerically inert.

Manual listening verdict on 2026-06-29:

```text
Stronger overfit FT does not bring a clear improvement.
Official EnCodec and overfit FT sound like tradeoffs.
Conclusion: audible effect exists, but no positive specialization signal.
```

## Listening Pack

For each train or heldout case:

```text
R0_original
official_encodec_1p5_current
overfit_ft_1p5
official_encodec_3p0_current
overfit_ft_3p0
```

Review files:

```text
review_bundle/listening_manifest.csv
review_bundle/a1383_manual_verdict_template.csv
delta_metrics.csv
summary.json
```

## Interpretation Gate

```text
If train clips are still not audibly changed:
  current training loop perturbation is too weak;
  A138.2v0 tie does not falsify bird loss, only the dose / action point.

If train clips change but heldout is unchanged:
  overfit is possible, but no generalizing specialization signal.

If train clips improve and heldout worsens:
  EnCodec prior is fragile under small-data FT.

If train and heldout both improve:
  a new EnCodec mechanism route may be justified.
```

Do not open A138.2v1 lambda sweep from this result. The next useful question is not how to tune EnCodec FT harder, but whether the 1.5 kbps transmission budget should replace part of generic EnCodec RVQ with bird-detail bits.
