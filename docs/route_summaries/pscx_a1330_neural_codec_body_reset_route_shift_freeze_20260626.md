# A133.0 Neural-Codec-Body Reset Route-Shift Freeze

## Decision

`a1330_neural_codec_body_reset_open_neural_body_primary`

## Frozen Verdict

- body2 main carrier: no-go
- body2 sparse residual rescue: no-go
- body2 dense low/mid residual rescue: pass, but bitrate-infeasible
- DAC8 neural body base: pass
- PS-CX residual / semantic layer: optional enhancement only
- A133: open

## Interpretation

A132.3 closes body2 as the main carrier. The only body2 rescue that works is
dense 0-10k or full waveform residual, which is diagnostic rather than a
deployable low-rate path. DAC8 base passes the listening gate, so A133 starts
from neural codec body as the primary carrier. PS-CX survives as an optional
sparse / semantic side-channel, not as a body repair path.

## A133 Plan

- A133.1 neural body rate ladder: DAC8 quality anchor, EnCodec6 practical
  quality candidate, EnCodec3 semantic / near-3kbps candidate.
- A133.2 PS-CX optional side-channel marginal audit: measure stable subjective
  benefit over neural body with all side bits counted.
- A133.3 final route stratification: freeze 8kbps quality, 6kbps practical,
  and 3kbps semantic/near-natural roles.

## Claim Boundary

Claimed: route shift is formally open and body2 repair routes are retired.

Not claimed: production codec, new neural model, side-channel benefit, or final
bitrate ladder.
