# A134.7 Codec-Family Ceiling Verdict

## Decision

`a1347_codec_family_ceiling_verdict_open_a135`

## Verdict

```text
A134.7:
  DAC8 / classic high-rate ceiling exists
  EnCodec rate ladder is non-separating on failure cases
  EnCodec6 still has rough / metallic artifact
  low-bitrate loss exists, but this artifact is not proven unavoidable
  likely issue: generic neural codec objective/model-family mismatch for bird vocal detail
```

## Frozen Interpretation

The project should not continue as "repair EnCodec with a thin adapter". The
research question moves to whether a bird-aware training objective can make a
neural codec spend capacity on ridge, chirp, onset, and clarity instead of
generic audio naturalness alone.

## Next

Open A135: bird-aware neural codec objective reset.
