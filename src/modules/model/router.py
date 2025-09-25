from fastapi import APIRouter
import torch
import torch.nn.functional as F
from .model import model, preprocess
from .schemas import InputData

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("/")
async def predict(data: InputData):
    x_num, x_cat = preprocess(data)

    model.eval()
    with torch.no_grad():
        outputs = model(x_num, x_cat)  # dict: head -> (1, k, C)

    results = {}
    for head, logits in outputs.items():
        logits = torch.tensor(logits)  # (1, k, C)
        probs = F.softmax(logits, dim=-1)          # convert to probabilities
        probs_mean = probs.mean(dim=1)             # average across ensemble k
        pred_class = torch.argmax(probs_mean, dim=-1).item()

        results[head] = {
            "probs": probs_mean[0].tolist(),       # list of probabilities
            "pred": pred_class                     # predicted class index
        }

    return results
