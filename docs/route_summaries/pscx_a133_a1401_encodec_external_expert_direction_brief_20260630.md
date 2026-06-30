# PS-CX A133-A140.1 EnCodec Route External Expert Direction Brief

Date: 2026-06-30  
Project: low-bitrate bird vocalization codec / bioacoustic neural codec feasibility  
Audience: external experts in audio codecs, neural audio compression, RVQ codecs, perceptual audio, bioacoustics, and signal processing  
Purpose: summarize everything we have learned since introducing EnCodec, and ask for help choosing the next research direction.

## 0. One-Page Summary

We are trying to build a legal low-bitrate codec for short bird vocalization clips. EnCodec entered the project after the earlier PS-CX body/carrier route was largely ruled out. It became a very strong generic neural codec baseline, especially at `1.5` and `3.0` kbps.

Since then, we have tested four increasingly direct ways to improve around EnCodec:

```text
A134-A136:
  decoder adapters / decoder fine-tune / package-conditioned probes

A137:
  frozen EnCodec RVQ layer reallocation at event frames

A138:
  training-time EnCodec specialization with neutral FT and bird-event loss

A139-A140.1:
  replace or augment EnCodec bits with source-derived bird-detail upper bounds
```

The current status is:

```text
EnCodec 1.5 kbps:
  surprisingly strong baseline

EnCodec rate ladder on hard cases:
  often non-separating by listening

DAC8 / Opus high-rate:
  clearly better ceiling on the selected failure cases

EnCodec-compatible small-change routes:
  no-promote

Strict or near-1.5 kbps EnCodec enhancement:
  appears saturated for our current mechanisms
```

The most important recent result is A140.1:

```text
E1.5 + 0.10 kbps exact-detail UB:
  no clear audible difference from E1.5

E1.5 + 0.25 kbps exact-detail UB:
  no clear audible difference from E1.5

E1.5 + 0.50 kbps exact-detail UB:
  no clear audible difference from E1.5
```

These upper bounds were not legal candidate bitstreams, because they injected exact source residual on selected event frames. They were intentionally generous. Their listening-tie result suggests that adding small local waveform detail around the current EnCodec output is not enough to produce obvious perceptual improvement on these hard cases.

Current question for external review:

```text
Are we done with EnCodec-compatible specialization, and should we now:

1. turn this into a benchmark / negative oracle study,
2. start a real codec-family reset such as DAC low-rate or bird-only codec,
3. or try a fundamentally different EnCodec training mechanism that our tests did not cover?
```

## 1. What We Need From The Expert

We are not looking for reassurance. We need a technically critical direction call.

Please help answer:

1. Does the evidence justify closing EnCodec-compatible small-change routes?
2. Are there flaws in our A137-A140 oracle designs that could hide a real EnCodec improvement path?
3. Is A140.1 too weak because exact waveform residual is the wrong detail representation, or is the tie itself strong evidence of saturation?
4. Is there still a worthwhile EnCodec route that requires full retraining, learned variable-depth quantization, or domain-specific encoder/quantizer training?
5. Should we switch to DAC-family low-rate experiments before building a bird-only codec?
6. Is a "neural codec failure benchmark for sparse bioacoustic signals" a publishable direction given the negative oracle chain?
7. What is the smallest next experiment that could change the decision?

## 2. Codec Boundary And Legal Runtime

The project has a strict codec boundary:

```text
Encoder:
  may read the original/source audio
  may compute package codes, masks, residuals, event metadata, or training targets

Package:
  every transmitted bit must be counted in the rate ledger
  route id, model id, and hashes must be reproducible

Decoder runtime:
  may read only the package plus fixed model artifacts
  must not read source/original wav
  must not read uncounted teacher features or side files
```

This legal boundary is not the current blocker. The post-A133 experiments repeatedly generated review bundles, rate ledgers, package manifests, and forbidden-source audits. The blocker is perceptual quality and representation.

## 3. Condensed Timeline Since EnCodec Entered

### A133: EnCodec Becomes The Neural Body Baseline

The earlier PS-CX body2 route failed as the main carrier. Dense exact residual could rescue body2, but only as a bitrate-infeasible diagnostic. The project therefore shifted to neural codec bodies.

A133.1 found:

```text
EnCodec3:
  beats retired body2/R34/R35/L3 routes

EnCodec6:
  near DAC8 on a broad ladder

EnCodec 1.5/3:
  strong enough that PS-CX body repair was no longer the main path
```

A133.5 tested a PS-CX-style D3 ridge/envelope side-channel over an EnCodec body:

```text
D3 signal:
  case-specific and sometimes upper-bound positive

compressed / ultralow subjective gain:
  not stable enough

promotion:
  no
```

Interpretation:

```text
PS-CX diagnostic structure still has value,
but direct PS-CX audio side-channel promotion is not supported.
```

### A134: EnCodec Baseline Saturation And Failure Cases

A134.3b tested EnCodec package decoder adapters:

```text
legal/package/control:
  pass

wrong-package / wrong-recording controls:
  pass

generic EnCodec 1.5 kbps:
  unexpectedly strong on many cases

adapter vs generic:
  subjective margin too thin

promotion:
  no
```

A134.6 mined failure cases:

```text
dominant failure:
  detail / clarity / brightness loss

EnCodec rate ladder:
  non-separating on failure cases

E3/E6:
  do not reliably rescue E1.5 failures

decoder adapter:
  no rescue
```

A134.7 compared codec-family ceilings:

```text
DAC8 / classic high-rate ceiling:
  exists

EnCodec6:
  still rough / metallic on failure cases

interpretation:
  not proven to be unavoidable bitrate loss
  possible generic codec objective or model-family mismatch
```

This is the point where EnCodec became both a strong baseline and the main obstacle.

### A135: Bird-Aware Objective Metrics Are Valid But Not Enough

A135.1 tried a bird-aware proxy-loss adapter:

```text
objective signal:
  weak positive

manual listening:
  no meaningful improvement

promotion:
  no
```

A135.2 audited objective metrics:

```text
tested metrics:
  l1_to_original
  logmag_l1_to_original
  onset_envelope_loss
  event_highband_loss
  event_centroid_loss

ceiling validity:
  5/5 metrics pass

DAC8 beats EnCodec6:
  15/15 for all tested metrics

Opus32/64 beat EnCodec6:
  15/15 for all tested metrics
```

Interpretation:

```text
The metrics can see the ceiling gap.
But small EnCodec adapters and proxy losses do not convert that gap into
perceptual improvement.
```

### A136: Codec-Family / Latent Replacement Question

A136 opened three questions:

```text
Q1: Has EnCodec already discarded the bird detail in its package codes?
Q2: Can another neural codec family or bird-only latent approach DAC8/Opus?
Q3: Are our metrics useful as losses, or only diagnostics?
```

A136.1 confirmed the family ceiling:

```text
DAC8 and Opus ceilings beat EnCodec6 on ceiling-valid metrics.
EnCodec rate ladder remains listening-nonseparating on failure cases.
```

A136.2 P1, a code-conditioned decoder probe, failed even as a train-overfit probe:

```text
latent sufficiency:
  unresolved

reason:
  P1 was not strong enough to be a valid latent oracle
```

A136.2b/A136.2c B1, an actual EnCodec decoder fine-tune, showed package-specific objective signal but failed listening:

```text
correct package beats wrong-package by objective controls:
  yes

B1 correct vs same-rate EnCodec by listening:
  fail

observed:
  B1 correct is clearly worse than same-rate EnCodec

interpretation:
  fine-tuning damaged the generic EnCodec decoder prior

promotion:
  no
```

Important boundary:

```text
B1 does not prove EnCodec latents are sufficient.
B1 also does not prove EnCodec latents are insufficient.
It proves that this decoder-fine-tune route is not a quality route.
```

### A137: EnCodec Paper/Code Audit And Frozen RVQ Reallocation

A137.0 audited EnCodec:

```text
24 kHz model:
  75 latent steps/sec

per RVQ layer:
  0.75 kbps

rate ladder:
  1.5 kbps = 2 codebooks
  3.0 kbps = 4 codebooks
  6.0 kbps = 8 codebooks

architecture:
  convolution/LSTM encoder
  residual vector quantizer
  convolution/LSTM decoder
```

A137.0b reviewed VRVQ:

```text
relevance:
  fixed number of RVQ codebooks per frame may be suboptimal
  variable-depth RVQ is a published and relevant mechanism

post-verdict relevance:
  useful literature support
  not a reason to keep tuning frozen EnCodec masks after A137.2v0 failed
```

A137.2v0 implemented a frozen EnCodec event-masked RVQ oracle:

```text
implementation:
  prefix-monotone per-layer latent masking
  frozen EnCodec decoder
  event4 / event8 routes
  matched random/background/wrong-mask controls

audit:
  fixed K=2/K=4 latent summation matches EnCodec decode
  event routes are not no-ops
  waveform deltas concentrate in event windows
```

Manual listening:

```text
event4 / event8:
  no clear improvement over fixed EnCodec anchors

promotion:
  no
```

Interpretation:

```text
Existing frozen EnCodec high-rate RVQ layers are not locally reusable enough
to improve bird-event quality by inference-time depth allocation.
```

This closed:

```text
post-hoc RVQ allocation
fixed EnCodec masked-latent route
continued event-mask/event8 tuning
```

### A138: Training-Time EnCodec Specialization

A138 asked:

```text
Can EnCodec be specialized during training so that bird-event
ridge/onset/highband information is preserved in the low-rate latent?
```

A138.1 first checked infrastructure and non-destructive training:

```text
A138.1a current anchors rebuild:
  pass

A138.1b AudioCraft/Dora scaffold:
  abandoned after one unblock attempt

A138.1b-alt minimal current-EnCodec training loop:
  pass

A138.1c neutral fine-tune sanity:
  pass
```

Neutral FT did not audibly damage EnCodec, so A138.2 was allowed.

A138.2v0 changed only the loss:

```text
same minimal loop
same 8 train clips
same 6 heldout failure cases
same steps / LR / train scope
same rates: 1.5 and 3.0 kbps

only change:
  base reconstruction loss
  + 0.25 * event_loss
  + 0.10 * onset_loss
```

Listening result:

```text
official current anchors, neutral minimal FT, and eventloss FT:
  no clear audible difference

A138.2v0:
  objective-positive / listening-tie / no-promote
```

A138.3 increased training strength to calibrate whether the loop can change output:

```text
stronger overfit FT:
  audible effect exists

manual verdict:
  official EnCodec and overfit FT sound like tradeoffs
  no clear positive specialization
```

Interpretation:

```text
The training loop is not inert.
But small-data EnCodec FT and conservative bird-event loss do not produce a
stable perceptual improvement.
```

### A139: Same-Rate Hybrid Replacement

A139 changed the question:

```text
Instead of trying to extract more detail from E1.5,
can we replace EnCodec's second generic RVQ layer with bird-detail bits?
```

Routes:

```text
baseline:
  EnCodec K=2 ~= 1.5 kbps

candidate upper bound:
  EnCodec K=1 ~= 0.75 kbps
  + exact event residual budget ~= 0.75 kbps
  total ~= 1.5 kbps
```

Manual verdict:

```text
E0.75 + exact event residual UB:
  clearly beats the 0.75 kbps carrier variants
  still slightly loses to E1p5_K2_fixed

promotion:
  no
```

Interpretation:

```text
EnCodec's second RVQ layer is not a freely replaceable generic bit bucket.
It appears to preserve naturalness, continuity, and texture stability in ways
that the tested event residual upper bound did not replace.
```

This closed:

```text
same-rate hybrid detail replacement
A139.1 detail token design
more complex residual/envelope prototypes under A139
```

### A140.1: Marginal Side-Channel Value Oracle

A140.1 asked one final practical question:

```text
If we keep EnCodec K2 intact,
how many extra source-derived bird-detail bits above E1.5 are needed
before hard-case detail audibly improves?
```

Routes per case:

```text
R0_original
E1p5_K2_fixed
E1p5_plus_detailUB_0p10   total 1.60 kbps
E1p5_plus_detailUB_0p25   total 1.75 kbps
E1p5_plus_detailUB_0p50   total 2.00 kbps
E3_K4_fixed               total 3.00 kbps
```

Machine metrics moved monotonically in event windows:

```text
mean delta event error vs E1.5:
  +0.10 kbps: -0.1603
  +0.25 kbps: -0.4044
  +0.50 kbps: -0.7624
```

But manual listening on 2026-06-30 found:

```text
E1.5 + 0.10 kbps exact-detail UB:
  no clear audible difference from E1.5

E1.5 + 0.25 kbps exact-detail UB:
  no clear audible difference from E1.5

E1.5 + 0.50 kbps exact-detail UB:
  no clear audible difference from E1.5

promotion:
  no
```

Interpretation:

```text
Even a generous exact-source-residual marginal side-channel did not produce
obvious perceptual improvement near the 1.5-2.0 kbps range.
```

This is the strongest saturation signal so far.

## 4. What We Think Is Now Ruled Out

Unless the expert finds a specific flaw, we should not keep spending time on:

- EnCodec decoder-only fine-tuning.
- Small EnCodec adapter scaling.
- More A138.2 lambda sweeps.
- Post-hoc frozen RVQ depth reallocation.
- More event4/event8/event-mask tuning.
- Replacing EnCodec K2 with an event residual detail stream at the same total 1.5 kbps.
- Designing legal A139 detail tokens after the upper bound lost.
- Designing legal A140 tiny side-channel tokens after the upper bound tied.
- Promotion from objective metrics without manual listening.

Repeated failure pattern:

```text
objective-positive or package-specific signal
does not imply perceptual quality improvement.
```

## 5. What Is Not Ruled Out

We should be careful not to overclaim.

Not ruled out:

```text
A full domain-specific neural codec trained from scratch.

DAC-family low-rate variants.

A larger, well-designed EnCodec retraining recipe that changes the encoder,
quantizer behavior, discriminator/loss schedule, and data scale together.

A learned variable-depth RVQ model trained end-to-end, not a frozen mask.

Feature-space or perceptual detail tokens that are not waveform residual.

A benchmark / negative-oracle contribution rather than a new codec.
```

A140.1 does not prove that "extra information can never help." It proves that
the tested exact waveform residual side-channel, at `+0.10` to `+0.50` kbps, did
not create a clear listening improvement over EnCodec 1.5 on our hard cases.

## 6. Current Working Interpretation

The evidence points to this:

```text
EnCodec is not easy to bypass because its low-rate representation and decoder
prior are already highly optimized for natural audio.

For these bird failure cases, small local changes around EnCodec do not cross
a perceptual threshold, even when metrics move.

The missing quality may require a different latent / codec family / training
distribution, not a side patch to the decoded waveform or frozen EnCodec latent.
```

We have two plausible explanations:

### Explanation A: EnCodec 1.5 Is Locally Saturated

EnCodec K2 may already spend its 1.5 kbps in a very efficient way for audible naturalness. Local event detail residuals may not help because the perceptual defect is not a small additive waveform error. It may be a global texture / phase / temporal fine-structure / decoder-prior issue.

Evidence:

```text
A137 frozen RVQ reallocation:
  no audible gain

A139 same-rate replacement:
  UB loses E1.5

A140.1 marginal exact detail:
  no clear difference up to 2.0 kbps total
```

### Explanation B: Our Detail Representation Is Wrong

The exact waveform residual UBs may not be the right form of information. Bird perceptual clarity might require the model to preserve event structure before quantization, rather than injecting local residual after a generic reconstruction.

Evidence:

```text
A135.2 metrics see the ceiling.
DAC8 / Opus ceilings exist.
A140.1 metric deltas are monotone but not perceptual.
```

If this explanation is true, a legal future route must change the representation, not merely add small residual bits.

## 7. Decision Options Now

### Option 1: Benchmark / Negative Oracle Paper

Claim:

```text
Generic neural codecs are strong at low bitrate, but sparse bioacoustic failure
cases expose a gap that common small adaptation strategies do not close.
```

Contribution:

- Failure-case benchmark for bird vocalization compression.
- Clean legal package/replay protocol.
- EnCodec saturation evidence across decoder FT, RVQ reallocation, same-rate replacement, and marginal detail UB.
- Metrics that see codec-family ceilings but do not guarantee promotion.
- Listening-first no-promote discipline.

Risk:

```text
Less of a new codec contribution.
Needs careful framing so negative results are seen as useful science.
```

### Option 2: Codec-Family Reset

Run a new branch:

```text
A141/A142 DAC low-rate and bird-only codec reset
```

Minimal experiment:

```text
baselines:
  EnCodec 1.5 / 3 / 6
  DAC available low-rate variants if possible
  DAC8 / Opus ceilings

candidate:
  small bird-domain neural codec or RVQ autoencoder

rates:
  1.5 and 3.0 kbps first

controls:
  wrong package / same-species wrong / group heldout

gate:
  manual listening beats EnCodec at the same rate on hard cases
  no generic bird hallucination
```

Risk:

```text
Substantially larger engineering effort.
Small custom codec may underperform EnCodec without enough data and training.
```

### Option 3: One Last EnCodec Training Mechanism

Only if an expert believes our A138 tests were too weak, define a real training mechanism rather than another small FT:

```text
full codec retraining or large-domain fine-tune
event-weighted low-rate bottleneck training
learned variable-depth quantizer / q_dropout schedule
bird-event discriminator or perceptual loss
data scale materially larger than 8 clips
current same-path anchors
listening-first gate
```

This should not be a lambda sweep. It must differ mechanism-wise from A138.

Risk:

```text
High effort.
May still preserve generic naturalness at the cost of bird-event detail.
```

## 8. Specific Questions For Expert Review

1. Are A137-A140.1 enough to close EnCodec-compatible small-change routes?
2. Does A140.1's exact waveform residual tie mean "no useful marginal detail," or only "wrong residual representation"?
3. Is post-decoder residual injection a poor oracle for neural codec specialization?
4. What would be a stronger but still minimal latent-sufficiency oracle for EnCodec codes?
5. Should a variable-depth RVQ idea be retried only if trained end-to-end, rather than with frozen EnCodec latents?
6. Would a bird-event-aware quantizer/discriminator plausibly beat EnCodec 1.5/3 at realistic data scale?
7. Is DAC8's better quality mostly rate, architecture family, training data, or objective?
8. Which codec family should be tested first if we reset: DAC low-rate, SoundStream-style, EnCodec retrain, or a small bird-only codec?
9. What listening protocol would convince you that a bird-only codec is not hallucinating generic bird texture?
10. Is the negative-oracle benchmark itself publishable, and what would it need?
11. What is the smallest two-week experiment that could change the path?

## 9. Recommended Listening Subset For The Expert

The expert does not need to listen to every historical pack. Suggested order:

1. A134.7 failure cases:
   compare EnCodec1.5/3/6, DAC8, Opus, original.

2. A136.2c B1:
   hear why package-specific decoder fine-tune was worse than same-rate EnCodec.

3. A137.2v0:
   fixed EnCodec vs event4/event8 masked RVQ routes and controls.

4. A138.2v0 / A138.3:
   official vs neutral FT vs eventloss FT vs stronger overfit tradeoff.

5. A139.0:
   E0.75 carrier, E1.5, E0.75 + exact event residual UB, E3.

6. A140.1:
   E1.5 vs E1.5 + 0.10/0.25/0.50 exact-detail UB, plus E3.

## 10. Key Local Artifacts

Previous broad external brief:

```text
D:\codebase\biofargan\docs\pscx_a117_a1362c_external_expert_review_brief_20260627.md
```

EnCodec route documents:

```text
D:\codebase\biofargan\docs\pscx_a1343b_baseline_saturation_verdict_20260627.md
D:\codebase\biofargan\docs\pscx_a1346_simplified_failure_verdict_20260627.md
D:\codebase\biofargan\docs\pscx_a1347_codec_family_ceiling_verdict_20260627.md
D:\codebase\biofargan\docs\pscx_a1352_objective_validity_audit_20260627.md
D:\codebase\biofargan\docs\pscx_a1360_codec_family_latent_replacement_contract_20260627.md
D:\codebase\biofargan\docs\pscx_a1362c_b1_manual_verdict_20260627.md
D:\codebase\biofargan\docs\pscx_a1370_encodec_paper_code_audit_20260628.md
D:\codebase\biofargan\docs\pscx_a1370b_vrvq_paper_code_relevance_20260628.md
D:\codebase\biofargan\docs\pscx_a1371_2v0_encodec_event_masked_rvq_oracle_20260628.md
D:\codebase\biofargan\docs\pscx_a138_training_time_encodec_specialization_route_contract_20260628.md
D:\codebase\biofargan\docs\pscx_a1381_encodec_training_scaffold_20260628.md
D:\codebase\biofargan\docs\pscx_a1383_encodec_audible_effect_calibration_20260629.md
D:\codebase\biofargan\docs\pscx_a1390_same_rate_hybrid_budget_oracle_20260629.md
D:\codebase\biofargan\docs\pscx_a140_decision_freeze_after_encodec_no_go_20260629.md
D:\codebase\biofargan\docs\pscx_a1401_marginal_side_channel_value_oracle_20260629.md
```

Recent review bundles:

```text
D:\codebase\biofargan\runs\diagnostics\a1371_2v0_encodec_event_masked_rvq_oracle_20260628\review_bundle
D:\codebase\biofargan\runs\diagnostics\a1381b_alt_minimal_encodec_training_loop_20260628\review_bundle
D:\codebase\biofargan\runs\diagnostics\a1382v0_bird_event_weighted_loss_20260629\review_bundle
D:\codebase\biofargan\runs\diagnostics\a1383_encodec_audible_effect_calibration_20260629\review_bundle
D:\codebase\biofargan\runs\diagnostics\a1390_same_rate_hybrid_budget_oracle_20260629\review_bundle
D:\codebase\biofargan\runs\diagnostics\a1401_marginal_side_channel_value_oracle_20260629\review_bundle
```

Recent summaries:

```text
D:\codebase\biofargan\runs\diagnostics\a1371_2v0_encodec_event_masked_rvq_oracle_20260628\summary.json
D:\codebase\biofargan\runs\diagnostics\a1382v0_bird_event_weighted_loss_20260629\summary.json
D:\codebase\biofargan\runs\diagnostics\a1383_encodec_audible_effect_calibration_20260629\summary.json
D:\codebase\biofargan\runs\diagnostics\a1390_same_rate_hybrid_budget_oracle_20260629\summary.json
D:\codebase\biofargan\runs\diagnostics\a1401_marginal_side_channel_value_oracle_20260629\summary.json
D:\codebase\biofargan\runs\diagnostics\a1401_marginal_side_channel_value_oracle_20260629\review_bundle\a1401_manual_verdict.csv
```

## 11. Current Bottom Line

The project is no longer in vague "missing innovation" territory. It has a concrete negative result chain:

```text
EnCodec is strong.
Frozen RVQ reallocation does not improve it.
Small EnCodec fine-tuning does not specialize it perceptually.
Replacing its second RVQ layer with event detail loses.
Adding up to +0.50 kbps exact event detail above E1.5 still ties by listening.
```

Therefore:

```text
Strict or near-1.5 kbps EnCodec-compatible enhancement appears saturated for
the current mechanisms.
```

The expert direction call we need:

```text
Should we write this up as a benchmark / negative oracle study,
or reset to a new codec family / bird-only codec,
or is there one genuinely different EnCodec training mechanism still worth a
bounded test?
```
