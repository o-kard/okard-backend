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

    print("\n🔮 === MODEL PREDICTION RESULT ===")
    for head, res in results.items():
        print(f"{head}: {res['label']} ({res['confidence']:.2%}) - Probs: {[round(p, 4) for p in res['probs']]}")
    print("==================================\n")


    # Rule-based Post-Processing
    from datetime import datetime
    try:
        start = datetime.fromisoformat(data.start_date)
        end = datetime.fromisoformat(data.end_date)
        duration = (end - start).days
        
        # กฎข้อ 1: ขาดสื่ออธิบายแบบไดนามิก และตั้งเวลานานเผื่อฟลุค 
        if getattr(data, "has_video", 1) == 0 and duration >= 45:
            results["risk_level"]["pred"] = 2
            results["risk_level"]["label"] = "High Risk"
            results["risk_level"]["confidence"] = 0.90
                
        # กฎข้อ 2: หาเงินเยอะเวอร์ในเวลาสั้นด่วน
        if duration <= 5 and data.goal >= 5000:
            results["risk_level"]["pred"] = 2
            results["risk_level"]["label"] = "High Risk"
            results["risk_level"]["confidence"] = 0.99
            
        # กฎข้อ 3: โมเดลบอกเจ๊งชัวร์ (Success = Failed แบบมั่นใจมาก)
        success_probs = results.get("success_cls", {}).get("probs", [])
        if len(success_probs) > 0 and success_probs[0] > 0.85:
            # 0 ใน success_cls คือ Failed
            results["risk_level"]["pred"] = 2
            results["risk_level"]["label"] = "High Risk"
            results["risk_level"]["confidence"] = max(0.90, success_probs[0])
            
        # กฎข้อ 4: ขอเงินสูงปี๊ดแบบไม่มีสื่อ 
        if data.goal >= 50000 and getattr(data, "has_video", 1) == 0:
            results["risk_level"]["pred"] = 2
            results["risk_level"]["label"] = "High Risk"
            results["risk_level"]["confidence"] = 0.95

    except Exception as e:
        pass

    if save:
        if not post_id:
            raise ValueError("post_id is required to save prediction results.")
        return repo.save_prediction_results(db, post_id, results)
    else:
        return results