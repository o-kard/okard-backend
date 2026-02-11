import torch
import torch.nn as nn

from tabm import TabM, LinearEnsemble, LayerNormEnsemble  



# ==== classes จากงานวิจัย (TabM.ipynb) ====
class MLPHeadShared(nn.Module):
    def __init__(self, d_in, out_dim, hidden=128, depth=2, dropout=0.1):
        super().__init__()
        layers = []
        d = d_in
        for _ in range(depth - 1):
            layers += [nn.Linear(d, hidden), nn.ReLU(), nn.Dropout(dropout)]
            d = hidden
        layers += [nn.Linear(d, out_dim)]
        self.net = nn.Sequential(*layers)

    def forward(self, z):  # z: (B, k, d_in)
        B, k, D = z.shape
        y = self.net(z.reshape(B * k, D))
        return y.view(B, k, -1)


class TabMHeads(nn.Module):
    def __init__(self, d_in: int, k: int, head_dims: dict[str, int]):
        super().__init__()
        self.k = k
        self.heads = nn.ModuleDict()

        for name, out_dim in head_dims.items():
            if name == "risk_level":
                self.heads[name] = MLPHeadShared(d_in=d_in, out_dim=out_dim, hidden=512, depth=4, dropout=0.1)
            elif name == "stretch_potential_cls":
                self.heads[name] = MLPHeadShared(d_in=d_in, out_dim=out_dim, hidden=512, depth=4, dropout=0.1)
            elif name == "success_cls":
                self.heads[name] = MLPHeadShared(d_in=d_in, out_dim=out_dim, hidden=256, depth=3, dropout=0.1)
            else:
                self.heads[name] = LinearEnsemble(d_in, out_dim, k=k)

    def forward(self, z):
        return {name: head(z) for name, head in self.heads.items()}


class TabMMultiHead(nn.Module):
    def __init__(self, n_num_features, cat_cardinalities, head_dims: dict[str, int],
                 k=8, d_block=256, n_blocks=4, dropout=0.1,
                 start_scaling_init="normal", **kwargs):
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
        self.heads = TabMHeads(d_in=d_block, k=k, head_dims=head_dims)

    def forward(self, x_num, x_cat=None):
        z = self.backbone(x_num, x_cat)  # (B, k, d_block)
        return self.heads(z)


# ===== helper สำหรับ backend =====
def load_model(model_path, device="cpu"):
    checkpoint = torch.load(model_path, map_location=device)
    
    # ถ้าเป็น Full Checkpoint (มี config และ state_dict)
    if isinstance(checkpoint, dict) and "config" in checkpoint and "state_dict" in checkpoint:
        config = checkpoint["config"]
        state_dict = checkpoint["state_dict"]
    else:
        return state_dict

    model = TabMMultiHead(**config).to(device)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def load_model_standard(model_path, n_num_features, cat_cardinalities, head_dims, device="cpu", **kwargs):
    """
    โหลดโมเดลแบบมาตรฐาน (รับโครงสร้างมาด้วย)
    """
    checkpoint = torch.load(model_path, map_location=device)
    
    # Check if this is a training checkpoint with metadata
    if isinstance(checkpoint, dict) and "model" in checkpoint:
        print(f"[INFO] Detected training checkpoint with keys: {checkpoint.keys()}")
        state_dict = checkpoint["model"]
    elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
    else:
        state_dict = checkpoint

    # --- Fix state_dict key mismatch ---
    # Checkpoint has "backbone.blocks..." but model needs "backbone.backbone.blocks..."
    # Checkpoint has "heads.success_cls..." but model needs "heads.heads.success_cls..."
    new_state_dict = {}
    for key, value in state_dict.items():
        new_key = key
        # Fix backbone prefix
        if key.startswith("backbone.") and not key.startswith("backbone.backbone."):
            # Check if model expects backbone.backbone
            new_key = key.replace("backbone.", "backbone.backbone.", 1)
        
        # Fix heads prefix
        if key.startswith("heads.") and not key.startswith("heads.heads."):
             new_key = key.replace("heads.", "heads.heads.", 1)
        
        # Fix LinearEnsemble keys (W -> weight, b -> bias)
        if new_key.endswith(".W"):
            new_key = new_key[:-2] + ".weight"
            # print(f"[DEBUG] Processing {new_key} original_shape={value.shape}")
            
            if len(value.shape) == 3:
                # Heuristic: Checkpoint (8, 4, 256) vs Model (8, 256, 4)
                # If dim1 < dim2 (e.g. 4 < 256), we assume it's (k, out, in) and needs transpose to (k, in, out)
                if value.shape[1] < value.shape[2]:
                    value = value.permute(0, 2, 1)
                    print(f"[DEBUG] Transposed {new_key} to {value.shape} (heuristic: dim1 < dim2)")
                else:
                    print(f"[DEBUG] Skipping transpose for {new_key} shape={value.shape}")
            else:
                pass

        elif new_key.endswith(".b"):
            # print(f"[DEBUG] Renaming {new_key} to {new_key[:-2] + '.bias'}")
            new_key = new_key[:-2] + ".bias"
             
        new_state_dict[new_key] = value
    
    state_dict = new_state_dict
    # -----------------------------------

    model = TabMMultiHead(
        n_num_features=n_num_features,
        cat_cardinalities=cat_cardinalities,
        head_dims=head_dims,
        **kwargs
    ).to(device)
    
    model.load_state_dict(state_dict)
    model.eval()
    return model

