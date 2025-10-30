import torch
import torch.nn as nn

class PositionNet(nn.Module):
    def __init__(self, positive_len=2, out_dim=1024, feature_type="concat"):
        super().__init__()
        self.positive_len = positive_len
        self.feature_type = feature_type
        # Small MLP that mimics a positional feature projector
        self.net = nn.Sequential(
            nn.Linear(positive_len, out_dim // 2),
            nn.SiLU(),
            nn.Linear(out_dim // 2, out_dim),
        )

    def forward(self, pos: torch.Tensor):
        # pos expected shape: (B, positive_len) or broadcastable to it
        if pos.dim() > 2:
            pos = pos.flatten(start_dim=1)
        return self.net(pos.float())
