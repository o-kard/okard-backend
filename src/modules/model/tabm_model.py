import torch
import torch.nn as nn

from tabm import TabM, LinearEnsemble, LayerNormEnsemble  

head_dims = {
    "success_cls": 2,
    "risk_level": 3,
    "days_to_state_change": 4,
    "recommend_category": 10,  
    "goal_eval": 3,
    "stretch_potential_cls": 3,
}

# ==== classes ที่คุณเขียนไว้ ====
class _MLP(nn.Module):
    def __init__(self, d_in, out_dim, hidden=128, depth=2, dropout=0.1):
        super().__init__()
        layers, d = [], d_in
        for _ in range(depth-1):
            layers += [nn.Linear(d, hidden), nn.ReLU(), nn.Dropout(dropout)]
            d = hidden
        layers += [nn.Linear(d, out_dim)]
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class MLPEnsemble(nn.Module):
    def __init__(self, d_in, out_dim, k, hidden=128, depth=2, dropout=0.1):
        super().__init__()
        self.mlps = nn.ModuleList([_MLP(d_in, out_dim, hidden, depth, dropout) for _ in range(k)])

    def forward(self, z):
        outs = [self.mlps[i](z[:, i, :]) for i in range(len(self.mlps))]
        return torch.stack(outs, dim=1)


class MLPHeadShared(nn.Module):
    def __init__(self, d_in, out_dim, hidden=128, depth=2, dropout=0.1):
        super().__init__()
        layers = []
        d = d_in
        for _ in range(depth-1):
            layers += [nn.Linear(d, hidden), nn.ReLU(), nn.Dropout(dropout)]
            d = hidden
        layers += [nn.Linear(d, out_dim)]
        self.net = nn.Sequential(*layers)

    def forward(self, z):
        B, k, D = z.shape
        y = self.net(z.reshape(B*k, D))
        return y.view(B, k, -1)


class TabMHeads(nn.Module):
    def __init__(self, d_in: int, k: int, head_dims: dict[str, int]):
        super().__init__()
        self.k = k
        self.heads = nn.ModuleDict({
            name: LinearEnsemble(d_in, out_dim, k=k)
            for name, out_dim in head_dims.items()
        })

    def forward(self, z):
        return {name: head(z) for name, head in self.heads.items()}


class TabMMultiHead(nn.Module):
    def __init__(self, n_num_features, cat_cardinalities, head_dims: dict[str, int],
                 k=14, d_block=512, n_blocks=5, dropout=0.3,
                 start_scaling_init="random-signs"):
        super().__init__()
        self.k = k
        self.backbone = TabM(
            n_num_features=n_num_features,
            cat_cardinalities=cat_cardinalities,
            d_out=None,
            k=k,
            n_blocks=n_blocks,
            d_block=d_block,
            dropout=dropout,
            arch_type='tabm',
            start_scaling_init=start_scaling_init,
        )
        d_latent = d_block
        self.heads = nn.ModuleDict({
            name: nn.Sequential(
                LayerNormEnsemble(d_latent, k=k),
                LinearEnsemble(d_latent, out_dim, k=k),
            )
            for name, out_dim in head_dims.items()
        })

    def forward(self, x_num, x_cat=None):
        z = self.backbone(x_num, x_cat)
        return {name: head(z) for name, head in self.heads.items()}


# ===== helper สำหรับ backend =====
def load_model(model_path, device="cpu"):
    checkpoint = torch.load(model_path, map_location=device)
    config = checkpoint["config"]

    model = TabMMultiHead(**config).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model

