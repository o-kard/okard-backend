import torch.nn.functional as F
from sqlalchemy.orm import Session
from uuid import UUID
import torch
from . import repo, schema, model
from src.modules.model.mapping import OUTPUT_MAPPINGS
from src.modules.model.loader import preprocess
from . import repo, model, loader

async def predict(db: Session, data: schema.InputData, post_id: UUID = None, save: bool = False):
    x_num, x_cat = preprocess(data)
    loader.model.eval()
    with torch.no_grad():
        outputs = loader.model(x_num, x_cat)

    results = {}
    for head, logits in outputs.items():
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

    if save:
        if not post_id:
            raise ValueError("post_id is required to save prediction results.")
        return repo.save_prediction_results(db, post_id, results)
    else:
        return results