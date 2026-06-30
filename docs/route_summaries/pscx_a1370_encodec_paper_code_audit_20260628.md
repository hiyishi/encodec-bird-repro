# PS-CX A137.0 EnCodec Paper And Code Audit

Date: 2026-06-28  
Purpose: ground the next PS-CX branch in EnCodec's actual paper and implementation before running more adapter or codec-family probes.

## Decision

`a1370_encodec_paper_code_audit_complete`

Post-verdict update: A137.2v0 implemented the masked-latent oracle and failed listening. The A137.0 audit remains useful because it correctly identified EnCodec's RVQ structure and insertion points, but the post-hoc frozen-RVQ allocation branch is now closed. The next EnCodec-based branch is A138 training-time specialization, not more event-mask tuning.

The next useful work is not another decoder adapter scale-up. A136.2c already stopped B1 because correct-package B1 sounded clearly worse than same-rate EnCodec. The audit supports a cleaner next branch:

```text
A137.1 codebook-event analysis:
  analyze which RVQ layers matter inside bird event / ridge / onset windows.

A137.2 event-aware RVQ allocation oracle:
  assemble EnCodec-compatible latents from base codes plus event-local extra RVQ
  layers, with an explicit bitrate ledger.

A137.3 package design:
  only if A137.2 is positive, define base codes + event mask + local extra codes
  as a legal package.

A137.4 optional training:
  only after the oracle works; do not start with decoder fine-tuning.
```

## Local Source Cache

External materials are cached under ignored `cache/` so third-party source and PDFs do not enter the repo commit surface.

```text
cache/external/a1370_encodec/papers/high_fidelity_neural_audio_compression_openreview_ivCd8z8zR2.pdf
  source: https://openreview.net/pdf?id=ivCd8z8zR2
  sha256: F7254D7992BDFCD46CFE4B9D74395090496C41EF53777A05FD984C1637391DD1

cache/external/a1370_encodec/papers/arxiv_2210.13438_metadata.xml
  source: https://export.arxiv.org/api/query?id_list=2210.13438
  sha256: 2E12674D894A4FBB1AB3FB3C9BDAE8B3AF010073B9248D8C163AA6E3FF6D9B15

cache/external/a1370_encodec/src/encodec
  source: https://github.com/facebookresearch/encodec
  commit: 0e2d0aed29362c8e8f52494baf3e6f99056b214f

cache/external/a1370_encodec/src/audiocraft
  source: https://github.com/facebookresearch/audiocraft
  commit: 896ec7c47f5e5d1e5aa1e4b260c4405328bf009d
  scope: sparse checkout of EnCodec docs, solver, model, quantization, and config.
```

Note: direct arXiv PDF download returned a short `Rate exceeded` response during this audit, so the local PDF is the official OpenReview/TMLR copy and arXiv is represented by metadata.

## Paper Facts That Matter

EnCodec is not a loose decoder that can be safely re-headed without care. The paper frames it as:

```text
waveform -> SEANet convolutional/LSTM encoder -> RVQ -> SEANet convolutional/LSTM decoder
```

Key facts from the paper:

1. The 24 kHz streamable encoder emits 75 latent steps per second. With 1024 entries per codebook, each RVQ layer costs `75 * 10 = 750 bps`, or `0.75 kbps`.
2. The 24 kHz model supports 1.5, 3, 6, 12, and 24 kbps by selecting 2, 4, 8, 16, or 32 RVQ codebooks.
3. RVQ layers are residual: each layer quantizes what previous layers did not explain.
4. Training combines waveform L1, multi-scale mel/spectrogram reconstruction loss, MS-STFT discriminator loss, feature matching, RVQ commitment loss, and a gradient loss balancer.
5. Multi-bandwidth training selects the number of RVQ layers for the batch; the paper also reports that dedicated per-bandwidth discriminators improve quality.
6. Entropy coding with a small Transformer LM can reduce realized bandwidth, but it is a coding layer over the same codes, not a new reconstruction mechanism.

Interpretation for PS-CX:

```text
The natural EnCodec insertion point is RVQ layer allocation, not decoder replacement.
Bird vocalizations are sparse and event-local; fixed n_q per frame is therefore
the exact mechanism to challenge first.
```

## Implementation Facts That Matter

Official `facebookresearch/encodec`:

```text
encodec/model.py:
  frame_rate = ceil(sample_rate / prod(encoder.ratios))
  bits_per_codebook = log2(quantizer.bins)
  24 kHz pretrained target bandwidths = [1.5, 3, 6, 12, 24]
  48 kHz pretrained target bandwidths = [3, 6, 12, 24]

encodec/modules/seanet.py:
  default ratios = [8, 5, 4, 2]
  hop_length = 320
  24 kHz / 320 = 75 Hz
  48 kHz / 320 = 150 Hz

encodec/quantization/vq.py:
  bw_per_q = log2(bins) * frame_rate
  n_q = floor(target_kbps * 1000 / bw_per_q)

encodec/quantization/core_vq.py:
  residual is updated as residual - quantized at each layer
  decode sums the selected residual-layer quantized vectors

encodec/model.py:
  public encode returns codes as [B, K, T]
  internal RVQ stack uses [K, B, T]
```

AudioCraft training implementation:

```text
docs/ENCODEC.md:
  CompressionSolver trains SEANet + RVQ with objective and perceptual losses.

audiocraft/solvers/compression.py:
  qres = model(x)
  logs qres.bandwidth
  applies adversarial, feature, auxiliary, and quantizer penalty losses.

audiocraft/models/encodec.py:
  set_num_codebooks(n) is explicit.
  encode returns [B, K, T].
  decode_latent(codes) exposes quantizer-to-latent before decoder.

audiocraft/quantization/vq.py:
  q_dropout can randomly vary active RVQ layers during training.
  set_num_codebooks changes active K without changing total available codebooks.

config/model/encodec/encodec_base_causal.yaml:
  rvq.n_q = 32
  rvq.q_dropout = true

config/model/encodec/default.yaml:
  rvq.bins = 1024
  seanet.ratios = [8, 5, 4, 2]
  seanet.lstm = 2
```

Interpretation:

```text
Event-aware RVQ allocation can be tested without retraining by assembling a
masked latent from existing codebook vectors and feeding the frozen decoder.
This is not standard .ecdc decoding, but it is EnCodec-compatible in the sense
that it uses the same encoder, RVQ codebooks, residual summation, and decoder.
```

## Immediate Experimental Insertion Points

### 1. Codebook-event analysis

Use high-rate EnCodec codes as the analysis source. For each clip:

```text
extract event / ridge / onset / active masks
encode full codes at K=32 or available maximum
for each prefix K and each residual layer k:
  reconstruct or decode latent contribution
  measure event-window delta vs background-window delta
  record code occupancy / entropy conditioned on event type
```

Expected output:

```text
layer importance curves:
  per RVQ layer contribution in event windows
  per RVQ layer contribution in non-event/background windows

alignment tables:
  codebook usage vs ridge/onset/highband event features

decision:
  whether bird details are concentrated in late RVQ layers during sparse events
```

This is the cheapest way to test whether fixed RVQ depth wastes bits on background while under-serving event detail.

### 2. Event-aware RVQ allocation oracle

Construct a frozen-decoder oracle:

```text
base latent:
  decode/sum first K_base RVQ layers everywhere

event extra latent:
  add selected extra RVQ layers only at event frames

background:
  no extra layers, or explicitly fewer layers

decoder:
  frozen EnCodec decoder
```

Rate ledger:

```text
24 kHz per RVQ layer = 0.75 kbps before entropy coding.

average kbps =
  0.75 * K_base
  + 0.75 * sum(extra_layers_i * event_coverage_i)
  + event_mask_kbps
  + package headers
```

Useful examples:

```text
K_base=2 everywhere:
  base = 1.5 kbps

K_base=2 plus 4 extra layers on 50% event frames:
  nominal = 1.5 + 0.75 * 4 * 0.5 = 3.0 kbps before mask/header

K_base=2 plus 8 extra layers on 25% event frames:
  nominal = 1.5 + 0.75 * 8 * 0.25 = 3.0 kbps before mask/header
```

Gate:

```text
At matched or near-matched average bitrate, event-aware allocation must beat
same-rate fixed EnCodec on the A134/A136 failure cases by listening, not just
proxy metrics.
```

### 3. EnCodec-compatible package design

Only after a positive oracle:

```text
package =
  fixed model id
  audio length
  base K
  base codes [B, K_base, T]
  event mask / event spans
  event-local extra codebook indices
  bitrate ledger
```

Decoder runtime remains legal:

```text
input allowed:
  package + fixed model artifacts

input forbidden:
  source wav
  teacher spectrograms
  uncounted residual side files
```

### 4. Optional training, last

Training should be opened only after event-aware allocation works as an oracle. Candidate training routes:

```text
frozen EnCodec decoder + event-aware quantizer / allocation controller
bird-event weighted quantizer loss
small corrector over decoded latent, not waveform postfilter first
custom bird-only RVQ smoke if EnCodec allocation oracle is negative
```

## No-Promote Boundaries

Do not do these next:

```text
Do not scale A136.2b/B1 decoder fine-tune.
Do not claim B1 proves EnCodec latent sufficiency.
Do not claim B1 proves EnCodec latent insufficiency.
Do not train a larger adapter before codebook-event analysis.
Do not promote objective-only wins without manual listening.
Do not treat standard .ecdc bitstream compatibility as required for the oracle;
  the oracle is allowed to be a custom legal package as long as every bit is counted.
```

## Working Hypothesis After A137.0

```text
Generic EnCodec is strong because the SEANet/RVQ/decoder prior is strong.
Its weakness for bird failure cases may be fixed-n_q allocation rather than
global architecture capacity.

If late RVQ layers carry event-local bird detail, a sparse event-aware codebook
allocation can become a paper contribution:

  Event-aware EnCodec for sparse bioacoustic signals.

If late RVQ layers do not carry recoverable event detail, the result is still
decision-quality and should push the project toward A136.3 bird-only RVQ /
neural codec smoke.
```

## Next Step

```text
A137.1:
  implement codebook-event analysis on the known A134/A136 failure cases.

A137.2:
  if A137.1 shows event-local RVQ layer concentration, build the masked-latent
  allocation oracle and compare against fixed EnCodec 1.5/3/6 at the same
  average bitrate.
```
