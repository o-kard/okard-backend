from fastapi import APIRouter
import torch
import torch.nn.functional as F
from .model import model, preprocess
from .schemas import InputData
from .mapping import OUTPUT_MAPPINGS 
from .model import label_encoders

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("/")
async def predict(data: InputData):
    x_num, x_cat = preprocess(data)

    # print("🔎 DEBUG")
    # print("x_num.shape:", x_num.shape)
    # print("x_cat.shape:", x_cat.shape)
    # print("x_num mean/std:", float(x_num.mean()), float(x_num.std()))
    # print("x_cat values:", x_cat.tolist())

    model.eval()
    with torch.no_grad():
        outputs = model(x_num, x_cat)

    results = {}
    for head, logits in outputs.items():
        print(f"{head} logits shape:", logits.shape)  # (1, k, C)

        probs = F.softmax(logits, dim=-1)
        probs_mean = probs.mean(dim=1)
        pred_class = probs_mean.argmax(dim=-1).item()

        label = OUTPUT_MAPPINGS.get(head, {}).get(pred_class, f"Unknown ({pred_class})")

        results[head] = {
            "pred": pred_class,
            "label": label,
            "confidence": float(probs_mean[0][pred_class]),
            "probs": probs_mean[0].tolist(),
        }

    return results
