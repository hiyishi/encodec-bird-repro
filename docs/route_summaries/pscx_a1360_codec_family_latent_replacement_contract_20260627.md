# A136.0 Codec-Family / Latent Replacement Contract

## Decision

`a1360_codec_family_latent_replacement_contract_open`

## Freeze

```text
A135.1 proxy-loss adapter:
  no-promote
  do not scale

A135.2 objective validity:
  pass
  metrics separate DAC8/Opus ceilings from EnCodec6

Next bottleneck:
  codec family / quantized latent / decoder prior
```

## A136 Questions

```text
Q1: Has EnCodec package already discarded bird-call detail?
Q2: Can a different codec family or bird-only latent approach DAC8/Opus ceiling?
Q3: Are ceiling-valid metrics useful as losses, or only as diagnostics?
```

## Stage Plan

```text
A136.1 codec-family ceiling smoke
A136.2 EnCodec latent sufficiency oracle
A136.3 small bird-only RVQ autoencoder smoke
```

Promotion requires manual listening. Objective metrics can support routing, but
cannot promote a codec candidate by themselves.
