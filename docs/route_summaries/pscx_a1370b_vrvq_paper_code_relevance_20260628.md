# PS-CX A137.0b VRVQ Paper And Code Relevance Audit

Date: 2026-06-28  
Paper: Variable Bitrate Residual Vector Quantization for Audio Coding  
URL: https://arxiv.org/abs/2410.06016  
Purpose: check whether VRVQ contains mechanisms useful for A137 event-aware EnCodec / RVQ allocation.

## Decision

`a1370b_vrvq_relevant_for_event_aware_rvq_oracle`

Post-verdict update: A137.2v0 used this masked-RVQ mechanism as a frozen EnCodec oracle and failed listening. VRVQ remains relevant as literature and mechanism support for variable-depth RVQ, but it no longer justifies continued post-hoc allocation on frozen EnCodec latents. Its remaining relevance is for training-time behavior in A138 or later codec-family work.

VRVQ is directly relevant. It formalizes exactly the weakness A137.0 identified in EnCodec: RVQ codecs usually use a fixed number of codebooks per latent frame, which can be suboptimal for rate-distortion. VRVQ's useful contribution for us is not the DAC training stack itself, but the frame-wise RVQ layer mask:

```text
per-frame mask m[B, K, T]
per-layer residual contribution z_q_is[B, K, D, T]
masked latent z_q = sum_k z_q_is[:, k] * m[:, k]
```

This is almost the same operation needed for A137.2 EnCodec-compatible event-aware allocation oracle.

## Local Source Cache

```text
cache/external/a1370_vrvq/papers/variable_bitrate_residual_vector_quantization_arxiv_2410.06016.pdf
  source: https://arxiv.org/pdf/2410.06016
  sha256: 642275A6F13D27D34D1341E4049993FE8B8950354E6BFA055F1B6DFE397B74E5

cache/external/a1370_vrvq/papers/arxiv_2410.06016_metadata.xml
  source: https://export.arxiv.org/api/query?id_list=2410.06016
  sha256: 9D7A0E20D729C3583AA1CE209D56C5A7E2459938A5742D2B4EEB6F79B75A3ECE

cache/external/a1370_vrvq/src/VRVQ
  source: https://github.com/SonyResearch/VRVQ
  commit: 1033370e09b108a41b11fde31a959489dfe2d132
```

## Paper Facts That Matter

Key claims:

```text
Problem:
  fixed number of RVQ codebooks per frame is inefficient.

Method:
  learn an importance map p[B, 1, T].
  convert p to a monotonic binary mask m[B, K, T].
  use m to decide how many residual codebooks each frame uses.

Training:
  optimize distortion + lambda * rate loss.
  rate loss is mean importance map.
  use a straight-through estimator for the hard mask.
  sample scaling factor l during training so one model supports multiple rates.

Codec base:
  DAC / improved RVQGAN-style model at 44.1 kHz.
  hop length 512, frame rate about 86 Hz.
  Nq=8, codebook size 1024, so each selected codebook index costs 10 bits.
```

Important caveats:

```text
They did not train a separate entropy model in this paper.
They count an extra per-frame codebook-count transmission cost.
For Nq=8, count overhead is log2(8)=3 bits/frame, about 0.258 kbps.
At low bitrates, that overhead can eat much of the VBR benefit.
```

This overhead warning matters for Bio-FARGAN: event masks and local K values cannot be treated as free.

## Source Facts That Matter

Core files:

```text
models/utils.py
  generate_mask_ste(x, nq, alpha)
  generate_mask_hard(x, nq)
  cal_bpf_from_mask(mask, bits_per_codebook)

models/quantize.py
  VBRResidualVectorQuantize.forward(...)
  builds z_q_is as [B, Nq, D, T]
  builds mask_imp as [B, Nq, T]
  applies z_q = sum(z_q_is * mask_imp[:, :, None, :], dim=1)

models/importance_subnet.py
  small Conv1D importance subnet with sigmoid output [B, 1, T]

models/dac_vrvq.py
  DAC_VRVQ wraps encoder, VBR quantizer, and decoder.

scripts/inference.py
  reuses one full encode pass, rescales imp_map by level, hardens mask,
  sums masked z_q_is, decodes, and computes kbps.
```

Implementation details worth copying:

```text
Hard mask:
  m[k, t] = 1 if scaled_importance[t] - k >= 0 else 0

Monotonicity:
  lower RVQ layers are always kept before higher RVQ layers.

Rate calculation:
  bpf = mean over frames of sum_k mask[k, t] * bits_per_codebook[k]
  kbps = bpf * frame_rate / 1000

Inference control:
  scale importance map by a continuous level to sweep rate without retraining.
```

## What We Should Use

### Use immediately for A137.2 oracle

Use VRVQ's mask application pattern over EnCodec RVQ residual contributions:

```text
encode source with full/high EnCodec K
recover per-layer quantized vectors z_q_is[B, K, D, T]
build a bird-event mask m[B, K, T]
z_q_event = sum_k z_q_is[:, k] * m[:, k]
decode z_q_event with frozen EnCodec decoder
ledger = selected_code_bits + event-mask bits + headers
```

The first mask should not be learned. It should be an oracle or deterministic mask from existing bird event / ridge / onset detectors:

```text
background:
  K_base = 2 or 4

event frames:
  K_base + extra K, e.g. 4/8/16

transition frames:
  small dilation or fade in K to avoid boundary artifacts
```

This isolates the core question:

```text
Does EnCodec contain event-local bird detail in later RVQ layers?
```

### Use for A137.1 analysis

VRVQ gives the right visualization language:

```text
plot [K x T] codebook-use masks
overlay bird event / ridge / onset marks
measure event vs non-event selected-layer utility
compute bpf/kbps from the actual mask
```

### Use later for training

If A137.2 works, a learned importance subnet becomes plausible:

```text
input:
  EnCodec encoder intermediate feature, or bird-event features, or both

target:
  event-aware rate-distortion objective

loss:
  reconstruction / bird metrics + lambda * mean importance

gradient:
  STE or soft surrogate mask, following VRVQ
```

Do not start here. It is a training project, not the next oracle.

## What We Should Not Use Directly

```text
Do not assume Sony VRVQ weights solve bird calls.
Do not replace EnCodec with VRVQ as-is; it is DAC-based and trained on broad audio.
Do not copy their rate wins without checking manual listening on our failure cases.
Do not ignore codebook-count/mask overhead; the paper explicitly shows low-rate VBR gains can diminish.
Do not train an importance map before proving masked RVQ allocation has listening upside.
```

## Relevance To Current Branch

VRVQ strongly supports the A137 branch:

```text
A137.0:
  EnCodec audit says fixed RVQ layer count is the natural insertion point.

A137.0b:
  VRVQ gives a published method and source code for frame-wise RVQ layer masking.

A137.1:
  analyze event-local utility of EnCodec RVQ layers.

A137.2:
  implement masked-latent EnCodec oracle with explicit event-mask overhead.

A137.3:
  if positive, design legal package: base codes + event-local extra codes + mask/count stream.

A137.4:
  only then consider learned importance/event allocation.
```

## Recommended Next Experiment

Run a non-training masked latent oracle:

```text
Name:
  A137.2v0 EnCodec event-mask RVQ allocation oracle

Inputs:
  A134/A136 EnCodec failure cases
  frozen EnCodec 24 kHz model
  event / ridge / onset masks already available or cheaply derived

Routes:
  fixed K=2, K=4, K=8 baselines
  K=2 everywhere + extra K on event frames
  K=4 everywhere + extra K on event frames
  optional random-frame extra-K control at same average kbps

Must report:
  selected bits/frame
  average kbps
  event mask/header kbps
  objective diagnostics
  manual listening pack

Pass condition:
  event-aware route beats same-rate fixed EnCodec by listening on failure cases.
```

If this fails, VRVQ still helped by giving us a strong negative: the issue is likely not just fixed RVQ allocation inside EnCodec, and the branch should move toward bird-only RVQ / neural codec smoke.
