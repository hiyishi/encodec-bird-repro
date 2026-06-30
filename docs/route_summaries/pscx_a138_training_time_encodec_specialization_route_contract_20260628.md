# PS-CX A138 Training-Time EnCodec Specialization Route Contract

Generated: 2026-06-28

## Status

```text
A137.0  EnCodec audit: pass
A137.0b VRVQ relevance: pass as literature/mechanism support
A137.2v0 masked frozen RVQ oracle: listening fail / no-promote
B1 decoder-only fine-tune: stopped
post-hoc RVQ allocation: closed
next: A138 training-time EnCodec specialization
immediate: A140 decision freeze; choose strict 1.5 kbps benchmark, marginal side-channel oracle, or codec-family reset
```

## Problem Definition

Question:

```text
Can EnCodec be specialized during training so that bird-event ridge/onset/highband
information is preserved in the low-rate latent in the first place?
```

This replaces the A137.2v0 question:

```text
Can we reuse existing frozen EnCodec high-rate RVQ layers locally at inference time?
```

A137.2v0 answered the second question negatively. The next route must therefore change what the codec learns, not only how existing frozen layers are selected.

## Innovation Narrative

Frozen EnCodec is already a strong low-bitrate baseline for bird vocalizations, but its existing RVQ layers cannot be post-hoc reallocated to recover event detail. Therefore, useful specialization must happen during training: the encoder/quantizer must learn to preserve bird-event structure under low-rate constraints.

## Route Contract

A138 is EnCodec-based specialization, not a bird-only codec reset.

Allowed:

- Start from EnCodec / AudioCraft compression model.
- Fine-tune the full codec, or encoder + quantizer + decoder together.
- First prove the training recipe can preserve EnCodec naturalness under a neutral objective.
- Only after neutral fine-tune sanity passes, modify the training objective toward bird-event structure.
- Add rate/depth regularization or RVQ depth dropout only after the base scaffold is reproducible.
- Produce current-decoder listening anchors for official EnCodec `1.5`, `3`, and `6` kbps in the same pack.

Not allowed as promotion routes:

- Decoder-only fine-tune.
- Post-filter enhancement.
- Inference-time masked latent allocation on frozen EnCodec.
- Cross-run listening claims against old A1347 decoded WAVs.
- Metric-only promotion without listening.

## A138.1 Training Infrastructure Smoke

A138.1 is not trying to win. It checks whether training can touch EnCodec without breaking the strong pretrained prior.

Current artifact:

```text
runs/diagnostics/a1381_encodec_training_scaffold_20260628/
```

Current status:

```text
A138.1a current anchors rebuild: pass
A138.1b AudioCraft / EnCodec training scaffold: abandoned_after_one_unblock_attempt
A138.1b-alt minimal EnCodec training loop: pass
A138.1c neutral fine-tune sanity: pass
A138.2v0 bird-event weighted loss differential: objective-positive / listening-tie / no-promote
A138.2v1 lambda sweep: not unblocked
A138.3 audible effect calibration: audible effect present / mixed tradeoff / no positive specialization
A139.0 same-rate hybrid budget oracle: UB beats E0.75 variants but loses E1.5 / no-go
A139.1 detail token design: not unblocked
A140 decision freeze: accepted
A140.1 marginal side-channel value oracle: listening-tie / no-promote
```

The current conda environment can rebuild EnCodec anchors with `encodec`, `torch`, and `torchaudio`. A single AudioCraft/Dora unblock attempt made Dora runnable, but `CompressionSolver` still failed because the cached AudioCraft source lacks `audiocraft.modules`. Per the A138 decision rule, the project stopped repairing AudioCraft/Dora and used a minimal current-`encodec` training loop fallback.

The A138.1 summary schema is fixed around hard gates:

```json
{
  "a1381a_current_anchors_rebuild_pass": true,
  "a1381b_training_scaffold_pass": false,
  "a1381c_neutral_finetune_sanity_pass": true,
  "neutral_ft_audible_degradation": false,
  "audiocraft_import_pass": false,
  "dora_import_pass": false,
  "compression_solver_import_pass": false,
  "audiocraft_encodec_anchor_rebuild_pass": false,
  "audiocraft_vs_official_anchor_parity_pass": false,
  "training_path_anchor_policy": "blocked_until_anchor_policy_resolved",
  "micro_overfit_loss_decrease_pass": false,
  "checkpoint_save_load_pass": false,
  "checkpoint_replay_pass": false,
  "rate_ledger_pass": true,
  "forbidden_source_path_audit_pass": true,
  "a1382_unblocked": true
}
```

Current anchor artifacts must record the official model id/hash, encode path, decode path, `n_q`, bandwidth, sample rate, bitrate ledger, decoded WAV hashes, and manifest hashes. Training scaffold promotion additionally requires checkpoint replay, package reproducibility, forbidden-path hygiene, and an independently auditable review bundle.

### A138.1b-0 Compatibility Bridge

This bridge is mandatory before micro-overfit or neutral fine-tune verdicts.

Goal:

```text
Resolve whether the AudioCraft training path and current official encodec path
produce comparable anchors.
```

Required checks:

- `audiocraft` import pass
- `dora` import pass
- `CompressionSolver` import pass
- Dora compression config resolve pass
- AudioCraft-path EnCodec anchor rebuild pass
- AudioCraft-vs-official-anchor parity pass

Training path anchor policy:

```text
official_encodec_anchors_allowed:
  AudioCraft-path anchors are close enough to current official encodec anchors.

audiocraft_anchors_required:
  AudioCraft-path anchors differ materially; all A138 training candidates must
  be compared only against AudioCraft-path rebuilt anchors.

blocked_until_anchor_policy_resolved:
  Compatibility bridge has not produced a safe anchor policy.
```

If the policy is not resolved, AudioCraft-path training verdicts are blocked even if a micro-overfit loss decreases. For A138.1b-alt, the policy is bypassed by using the same current `encodec` path for anchors and minimal FT candidates.

### A138.1b-alt Minimal Current-EnCodec Training Loop

Current artifact:

```text
runs/diagnostics/a1381b_alt_minimal_encodec_training_loop_20260628/
```

Status:

```text
micro_overfit_loss_decrease_pass: true
checkpoint_save_load_pass: true
checkpoint_replay_pass: true
package_replay_pass: true
rate_ledger_pass: true
forbidden_source_path_audit_pass: true
review_bundle_generated_pass: true
A138.1c listening sanity: pass
A138.2v0: no-promote
A138.2v1: not unblocked
```

Manual verdict on 2026-06-29: neutral FT did not audibly damage EnCodec. This means the training chain is alive and neutral fine-tuning was perceptually safe enough to open A138.2v0.

### A138.1a Current Anchor Rebuild

Goal:

```text
Regenerate current EnCodec E1.5 / E3 / E6 anchors with the same decode path
that will be used for A138 candidates.
```

Reason:

```text
Old A1347 official decoded WAVs may not be bit-identical to the current
A137/A138 decode path. All future EnCodec listening verdicts should use
same-run current anchors.
```

Required output:

- `R0_original`
- `official_EnCodec_1p5_current_decode`
- `official_EnCodec_3p0_current_decode`
- `official_EnCodec_6p0_current_decode`
- package/code hashes
- rate ledger
- listening manifest

### A138.1b AudioCraft / EnCodec Training Scaffold

Goal:

```text
Run a small full-compression-model fine-tune end to end without bird-aware loss.
```

This stage only proves infrastructure:

- training launches reproducibly
- checkpoint saves and reloads
- encode/decode works after fine-tune
- package export works
- rate ledger remains correct
- listening pack can be generated against current anchors

No promotion decision is made from A138.1b unless the scaffold itself is broken.

### A138.1c Neutral Fine-Tune Sanity

Minimal neutral smoke:

```text
train cases:
  100-300 bird clips

heldout:
  A134/A136 failure cases

rate points:
  1.5 kbps
  3 kbps

baseline:
  current official EnCodec anchors regenerated in the same listening pack

candidate:
  EnCodec architecture fine-tuned with a neutral reconstruction objective
```

Neutral objective:

```text
base reconstruction:
  MR-STFT / waveform / mel / logmag as needed for stability

rate behavior:
  train/evaluate at 1.5 and 3 kbps
```

Gate:

```text
If neutral full-codec fine-tune is clearly worse than official EnCodec:
  do not add bird-aware loss yet.
  fix recipe / scale / data / checkpoint handling first.

If neutral fine-tune is roughly stable:
  A138.2 bird-event weighted loss may start.
```

The point of A138.1 is to answer whether training can preserve EnCodec naturalness. This is the lesson from B1: model changes can be metric-positive and listening-negative.

## A138.2 Bird-Event Weighted Loss

A138.2 opens only after A138.1c does not obviously degrade EnCodec naturalness. Current status: A138.2v0 is objective-positive but listening-tie/no-promote after manual listening on 2026-06-29.

Current A138.2v0 artifact:

```text
runs/diagnostics/a1382v0_bird_event_weighted_loss_20260629/
```

A138.2v0 is a differential experiment, not a tuning run:

```text
same minimal training loop
same 8 train clips
same 6 heldout failure cases
same steps
same LR
same train scope: encoder_decoder
same bandwidths: 1.5 / 3.0
only change: loss weighting
```

The implemented v0 objective is intentionally conservative:

```text
loss =
  base_reconstruction_loss
  + 0.25 * event_loss
  + 0.10 * onset_loss
```

Promotion is not allowed from objective loss. A138.2v0 must beat neutral FT perceptually, not merely official EnCodec or weighted loss.

Manual listening verdict on 2026-06-29:

```text
official current anchors, neutral minimal FT, and eventloss FT have no clear audible difference.
A138.2v0 does not show bird-event specialization signal.
Promotion: no.
A138.2v1: not unblocked by this result.
```

The next step is not an A138.2v1 lambda sweep. A138.3 showed stronger neutral overfit can create audible tradeoffs but not stable improvement. The project should now test whether the 1.5 kbps transmission budget should replace part of generic EnCodec RVQ with bird-detail bits.

Current A138.3 artifact:

```text
runs/diagnostics/a1383_encodec_audible_effect_calibration_20260629/
```

Current A139.0 artifact:

```text
runs/diagnostics/a1390_same_rate_hybrid_budget_oracle_20260629/
```

A139.0 listening verdict on 2026-06-29:

```text
UB is a 1.5 kbps total-budget route:
  E0.75 carrier + 0.75 detail budget.

UB clearly beats the 0.75 kbps carrier variants,
but still slightly loses to E1.5_K2_fixed.

Primary gate fails.
A139 same-rate hybrid detail replacement is no-go.
```

A140 freezes the strategic choice:

```text
Option 1: strict 1.5 kbps benchmark / negative oracle study
Option 2: E1.5 + tiny encoder-derived bird-detail side-channel
Option 3: codec-family reset
```

Current A140.1 artifact:

```text
runs/diagnostics/a1401_marginal_side_channel_value_oracle_20260629/
```

A140.1 marginal side-channel value oracle tested `E1.5 + 0.10 / 0.25 / 0.50 kbps`
exact-source-residual upper bounds against same-pack `E1p5_K2_fixed`, with
`E3_K4_fixed` as a reference. Manual listening on 2026-06-30 found no clear
audible difference. It is no-promote and does not unblock a legal side-channel
token design.

Candidate training objective:

```text
base reconstruction:
  MR-STFT / waveform / mel / logmag as needed for stability

bird-event weights:
  event-local MR-STFT
  event-weighted logmel
  event-weighted highband loss
  onset / envelope flux loss
  ridge-continuity proxy if cheap and stable

background behavior:
  lower background weight than bird-event windows
  reject brightness/noise cheating

rate behavior:
  train/evaluate at 1.5 and 3 kbps
  optional RVQ depth dropout or variable-depth regularization only after neutral scaffold is stable
```

## Listening Gate

Neutral sanity gate:

```text
A138.1c pass:
  neutral fine-tune is not clearly worse than current official EnCodec anchors.

A138.1c fail:
  neutral full-codec fine-tune damages naturalness, metallic texture, or stability.
  Do not proceed to bird-aware loss until the training recipe is fixed.
```

Pass:

```text
bird-event FT is not audibly worse than neutral FT
and
at least some failure cases show clearer ridge / onset / event clarity.
```

Strong pass:

```text
bird-event FT is stable better than neutral FT at E1.5 or E3
and
there is no obvious background damage, harshness, or brightness cheating.
```

Fail:

```text
only beats official EnCodec but not neutral FT
brighter but harsher
metric-positive but no listening improvement
damages EnCodec naturalness
improves only by loudness/noise cheating
event is clearer but background is dirtier
```

If neutral full-codec fine-tune cannot preserve EnCodec naturalness, A138 is blocked at training infrastructure, not falsified as a specialization idea. If bird-aware fine-tuning passes neutral sanity but still fails listening, EnCodec-based specialization should be treated as near no-go and the project should move to DAC-family or bird-only codec routes.

## Required A138 Listening Pack Discipline

Every A138 listening pack must include current same-run anchors:

```text
R0_original
official_EnCodec_1p5_current_decode
official_EnCodec_3p0_current_decode
official_EnCodec_6p0_current_decode
candidate_bird_aware_1p5
candidate_bird_aware_3p0
```

A138.2v0 is intentionally compact and keeps only the A138.1b-alt rate points:

```text
R0_original
official_EnCodec_1p5_current_decode
official_EnCodec_3p0_current_decode
neutral_finetune_1p5
neutral_finetune_3p0
bird_event_finetune_1p5
bird_event_finetune_3p0
```

For A138.1c, replace bird-aware candidates with:

```text
candidate_neutral_finetune_1p5
candidate_neutral_finetune_3p0
```

Old A1347 official decoded WAVs are useful for historical context only. They must not be used as strong cross-run listening anchors for A138 verdicts.

## Expected Outputs

Minimum A138.1a outputs:

- current official EnCodec anchor WAVs
- route manifest with package/code hashes
- rate ledger at 1.5, 3, and 6 kbps
- listening manifest with failure-case ordering

Minimum A138.1b/c outputs:

- route manifest with model/checkpoint hashes
- current official EnCodec anchor WAVs
- candidate neutral-finetune WAVs
- rate ledger at 1.5 and 3 kbps
- listening manifest with failure-case ordering
- metric probe separated by event/background windows
- explicit stable/degraded verdict after listening

Minimum A138.2 outputs:

- current official EnCodec anchor WAVs
- candidate bird-aware WAVs
- neutral-finetune reference if available
- rate ledger at 1.5 and 3 kbps
- listening manifest with failure-case ordering
- metric probe separated by event/background windows
- explicit no-promote/pass verdict after listening
