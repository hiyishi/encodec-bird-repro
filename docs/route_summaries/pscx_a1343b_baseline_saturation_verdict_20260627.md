# A134.3b Baseline Saturation Verdict

## Decision

`a1343b_baseline_saturation_hold_10k_open_a1346`

## Verdict

```text
A134.3b:
  legal/package/control: pass
  wrong-package / wrong-recording controls: pass
  generic EnCodec 1.5kbps: unexpectedly strong on many cases
  adapter vs generic: subjective margin too thin
  promotion: no
  10k training: hold
```

## Interpretation

Generic EnCodec 1.5kbps is a real strong baseline for many bird-call clips.
The scaled adapter has objective-positive signs but does not have a large
enough subjective margin to justify promotion or 10k expansion.

## Next

Open A134.6: mine generic EnCodec 1.5 failure cases, label failure types, and
test whether any bird-specialized route rescues those cases specifically.
