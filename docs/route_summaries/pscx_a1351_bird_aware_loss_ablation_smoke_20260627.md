# A135.1 Bird-Aware Loss Ablation Smoke

## Decision

`a1351_bird_aware_loss_ablation_smoke_ready`

## Scope

- train cases per rate: {'1.5': 256, '3.0': 256}
- eval failure cases: 15
- bandwidths: [1.5, 3.0]
- variants: ['C0_generic', 'C1_onset', 'C4_event_highband', 'C5_combined_proxy']
- candidate rows: 120
- forbidden runtime input total: 0

## Boundary

This is a loss-only adapter smoke, not a codec promotion. It tests whether
stable bird-aware proxy losses beat generic audio loss on A134.7 failure cases.
Exact ridge/IF losses remain contract-only until trackers are frozen.

## Objective Probe Reading

Correct-input median `delta_logmag_vs_same_rate_base`:

```text
1.5kbps:
  C0_generic          -0.0216
  C1_onset            -0.0297
  C4_event_highband   -0.0249
  C5_combined_proxy   -0.0244

3.0kbps:
  C0_generic          -0.0253
  C1_onset            -0.0186
  C4_event_highband   -0.0265
  C5_combined_proxy   -0.0331
```

Bird-aware proxy terms show a weak objective signal over C0:

```text
1.5kbps vs C0:
  C1_onset            median -0.0069, wins 11/15
  C4_event_highband   median -0.0053, wins 11/15
  C5_combined_proxy   median -0.0042, wins 10/15

3.0kbps vs C0:
  C1_onset            median +0.0015, wins 6/15
  C4_event_highband   median -0.0032, wins 10/15
  C5_combined_proxy   median -0.0093, wins 13/15
```

No variant has a median objective win over EnCodec6 on these failure cases.
Wrong-input controls are generally worse by median log-magnitude distance, but
the metric is not clean enough to serve as the hallucination gate by itself.
Listening must remain the promotion gate.

## Verdict

```text
A135.1:
  infrastructure / contract smoke: pass
  forbidden runtime input: 0
  bird-aware proxy objective signal: weak positive
  manual listening: no meaningful improvement
  codec or quality promotion: no
  scaled loss ablation: blocked
```

## Freeze

```text
Do not scale A135.1.
Do not tune C1/C4/C5 weights as a main route.
Do not treat the weak proxy metric as contribution evidence.
Next step: A135.2 objective validity audit.
```
