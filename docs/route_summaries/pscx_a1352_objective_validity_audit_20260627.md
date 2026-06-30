# A135.2 Objective Validity Audit

## Decision

`a1352_objective_validity_audit_ready`

## Purpose

A135.2 tests whether the A135 proxy objectives are valid enough to keep using as losses.
It does not train a model. It checks whether objective metrics rank known listening ceilings
above EnCodec failure routes.

## Pairwise Validity

```text
l1_to_original: ceiling passes 3/3
logmag_l1_to_original: ceiling passes 3/3
onset_envelope_loss: ceiling passes 3/3
event_highband_loss: ceiling passes 3/3
event_centroid_loss: ceiling passes 3/3
```

## Verdict

```text
A135.2:
  metric rows: 135
  pairwise rows: 25
  ceiling validity pass metrics: 5/5
  decision: a1352_objective_validity_audit_ready
```

## Interpretation

```text
The proxy metrics are not useless:
  DAC8 beats EnCodec6 on 15/15 cases for all tested metrics.
  Opus32/64 beat EnCodec6 on 15/15 cases for all tested metrics.

But A135.1 still has no listening promotion:
  the current tiny adapter + proxy loss setup does not turn metric separability
  into a meaningful clarity/detail improvement.
```

So the next move should not be scaling A135.1. The evidence points toward a
codec-family / latent / decoder-prior problem, or toward needing a stronger
bird-only codec candidate rather than another small EnCodec adapter loss tweak.
