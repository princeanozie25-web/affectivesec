"""Contrastive activation addition on a Hugging Face causal LM (prereg/pilot-01.md)."""

from __future__ import annotations

import torch

from .lexicon import CALM, DESPERATE, NEUTRAL


def load(model_id: str, device: str = "mps"):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16).to(device).eval()
    return tok, model


@torch.no_grad()
def mean_activation(tok, model, texts: list, layer: int) -> tuple:
    """(mean over texts of the token-mean of hidden_states[layer], mean L2 norm of those token-means)."""
    vecs = []
    for t in texts:
        ids = tok(t, return_tensors="pt").to(model.device)
        h = model(**ids, output_hidden_states=True).hidden_states[layer][0].float()
        vecs.append(h.mean(0))
    stack = torch.stack(vecs)
    return stack.mean(0), stack.norm(dim=1).mean().item()


def directions(tok, model, layer: int, seed: int = 20261001) -> tuple:
    """({name: unit vector}, N) where N is the mean neutral activation norm at `layer`."""
    neutral, norm = mean_activation(tok, model, NEUTRAL, layer)
    out = {}
    for name, texts in (("desperate", DESPERATE), ("calm", CALM)):
        mean, _ = mean_activation(tok, model, texts, layer)
        d = mean - neutral
        out[name] = d / d.norm()
    g = torch.Generator().manual_seed(seed)
    r = torch.randn(neutral.shape[0], generator=g)
    out["random"] = (r / r.norm()).to(neutral.device)
    return out, norm


class Steer:
    """Adds `vector` to the output of decoder layer `layer - 1` (that output is hidden_states[layer])."""

    def __init__(self, model, layer: int, vector):
        self.vector, self.handle = vector, None
        block = model.model.layers[layer - 1]
        self.handle = block.register_forward_hook(self._hook) if vector is not None else None

    def _hook(self, module, args, output):
        if isinstance(output, tuple):
            return (output[0] + self.vector.to(output[0].dtype),) + tuple(output[1:])
        return output + self.vector.to(output.dtype)

    def close(self):
        if self.handle is not None:
            self.handle.remove()


@torch.no_grad()
def generate(tok, model, prompt: str, max_new_tokens: int = 384) -> str:
    messages = [{"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Complete the following Python code. Return only the code.\n\n"
                                            f"```python\n{prompt}\n```"}]
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").to(model.device)
    out = model.generate(**ids, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
