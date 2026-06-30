# PS-CX A138.1 EnCodec Training Scaffold

Generated: 2026-06-28

## Decision

- A138.1a current anchors: `pass`
- A138.1b AudioCraft/Dora scaffold: `abandoned_after_one_unblock_attempt`
- A138.1b-alt minimal EnCodec training loop: `pass`
- A138.1c neutral fine-tune sanity: `pass`
- A138.2v0 downstream verdict: `objective-positive / listening-tie / no-promote`
- A138.3 downstream verdict: `audible effect present / mixed tradeoff / no positive specialization`
- A139.0 downstream verdict: `UB beats E0.75 variants but loses E1.5 / no-go`
- A139.1 downstream status: `not unblocked`
- A140 downstream status: `decision freeze accepted`
- A140.1 downstream status: `marginal side-channel value oracle listening-tie / no-promote`
- Training path anchor policy: `blocked_until_anchor_policy_resolved`
- Immediate next: `external expert direction review; choose benchmark/negative-oracle paper vs codec-family reset.`

A138.1 is not trying to beat EnCodec. It checks whether current anchors are reproducible and whether the AudioCraft/EnCodec training stack is ready before any bird-aware loss is attempted.

## Hard Gates

- Current anchors rebuild pass: `True`
- AudioCraft import pass: `True`
- Dora import pass: `True`
- CompressionSolver import pass: `False`
- Dora config resolve pass: `False`
- AudioCraft EnCodec anchor rebuild pass: `False`
- AudioCraft vs official anchor parity pass: `False`
- Training scaffold pass: `False`
- Micro-overfit loss decrease pass: `False`
- Checkpoint save/load pass: `False`
- Neutral fine-tune sanity pass: `True`
- Neutral FT audible degradation: `False`
- Checkpoint replay pass: `False`
- Rate ledger pass: `True`
- Forbidden source path audit pass: `True`
- Review bundle generated pass: `True`

A138.1b cannot pass on loss decrease alone. It must also prove checkpoint save/load replay, package reproducibility, rate ledger consistency, source-path hygiene, and independent review-bundle generation.

A138.1b-0 compatibility bridge must resolve the training path anchor policy before training verdicts. If AudioCraft-path anchors differ from current official `encodec` anchors, all A138 training comparisons must use AudioCraft-path anchors.

A single AudioCraft/Dora unblock attempt was made. Dora became runnable, but `CompressionSolver` failed because the cached AudioCraft source lacks `audiocraft.modules`. The project therefore stopped repairing AudioCraft/Dora and switched to `A138.1b-alt` minimal current-`encodec` training loop.

`A138.1b-alt` passed the trainability audit:

```text
micro_overfit_loss_decrease_pass: true
checkpoint_save_load_pass: true
checkpoint_replay_pass: true
package_replay_pass: true
rate_ledger_pass: true
forbidden_source_path_audit_pass: true
review_bundle_generated_pass: true
```

A138.1c is judged by listening first: metallic, watery, muffled, noisy, harsher high-frequency, dirtier background, or smeared bird events are fail conditions even if metrics improve.

Manual verdict on 2026-06-29: neutral FT did not audibly damage EnCodec. A138.1c passes and A138.2 is unblocked.

Downstream A138.2v0 verdict on 2026-06-29: eventloss, neutral minimal FT, and current official anchors had no clear audible difference. A138.2v0 is no-promote and does not unblock A138.2v1.

Downstream A138.3 artifact generated on 2026-06-29: `D:\codebase\biofargan\runs\diagnostics\a1383_encodec_audible_effect_calibration_20260629`. This is not a candidate route; it calibrates whether stronger neutral FT can create a clearly audible output change.

Downstream A138.3 listening verdict on 2026-06-29: stronger overfit FT did not bring a clear improvement; official EnCodec and overfit FT sounded like tradeoffs. A139.0 was opened to test same-rate replacement of generic RVQ bits with bird-detail bits.

Downstream A139.0 listening verdict on 2026-06-29: the exact event residual UB is a 1.5 kbps total-budget route (`E0.75 carrier + 0.75 detail budget`). It clearly beats the 0.75 kbps carrier variants, but still slightly loses to `E1p5_K2_fixed`. A139.0 is no-go.

Downstream A140 status on 2026-06-29: decision freeze accepted. EnCodec-compatible small-change routes are exhausted except for the marginal side-channel value question.

Downstream A140.1 artifact generated on 2026-06-29: `D:\codebase\biofargan\runs\diagnostics\a1401_marginal_side_channel_value_oracle_20260629`. It compares `E1p5_K2_fixed` against `E1.5 + 0.10/0.25/0.50 kbps` exact-source-residual upper bounds, with `E3_K4_fixed` as reference. These UB routes are not legal candidate bitstreams.

Downstream A140.1 manual verdict on 2026-06-30: all three marginal exact-detail UB budgets had no clear audible difference from `E1p5_K2_fixed`. A140.1 is no-promote and does not unblock a legal side-channel token design.

## Outputs

- Output directory: `D:\codebase\biofargan\runs\diagnostics\a1381_encodec_training_scaffold_20260628`
- Current anchor manifest: `D:\codebase\biofargan\runs\diagnostics\a1381_encodec_training_scaffold_20260628\anchors\current_anchor_manifest.csv`
- Listening manifest: `D:\codebase\biofargan\runs\diagnostics\a1381_encodec_training_scaffold_20260628\review_bundle\listening_manifest.csv`
- Rate ledger: `D:\codebase\biofargan\runs\diagnostics\a1381_encodec_training_scaffold_20260628\rate_ledger.csv`
- Scaffold checks: `D:\codebase\biofargan\runs\diagnostics\a1381_encodec_training_scaffold_20260628\train_smoke\scaffold_checks.csv`
- Training log: `D:\codebase\biofargan\runs\diagnostics\a1381_encodec_training_scaffold_20260628\train_log.csv`
- Summary: `D:\codebase\biofargan\runs\diagnostics\a1381_encodec_training_scaffold_20260628\summary.json`

## Gate

A138.1c opened A138.2v0 because neutral full-codec fine-tuning did not clearly degrade EnCodec naturalness. A138.2v0 itself is now no-promote after listening-tie against neutral FT and current official anchors.
