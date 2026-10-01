"""Contrastive activation addition in Apple MLX (mlx-lm). The same method as steer.py, 5-10x faster on the Mac.

A wrapper replaces one decoder block: it can record the block's output (to build directions) or add a fixed
vector to it at every position (to steer). hidden_states[L] in Hugging Face terms is the output of block L-1.
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn


class _Tap(nn.Module):
    def __init__(self, block):
        super().__init__()
        self.block, self.vector, self.record = block, None, None

    def __call__(self, h, mask=None, cache=None):
        out = self.block(h, mask, cache)
        if self.record is not None:
            self.record.append(out.astype(mx.float32).mean(axis=1)[0])
        if self.vector is not None:
            out = out + self.vector.astype(out.dtype)
        return out


def load(repo: str):
    from mlx_lm import load as _load
    return _load(repo)


def tap(model, layer: int) -> _Tap:
    """Install (once) and return the tap on block `layer - 1`."""
    inner = model.model
    i = layer - 1
    if isinstance(inner.layers[i], _Tap):
        return inner.layers[i]
    t = _Tap(inner.layers[i])
    inner.layers[i] = t
    return t


def activations(model, tok, texts: list, layer: int):
    """One token-mean activation per text at `layer`, stacked (texts x hidden)."""
    t = tap(model, layer)
    t.record, t.vector = [], None
    for text in texts:
        model(mx.array(tok.encode(text))[None])
    vecs = mx.stack(t.record)
    t.record = None
    return vecs


def mean_activation(model, tok, texts: list, layer: int):
    t = tap(model, layer)
    t.record, t.vector = [], None
    for text in texts:
        model(mx.array(tok.encode(text))[None])
    vecs = mx.stack(t.record)
    t.record = None
    norms = mx.linalg.norm(vecs, axis=1)
    return vecs.mean(axis=0), float(norms.mean().item())


def unit(v):
    return v / mx.linalg.norm(v)


def generate(model, tok, prompt: str, *, vector=None, layer: int = 14, max_tokens: int = 384,
             temp: float = 0.0, top_p: float = 1.0, seed: int | None = None) -> str:
    from mlx_lm import generate as _gen
    from mlx_lm.sample_utils import make_sampler
    t = tap(model, layer)
    t.vector = vector
    try:
        messages = [{"role": "system", "content": "You are a helpful coding assistant."},
                    {"role": "user", "content": "Complete the following Python code. Return only the code.\n\n"
                                                f"```python\n{prompt}\n```"}]
        text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        if seed is not None:
            mx.random.seed(seed)
        return _gen(model, tok, prompt=text, max_tokens=max_tokens, verbose=False,
                    sampler=make_sampler(temp=temp, top_p=top_p))
    finally:
        t.vector = None
