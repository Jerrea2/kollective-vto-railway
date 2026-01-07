# Minimal shim: enough to satisfy imports/instantiation.
import torch
import torch.nn as nn

class Resampler(nn.Module):
    def __init__(self, dim=1280, depth=4, dim_head=64, *args, **kwargs):
        super().__init__()
        # a tiny no-op proj so shapes are harmless if called
        self.out_dim = dim
        self.proj = nn.Identity()

    def forward(self, x=None, *args, **kwargs):
        # Return input if it's a tensor; otherwise return a tiny placeholder
        if isinstance(x, torch.Tensor):
            return self.proj(x)
        # produce a benign tensor if upstream passes None
        return torch.zeros(1, 1, self.out_dim)
