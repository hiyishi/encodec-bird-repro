# PS-CX A117-A136.2c External Expert Review Brief

Date: 2026-06-27  
Project: low-bitrate bird vocalization codec / neural codec feasibility  
Audience: external audio codec, neural vocoder, bioacoustics, perceptual audio, and signal-processing experts  
Purpose: give an external reviewer enough context to diagnose what is really blocking the project and what experiment should be run next.

## 0. One-Page Summary

We are trying to build a legal low-bitrate codec for short bird vocalization clips. The original PS-CX route attempted to encode a compact body/carrier plus sparse detail or residual information. After A117-A136.2c, the project has a much clearer state:

```text
PS-CX body2 as the main carrier:
  closed / no-go

PS-CX deterministic highband, phase, selector, and patch repair:
  closed / no-promote

PS-CX audio side-channel over a neural body:
  upper-bound signal exists, but deployable benefit is not stable
  paused / no-promote

Generic neural codec body:
  strong baseline
  EnCodec 1.5/3.0 kbps is often surprisingly usable
  DAC8 is the current quality anchor

Current hard problem:
  EnCodec failure cases still have detail / clarity / brightness loss and
  rough or metallic artifacts; EnCodec 1.5/3/6 are often non-separating on
  these failure cases, while DAC8 / Opus high-rate are clearly better.

Most recent result:
  A136.2c actual EnCodec decoder fine-tune B1 is stopped.
  B1 uses the correct package in controls, but manual listening says B1 correct
  is clearly worse than same-rate EnCodec.

Current open question:
  Is the remaining gap caused by EnCodec latent/package information loss, by
  decoder/objective family mismatch, or by the need for a bird-only codec latent?
```

This document supersedes the older A117-A1312 external brief. The key update is that we no longer think the next step is "body2 neural refiner" or "PS-CX side-channel promotion." The main question is now codec-family / latent replacement feasibility.

## 1. What We Need From The Expert

We want a technically critical review, not validation. The most useful feedback would answer:

1. Are we correctly interpreting the failure as a codec-family / latent / decoder-prior issue rather than a bitrate-only issue?
2. Is it worth running a stronger EnCodec-code sufficiency probe, such as token-to-mel/STFT-to-vocoder, after B1 failed perceptually?
3. Should we instead skip further EnCodec latent probing and build a small bird-only RVQ / neural codec smoke?
4. Which listening or objective tests would best separate "low-bitrate unavoidable loss" from "wrong model family or wrong objective" for bird vocalizations?
5. Are ridge, chirp, instantaneous-frequency, onset, and event-local highband metrics likely to be useful as losses, or only as diagnostics?
6. What is the minimal next experiment that would be publishable or decision-quality?

## 2. Project Goal And Legal Runtime Boundary

The target is a low-bitrate audio codec for bird vocalizations. The intended codec boundary is strict:

```text
Encoder side:
  may read source/original audio
  may compute body, detail, residual, metadata, neural-codec package, or model-side training targets

Package:
  every per-case transmitted bit must be counted in the rate ledger
  hashes and route IDs must be reproducible

Decoder runtime:
  may read only the package plus fixed model artifacts
  must not read source/original wav
  must not read teacher spectrograms or residual side files unless encoded in the package
  must report forbidden runtime input count = 0
```

This legal/cleanroom boundary is not the current blocker. A124 and later experiments repeatedly pass forbidden-input audits and clean replay checks. The blocker is quality and representation.

## 3. Current Frozen Status

| Area | Current status | Why |
| --- | --- | --- |
| PS-CX body2 as main carrier | closed | Only dense 0-10 kHz or full exact residual rescues it; sparse residual does not. |
| body2 highband / phase repair | closed | Original highband over body2 and original phase over body2 magnitude do not rescue listening. |
| selector expansion | closed as primary route | A1296 listening failed; A1297 showed selector material rescue rate only 1/31. |
| localized residual object over body2 | diagnostic only | Exact/dense residual can rescue, but bitrate is infeasible for low-rate codec. |
| EnCodec 3 kbps body | strong near-3 kbps baseline | A133.1 listening: EnCodec3 beats retired body2/R34/R35/L3 routes. |
| EnCodec 1.5 kbps body | strong baseline on many cases | A134.3b found baseline saturation; many clips already sound good. |
| EnCodec failure cases | unresolved | Main failure is detail/clarity/brightness loss and rough/metallic texture. E1.5/E3/E6 often do not separate on these cases. |
| DAC8 | quality anchor | A132.3/A134.7: clearly better on failure cases, often close to high-rate ceiling. |
| PS-CX D3 ridge/envelope side-channel | paused / no-promote | Case-specific and upper-bound positive, but compressed/ultralow subjective gain is not stable or obvious. |
| EnCodec decoder adapter / fine-tune B1 | stopped / no-promote | A136.2c manual listening: correct B1 is clearly worse than same-rate EnCodec. |
| Bird-aware proxy loss adapter | stopped / no-promote | A135.1 objective weak positive but no meaningful listening improvement. |
| Objective metrics | useful as diagnostics | A135.2: metrics separate DAC8/Opus ceilings from EnCodec6, but current model mechanisms cannot exploit them. |
| Latent sufficiency | unresolved | P1 probe failed as a probe; B1 failed perceptually; no valid conclusion yet that EnCodec codes have or lack enough detail. |

## 4. Important Definitions

```text
PS-CX:
  project shorthand for the earlier body/detail/residual codec route.

body2:
  upgraded PS-CX body/carrier representation. It became the main body baseline
  during A127-A132, then was retired as main carrier in A133.0.

R34 / R35:
  deterministic body2 repair routes. R34 is guarded body floor/highband repair.
  R35 is guarded local carrier/highband repair.

L3:
  A132.0 tiny neural waveform carrier refiner over body2.

EnCodec:
  generic neural audio codec baseline. We use official 24 kHz rate points such
  as 1.5, 3.0, and 6.0 kbps.

DAC8:
  DAC-family neural codec baseline at about 8 kbps. Current quality anchor.

Opus32 / Opus64:
  high-rate classical codec ceiling references.

D3:
  PS-CX ridge/envelope side-channel candidate over a neural codec body.

B1:
  A136.2b actual EnCodec decoder fine-tune / adaptation probe. Input is EnCodec
  package codes; runtime does not use generic decoded wav.
```

## 5. Condensed Evidence Chain

### 5.1 A117-A1312: PS-CX Engineering Closure, But Body/Carrier Failure

The earlier A117-A1312 phase proved that the project can build legal packages and cleanroom replay, but it also exposed a consistent listening failure.

Positive results:

- A120: an 8 kbps guarded stack repaired targeted small-set failures under a fixed/oracle artifact route.
- A122: a near-3 kbps small-set allocation-anchor route looked plausible on a frozen review set.
- A124: 128-case legal source-to-package-to-cleanroom-decoder pipeline passed exact replay and leakage checks.
- A126: localized residual objects showed real case-specific signal on enabled cases.
- A1312: a frozen learned decoder smoke was rendered legally with forbidden runtime input count 0.

Negative results:

- A121 compact residual metrics did not transfer to real render.
- A123 showed the A122 route was a small-set frozen artifact route, not a scalable reproducible pipeline.
- A125 showed most detail behaved like generic texture, not case-specific bird detail.
- A1296 sparse selector listening failed.
- A1297 showed body2 decoded floor was already poor.
- A1298/A1300 highband/local carrier repairs improved metrics but not natural listening.
- A1312 learned smoke was metric-positive but not a listening pass.

The A117-A1312 conclusion:

```text
The project was not blocked by cleanroom legality, rate ledger, or selector plumbing.
It was blocked by the decoded body/carrier floor.
```

### 5.2 A132: Failure Localization Ladder

A132 stopped route engineering and asked where the first rescue exists.

A132.0 trained a tiny waveform neural carrier refiner over body2:

```text
heldout L3 median delta vs body2: +0.008741
wrong-body specificity margin: +0.307394
forbidden runtime input count: 0
```

Interpretation:

```text
The learned refiner was legal and condition-specific, but it did not create a
usable quality jump. It was a diagnostic smoke, not a quality win.
```

A132.2 oracle ladder listening:

```text
O2 body2 + exact waveform residual:
  pass

O5 DAC8 + exact waveform residual:
  pass

O6 original low/mid + L3 highband:
  partial

O1 body2:
  fail

O3 original highband over body2:
  fail

O4 original phase over body2 magnitude:
  fail
```

Interpretation:

```text
Highband-only and phase-only repairs do not rescue the sound.
The audible failure is in the main low/mid carrier, ridge continuity, temporal
fine structure, and residual spectral content.
```

A132.3 residual sufficiency:

```text
body2 sparse 5/10 residual rescue:
  no

body2 dense low/mid or full exact residual rescue:
  yes, but bitrate-infeasible

DAC8 base:
  sufficient

DAC8 sparse residual variants:
  sufficient
```

This formally triggered the route shift:

```text
body2 cannot be the main carrier.
neural codec body becomes the primary carrier candidate.
PS-CX survives only as optional residual / semantic / diagnostic structure.
```

### 5.3 A133: Neural Body Reset And PS-CX Side-Channel Audit

A133.0 froze:

```text
body2 main carrier:
  no-go

body2 dense residual rescue:
  diagnostic only, bitrate-infeasible

DAC8 neural body base:
  pass

PS-CX residual / semantic layer:
  optional enhancement only
```

A133.1 neural body rate ladder:

```text
EnCodec6 near DAC8:
  true on the broad listening ladder

EnCodec3 beats retired body2 routes:
  true

EnCodec3 tier:
  near-natural candidate
```

A133.2 optional side-channel proxy:

```text
PS-CX-like side-channel proxy beats EnCodec3 base:
  true

proxy beats EnCodec6 base:
  true

proxy near/below DAC8:
  true

raw/proxy bitrate feasible:
  false
```

This briefly reopened PS-CX as a neural-body side-channel, but A133.5 closed promotion:

```text
E1.5 + compact D3 side-channel:
  no-promote

correct D3 perceptual benefit:
  not stable / not obvious enough

PS-CX audio side-channel:
  paused

PS-CX diagnostic assets:
  keep
```

Interpretation:

```text
D3 ridge/envelope information is not meaningless. It can be case-specific and
upper-bound positive. But it is not yet a stable deployable codec contribution.
The stronger use of PS-CX is now diagnostic structure, metrics, and possibly
loss design, not direct audio side bits.
```

### 5.4 A134: Bird-Specialized Neural Codec Reset

A134 shifted from "repair PS-CX" to "understand and improve neural codec behavior on bird calls."

A134.2 proved an A134 candidate can emit packages, decoded wavs, model hash, bitrate accounting, and forbidden-runtime-input audits. It made no contribution claim.

A134.3a/A134.3b tested EnCodec package decoder adapters:

```text
legal/package/control:
  pass

wrong-package / wrong-recording controls:
  pass

generic EnCodec 1.5 kbps:
  unexpectedly strong on many cases

adapter vs generic:
  subjective margin too thin

10k training:
  hold
```

A134.6 simplified failure verdict:

```text
dominant failure:
  detail / clarity / brightness loss

EnCodec rate ladder:
  non-separating on failure cases

E3/E6 do not reliably rescue E1.5 failures:
  true

decoder adapter:
  no rescue
```

A134.7 codec-family ceiling verdict:

```text
DAC8 / classic high-rate ceiling exists

EnCodec rate ladder is non-separating on failure cases

EnCodec6 still has rough / metallic artifact

low-bitrate loss exists, but this artifact is not proven unavoidable

likely issue:
  generic neural codec objective/model-family mismatch for bird vocal detail
```

Important nuance:

```text
On many ordinary cases, EnCodec 1.5/3.0 sounds surprisingly good.
On the selected failure cases, EnCodec 1.5/3.0/6.0 often sound similarly flawed,
while DAC8 and high-rate Opus provide a clear better ceiling.
```

This is why we are not interpreting the problem as simple "not enough bits."

### 5.5 A135: Bird-Aware Loss Objective Reset

A135 tried to turn PS-CX diagnostic structure into training objectives.

A135.1 loss-only adapter smoke:

```text
infrastructure / contract smoke:
  pass

forbidden runtime input:
  0

bird-aware proxy objective signal:
  weak positive

manual listening:
  no meaningful improvement

codec or quality promotion:
  no

scaled loss ablation:
  blocked
```

A135.2 objective validity audit:

```text
ceiling validity pass metrics:
  5/5

DAC8 beats EnCodec6:
  15/15 for all tested metrics

Opus32/64 beat EnCodec6:
  15/15 for all tested metrics
```

Interpretation:

```text
The proxy metrics are not useless. They can see the DAC8/Opus ceiling.
But the current small adapter + proxy-loss route cannot convert those metrics
into a meaningful listening improvement.
```

Therefore, the bottleneck moved from "what should we measure" to:

```text
codec family / quantized latent / decoder prior / model mechanism
```

### 5.6 A136: Codec-Family / Latent Replacement Feasibility

A136.0 opened three questions:

```text
Q1: Has EnCodec package already discarded bird-call detail?
Q2: Can a different codec family or bird-only latent approach DAC8/Opus ceiling?
Q3: Are ceiling-valid metrics useful as losses, or only as diagnostics?
```

A136.1 confirmed the family ceiling picture:

```text
DAC8 beats EnCodec6 on all tested ceiling-valid metrics.
Opus32/64 beat EnCodec6 on all tested ceiling-valid metrics.
EnCodec rate ladder is file/token-valid but listening-nonseparating on failure cases.
```

A136.2 P1 code-conditioned waveform decoder probe:

```text
input:
  EnCodec package codes only

runtime:
  package + fixed decoder model

forbidden runtime input:
  0

train-overfit sanity:
  fail

heldout quality:
  fail

latent sufficiency:
  unresolved
```

P1 failed even on micro-overfit sanity, so it is not a valid proof that EnCodec latents lack bird-call detail.

A136.2b B1 actual EnCodec decoder fine-tune:

Objective metrics initially showed weak package-specific signal:

```text
train-overfit wins generic:
  1.5 kbps: 5/8
  3.0 kbps: 5/8

heldout correct package wins same-rate EnCodec by objective metric:
  1.5 kbps: 11/15
  3.0 kbps: 11/15

correct beats wrong-package:
  15/15 at both rates

wins EnCodec6:
  1.5 kbps: 1/15
  3.0 kbps: 5/15
```

A136.2c manual listening overrode the objective weak-positive:

```text
B1 correct vs same-rate EnCodec:
  fail

Observed:
  B1 correct is clearly worse than same-rate EnCodec.

Interpretation:
  B1 depends on package information in objective controls, but it degrades the
  generic EnCodec decoder prior perceptually.

B1 quality route:
  stop

B1 scale-up / 10k / second seed:
  cancelled

EnCodec decoder fine-tune route:
  no-promote

Latent sufficiency:
  unresolved; B1 does not prove it
```

Current A136 status:

```text
P1:
  invalid/no-pass as latent probe

B1:
  package-specific but perceptually worse than same-rate EnCodec
  stopped

Open:
  B2 token -> mel/STFT -> vocoder probe if cheap
  otherwise A136.3 bird-only latent / RVQ autoencoder smoke
```

## 6. What We Believe Is Ruled Out

These should not be revived unless the expert sees a specific flaw in our logic:

- PS-CX body2 as the main audio carrier.
- More selector coverage as the primary fix.
- More body2 highband or airband patch tuning.
- Phase-only replacement over body2.
- Dense residual compression as a low-rate main route.
- Metric-positive STFT/gain overlays without listening promotion.
- D3 ridge/envelope side-channel as a promoted codec layer in its current form.
- Small EnCodec decoder adapter / post-filter as a quality route.
- Scaling A135.1 proxy-loss adapter.
- Scaling B1 to 10k or more seeds.

The repeated pattern is:

```text
metric positive or specificity positive
does not imply
perceptual quality improvement.
```

Manual listening has repeatedly prevented false promotion.

## 7. What Still Looks Valuable

These assets should probably be preserved:

1. A124 clean legal pipeline:
   exact replay, rate ledger, forbidden-input audit, package discipline.

2. A126 localized residual object:
   proof that case-specific residual information can exist, even if body2 is not viable.

3. PS-CX ridge / IF / chirp / onset diagnostics:
   more likely useful as metrics, labels, losses, or analysis tools than as direct audio side bits.

4. A133-A136 listening and failure-case bundles:
   they define the hard cases where EnCodec rate ladder does not separate.

5. DAC8 / Opus high-rate ceiling references:
   important evidence that the failure is not simply source material or listening setup.

6. Wrong-package / wrong-recording controls:
   crucial for detecting hallucination and generic bird-texture generation.

7. A135.2 metrics:
   they can separate known ceilings from EnCodec failure routes, even if current model mechanisms do not exploit them.

## 8. Current Working Hypotheses

### Hypothesis A: EnCodec Latent Is Partly Insufficient

The EnCodec encoder/quantizer may discard bird-call fine structure that matters for perceived clarity:

```text
ridge continuity
chirp / IF slope
onset shape
event-local highband brightness
temporal fine structure
non-metallic texture
```

Evidence for:

- EnCodec 1.5/3/6 are non-separating on selected failure cases.
- DAC8 and Opus high-rate are clearly better.
- B1 fine-tune cannot recover perceptual quality from fixed EnCodec package.

Evidence against or unresolved:

- B1 failing does not prove the latent is insufficient.
- P1 failed as a model/probe, not as a latent oracle.
- EnCodec packages might contain recoverable information that our probes did not decode.

### Hypothesis B: EnCodec Latent Is Sufficient, But Decoder/Objective Is Wrong

The codes may contain enough information, but generic decoder priors and training losses may not prioritize bird-call detail.

Evidence for:

- A135.2 metrics can see the ceiling gap.
- B1 objective controls showed correct package beats wrong-package, so there is some package-specific signal.

Evidence against:

- B1 correct sounds worse than generic EnCodec.
- A135.1 proxy losses did not create a meaningful listening gain.
- Simple decoder fine-tune appears to damage a strong generic decoder prior.

### Hypothesis C: Need Bird-Only Codec Family / Latent

The right route may be a small bird-domain RVQ or neural codec trained and evaluated on bird vocalizations, not an EnCodec adapter.

Evidence for:

- Generic EnCodec extra bitrate does not reliably target bird-call clarity on failure cases.
- DAC8 suggests neural codec family choice matters.
- PS-CX diagnostics identify bird-specific structure that generic codecs may not preserve optimally.

Risk:

- Engineering cost is higher.
- A small bird-only RVQ may underperform EnCodec unless architecture/training are strong enough.
- Hallucination controls are mandatory.

## 9. Suggested Next Experiments

### Option 1: A136.2/B2 Token-To-Mel/STFT-To-Vocoder Probe

Purpose:

```text
Test EnCodec code sufficiency with a stronger but still package-conditioned
probe before replacing the latent.
```

Contract:

```text
input:
  EnCodec package codes only

output:
  mel/STFT proxy, then fixed vocoder or reconstruction stage

forbidden:
  generic decoded wav as input
  original/source wav at runtime
  residual side-channel
```

Hard gate:

```text
train-overfit must beat same-rate EnCodec
correct package must beat wrong/same-species-wrong package
heldout must improve listening, not only metrics
```

If B2 also fails:

```text
stop EnCodec latent probing and open A136.3.
```

### Option 2: A136.3 Small Bird-Only RVQ / Neural Codec Smoke

Purpose:

```text
Test whether a bird-domain latent can preserve failure-case detail better than
generic EnCodec at 1.5 and 3.0 kbps.
```

Minimal candidate:

```text
small encoder/decoder + RVQ or quantized latent
rates: 1.5 and 3.0 kbps
loss: MR-STFT + logmel + waveform + ceiling-valid diagnostics
evaluation: failure cases + group-heldout
baselines: EnCodec1.5/3/6, DAC8, Opus32, original
controls: wrong-package / wrong-recording
```

Strong positive:

```text
bird-only 1.5 > EnCodec1.5 on failure cases
bird-only 3.0 > EnCodec3/6 on failure cases
no hallucination
manual listening confirms less rough/metallic texture and better clarity
```

### Option 3: Codec-Family Replacement Baseline

Before building a custom RVQ, test more codec families at comparable rates if available:

```text
DAC low-rate variants
other neural codecs with 1.5/3/6 kbps settings
high-rate Opus/MP3 ceilings for sanity
```

Goal:

```text
Determine whether DAC8 quality is family-specific, rate-specific, or both.
```

## 10. Questions For External Review

1. Is our conclusion "body2 main carrier no-go" justified by the oracle ladder and dense residual evidence?
2. Is EnCodec 1.5/3/6 non-separation on failure cases enough evidence to suspect objective/model-family mismatch?
3. Does DAC8 being much better imply 6-8 kbps is the real first quality range, or could a bird-specific 3 kbps codec plausibly close the gap?
4. Should we run B2 token-to-mel/vocoder before building a bird-only RVQ, or is that too much time spent on EnCodec?
5. How would you design the smallest valid latent sufficiency oracle?
6. What artifact metrics would catch the rough/metallic EnCodec failure without over-rewarding global brightness?
7. Are ridge / IF / chirp / onset losses likely to help if embedded in a stronger codec, or are they too brittle as optimization targets?
8. How should wrong-package controls be structured for a bird codec so we do not reward generic bird hallucination?
9. Is it better to target a domain-specific decoder for an existing neural codec package, or to train a domain-specific latent/codebook?
10. What should the next 2-week experiment be?

## 11. Recommended External Listening Subset

If the expert can listen to audio, we suggest this order:

1. A132.2 oracle ladder:
   hear why exact residual rescues body2 but highband/phase does not.

2. A132.3 residual sufficiency:
   compare body2 dense rescue with DAC8 base.

3. A133.1 rate ladder:
   hear why EnCodec3 became the neural-body baseline.

4. A133.5 ultralow E1.5 + D3:
   hear why PS-CX side-channel promotion was paused.

5. A134.7 / A136 failure cases:
   compare EnCodec1.5/3/6, DAC8, Opus, original.

6. A136.2c B1 manual pack:
   verify B1 correct is worse than same-rate EnCodec despite package specificity.

## 12. Key Local Artifacts

Main previous brief:

- `D:\codebase\biofargan\docs\pscx_a117_a1312_external_expert_direction_brief_20260626.md`

Current route-shift documents:

- `D:\codebase\biofargan\docs\pscx_a1322_root_cause_oracle_verdict_20260626.md`
- `D:\codebase\biofargan\docs\pscx_a1323_residual_sufficiency_verdict_20260626.md`
- `D:\codebase\biofargan\docs\pscx_a1330_neural_codec_body_reset_route_shift_freeze_20260626.md`
- `D:\codebase\biofargan\docs\pscx_a1331_neural_body_rate_ladder_verdict_20260626.md`
- `D:\codebase\biofargan\docs\pscx_a1335_ultralow_body_d3_frontier_verdict_20260627.md`

Current neural-codec / failure-case documents:

- `D:\codebase\biofargan\docs\pscx_a1343b_baseline_saturation_verdict_20260627.md`
- `D:\codebase\biofargan\docs\pscx_a1346_simplified_failure_verdict_20260627.md`
- `D:\codebase\biofargan\docs\pscx_a1347_codec_family_ceiling_verdict_20260627.md`
- `D:\codebase\biofargan\docs\pscx_a1351_bird_aware_loss_ablation_smoke_20260627.md`
- `D:\codebase\biofargan\docs\pscx_a1352_objective_validity_audit_20260627.md`
- `D:\codebase\biofargan\docs\pscx_a1360_codec_family_latent_replacement_contract_20260627.md`
- `D:\codebase\biofargan\docs\pscx_a1361_codec_family_ceiling_smoke_20260627.md`
- `D:\codebase\biofargan\docs\pscx_a1362_code_conditioned_decoder_probe_20260627.md`
- `D:\codebase\biofargan\docs\pscx_a1362b_encodec_decoder_finetune_probe_scaled_20260627.md`
- `D:\codebase\biofargan\docs\pscx_a1362c_b1_manual_verdict_20260627.md`

Listening bundles:

- `D:\codebase\biofargan\runs\diagnostics\a1321_route_shift_manual_listening_pack_20260626\review_bundle`
- `D:\codebase\biofargan\runs\diagnostics\a1323_residual_priority_listening_pack_20260626\review_bundle`
- `D:\codebase\biofargan\runs\diagnostics\a1331_neural_body_rate_ladder_listening_pack_20260626\review_bundle`
- `D:\codebase\biofargan\runs\diagnostics\a1335_ultralow_encodec_body_d3_frontier_listening_pack_20260627\review_bundle`
- `D:\codebase\biofargan\runs\diagnostics\a1362c_b1_listening_validation_pack_20260627\review_bundle`

Most recent manual verdict output:

- `D:\codebase\biofargan\runs\diagnostics\a1362c_b1_manual_verdict_20260627\summary.json`
- `D:\codebase\biofargan\runs\diagnostics\a1362c_b1_manual_verdict_20260627\manual_verdict.csv`

## 13. Bottom Line

The project has not failed because the legal pipeline is impossible. It has not failed because we forgot a selector, a highband shelf, or a small residual object. Those pieces were tested and mostly closed.

The current evidence says:

```text
PS-CX body2 is not a viable main carrier.
Generic neural codec body is the correct baseline.
EnCodec is strong but has bird-call failure cases that extra EnCodec bitrate
does not reliably fix.
DAC8 / Opus ceilings show the target sound is reachable in principle.
Current PS-CX side-channel, adapter, and proxy-loss routes do not close the gap.
The next real question is whether EnCodec package codes are enough, or whether
we need a bird-domain latent / codec family.
```

The decision we need external help with:

```text
Run one more stronger EnCodec-code sufficiency probe (B2),
or stop probing EnCodec and build A136.3 bird-only RVQ / neural codec smoke.
```
