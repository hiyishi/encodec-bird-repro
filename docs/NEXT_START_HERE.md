# Next Start Here

This file is for resuming the EnCodec / bioacoustic compression work on a new machine, with a new local dataset, after time away from the original Bio-FARGAN workspace.

The goal is not to replay every old experiment. The goal is to restore context quickly, avoid repeating no-promote routes, and make the next direction decision with fresh data.

## Current Mental Model

The previous work did not prove that EnCodec is useless for bioacoustics. It proved something narrower and more useful:

```text
EnCodec is a strong low-bitrate baseline.
Small EnCodec-compatible patches did not produce clear perceptual gains on our hard cases.
Metrics often moved before listening did.
Future work should start from the failure shape of the new dataset, not from old adapter tricks.
```

Treat the existing conclusions as guardrails, not as a ban on future EnCodec work.

## Do Not Restart Here

These routes already consumed enough evidence that they should not be the first new attempt:

```text
decoder-only EnCodec fine-tune
small adapter scale-up
post-hoc frozen RVQ event4/event8 mask tuning
same-rate E0.75 + event residual replacement of EnCodec K2
tiny E1.5 + 0.10/0.25/0.50 kbps waveform residual side-channel
metric-only promotion without listening
old PS-CX body2 carrier repair
```

Only reopen one of these if the new dataset produces a clearly different failure mode or an expert identifies a specific flaw in the old setup.

## Day 1 On A New Machine

1. Clone the repo:

```bash
git clone https://github.com/hiyishi/encodec-bird-repro.git
cd encodec-bird-repro
```

2. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a manifest for the new local data:

```text
clip_id,wav_path,split,species,group
my_clip_001,/path/to/audio001.wav,eval,unknown,site_a
my_clip_002,/path/to/audio002.wav,train,unknown,site_b
```

Required columns:

```text
clip_id,wav_path
```

Optional columns:

```text
split,species,group
```

4. Rebuild current EnCodec anchors:

```bash
python scripts/01_build_anchors.py --manifest manifest.csv --out_dir runs/anchors --clean
```

5. Listen first:

```text
R0_original
E1p5_K2_fixed
E3_K4_fixed
E6_K8_fixed
```

The first question is not "can we improve EnCodec?" It is:

```text
Does EnCodec 1.5/3/6 separate on this new dataset?
```

## Phase 1: Diagnose The New Dataset

Use the anchors to label clips:

```text
good_at_1p5:
  EnCodec 1.5 is already acceptable.

rate_separating:
  E3 or E6 clearly improves over E1.5.

hard_nonseparating:
  E1.5/E3/E6 have similar defects.

artifact_family:
  metallic / watery / muffled / noisy / harsh / dull / smeared / background damage.
```

The most important subset is:

```text
hard_nonseparating
```

Those are the clips where a specialized bioacoustic route might matter.

## Phase 2: Only Rerun Diagnostics If They Answer A New Question

Frozen RVQ allocation diagnostic:

```bash
python scripts/02_event_masked_rvq_oracle.py --manifest manifest.csv --out_dir runs/a137_masked_rvq --clean
```

Use this only to answer:

```text
Do later frozen EnCodec RVQ layers contain locally reusable bird-event detail on this dataset?
```

Exact-detail oracle:

```bash
python scripts/04_detail_oracles.py --manifest manifest.csv --out_dir runs/detail_oracles --mode both --clean
```

Use this only to answer:

```text
Would a generous source-derived detail upper bound audibly beat E1.5?
```

If these diagnostics tie again, do not design compressed side tokens.

## Phase 3: Minimal Training Smoke

Neutral FT safety check:

```bash
python scripts/03_minimal_finetune.py --manifest manifest.csv --out_dir runs/minimal_ft --steps 20 --clean
```

Event-weighted smoke:

```bash
python scripts/03_minimal_finetune.py --manifest manifest.csv --out_dir runs/eventloss_ft --loss_mode event --steps 20 --clean
```

Interpretation:

```text
neutral FT worse than official:
  training recipe is not safe. Stop and fix training before adding bird losses.

neutral FT ties official, eventloss ties neutral:
  same pattern as old A138. Do not lambda-sweep by default.

eventloss clearly beats neutral by listening:
  new dataset may have a real EnCodec specialization signal.
```

## Phase 4: Direction Decision

After anchors and optional diagnostics, choose one branch.

### Branch A: Benchmark / Negative Oracle Study

Choose this if:

```text
EnCodec 1.5 is strong.
E1.5/E3/E6 hard cases remain nonseparating.
RVQ masks and detail UBs do not help.
Small FT does not help.
```

Possible claim:

```text
Generic neural codecs are strong for sparse bioacoustic signals, but some
failure cases resist common EnCodec-compatible specialization mechanisms.
```

### Branch B: Codec-Family Reset

Choose this if:

```text
The hard cases remain important and EnCodec-compatible diagnostics tie again.
```

Start with:

```text
DAC-family low-rate tests
SoundStream-style or DAC-style low-rate codec smoke
small bird-domain RVQ autoencoder
```

Keep the same listening discipline:

```text
official EnCodec anchors
DAC / Opus ceilings where available
wrong-package or wrong-recording controls
manual listening gate
```

### Branch C: New EnCodec Training Mechanism

Choose this only if there is a genuinely new mechanism, not another small FT:

```text
full codec retraining
encoder+quantizer behavior change
learned variable-depth RVQ trained end-to-end
bird-event discriminator or stronger perceptual loss
larger data scale
clear same-run official anchors
```

Do not call a lambda sweep a new mechanism.

## What Would Change The Old Conclusion?

A new result is meaningful if it shows one of these:

```text
E1.5 + exact-detail UB clearly beats E1.5 on the new dataset.

Event-masked RVQ beats fixed EnCodec and controls do not.

Event-loss FT clearly beats neutral FT by listening, not only metrics.

A different codec family beats EnCodec 1.5/3 at the same rate without hallucination.
```

Anything weaker is useful diagnostic context, but not a route promotion.

## Reading Order

For context, read:

1. `docs/route_summaries/pscx_a133_a1401_encodec_external_expert_direction_brief_20260630.md`
2. `docs/route_summaries/pscx_a140_decision_freeze_after_encodec_no_go_20260629.md`
3. `docs/route_summaries/pscx_a1401_marginal_side_channel_value_oracle_20260629.md`
4. `docs/route_summaries/pscx_a1371_2v0_encodec_event_masked_rvq_oracle_20260628.md`
5. `docs/route_summaries/pscx_a138_training_time_encodec_specialization_route_contract_20260628.md`

## North Star

Do not let the old negative chain make the project feel closed.

Use it to avoid wasting the first week.

The next useful question is:

```text
On the new dataset, is the problem EnCodec's bitrate,
EnCodec's representation,
the training objective,
or the codec family?
```
