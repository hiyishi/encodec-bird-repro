# PS-CX A140 Decision Freeze After EnCodec No-Go

Generated: 2026-06-29

## Frozen Evidence

```text
A137 post-hoc frozen RVQ allocation: no-promote
B1 decoder-only fine-tune: stopped
A138.1 neutral FT: pass
A138.2v0 bird-event weighted loss: objective-positive / listening-tie / no-promote
A138.2v1 lambda sweep: not unblocked
A138.3 stronger overfit FT: audible effect present / mixed tradeoff / no positive specialization
A139.0 same-rate hybrid replacement: no-go
A139.1 detail token design: not unblocked
```

The current EnCodec conclusion is:

```text
post-hoc RVQ allocation: no
training-time small FT / event loss: no audible specialization
same-rate replacement of generic layer with bird detail: no
```

A139.0 is the hardest negative result:

```text
E0.75 carrier + oracle event residual detail <= E1.5 K2
```

That means EnCodec K2 at 1.5 kbps is a very strong budget allocation. The second RVQ layer is not simply disposable generic texture; it appears to preserve naturalness, continuity, and texture stability in ways that an event residual upper bound did not replace.

## Strategic Question

```text
Should the project keep the target strictly at 1.5 kbps,
or move to a slightly larger budget / different codec family / benchmark paper?
```

## Option 1: Conservative Route

```text
Treat EnCodec 1.5 as the current best strict-1.5 kbps baseline.
Turn the project into a bird low-rate codec failure benchmark plus negative oracle study.
```

Pros:

- Strong evidence chain.
- Good external review value.
- Avoids further engineering churn around a saturated baseline.

Cons:

- Less of a new codec contribution.
- Main claim becomes diagnostic rather than constructive.

## Option 2: Practical Route

```text
Relax exact 1.500 kbps.
Test E1.5 + tiny bird-detail side-channel.
```

Generated next experiment:

```text
A140.1 marginal side-channel value oracle:
  E1.5 + 0.10 kbps bird-detail oracle
  E1.5 + 0.25 kbps bird-detail oracle
  E1.5 + 0.50 kbps bird-detail oracle

Goal:
  find the smallest extra bitrate that clearly and stably beats E1.5 on hard cases.

Status:
  listening-tie / no-promote
```

This asks a different question from A139:

```text
A139 asked:
  Can we replace EnCodec's second generic RVQ layer?

A140.1 would ask:
  Given EnCodec K2 is strong, how many extra source-derived bird bits are needed
  to reliably improve hard cases?
```

Pros:

- More practical for transmission: low bitrate remains the main constraint, but not necessarily exactly 1.500 kbps.
- Directly measures marginal value per added bit.
- Can produce a defensible engineering tradeoff curve.

Cons:

- No longer strict same-rate.
- Must be careful not to drift into post-filter or hallucination; extra bits must be encoder-derived and counted.

## Option 3: Aggressive Route

```text
Switch codec family:
  DAC low-rate
  neural codec smoke
  bird-only codec
```

Pros:

- Real chance for a new codec mechanism.

Cons:

- Much larger engineering project.
- No guarantee it beats EnCodec 1.5.
- Requires new data scale, training recipe, and listening discipline.

## Recommendation

Do not run more EnCodec small-change experiments under A137/A138/A139.

Recommended next move:

```text
A140.1 marginal side-channel value oracle
```

Rationale:

```text
A139 proved same-rate replacement of K2 is not enough.
It did not prove that tiny additional encoder-derived side bits are worthless.
```

A140.1 should stay an oracle first. It should not train a model or design a production bitstream until it answers:

```text
How much extra bitrate above E1.5 is needed before hard-case bird detail audibly improves?
```

Current artifact:

```text
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/
```

The A140.1 side-channel routes are illegal exact-source-residual upper bounds,
not candidate bitstreams. Manual listening on 2026-06-30 found no clear audible
difference between same-pack `E1p5_K2_fixed` and `E1.5 + 0.10 / 0.25 / 0.50 kbps`
exact-detail UBs.

Because even `E1.5 + 0.50 kbps` oracle does not clearly beat E1.5, EnCodec-compatible small-change enhancement should close and the project should choose between the conservative benchmark paper and an aggressive codec-family reset.
