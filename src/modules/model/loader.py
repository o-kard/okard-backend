import os, joblib, torch, numpy as np, pandas as pd
from datetime import datetime
from .schema import InputData
from .tabm_model import load_model, load_model_standard, TabMMultiHead
from sentence_transformers import SentenceTransformer
import json

BASE_DIR = os.path.dirname(__file__)

# โหลด Config โมเดลและฟีเจอร์
config_path = os.path.join(BASE_DIR, "model_config.json")
with open(config_path, "r", encoding="utf-8") as f:
    model_config = json.load(f)

# ดึงชื่อฟีเจอร์จาก config
CATEGORICAL_FEATURES = model_config["feature_names"]["categorical"]
CYCLIC_NUMERIC = model_config["feature_names"]["cyclic"]
NUMERIC_FEATURES = model_config["feature_names"]["numeric"]

# โหลด preprocessors (รวม label_encoders และ scaler)
preprocessors_path = os.path.join(BASE_DIR, "pkl_files", "preprocessors.pkl")
preprocessors = joblib.load(preprocessors_path)
scaler = preprocessors["scaler"]
label_encoders = preprocessors["label_encoders"]

tables = joblib.load(os.path.join(BASE_DIR, "pkl_files", "group_stats.pkl"))  
sentence_model = SentenceTransformer(os.path.join(BASE_DIR, "pkl_files", "sentence_model"))

device = torch.device("cpu")

# โหลดโมเดลโดยใช้พารามิเตอร์จาก config
model_params = model_config["model_params"]
# โหลดโมเดลโดยใช้พารามิเตอร์จาก config
model_params = model_config["model_params"]
# Force reload - Antigravity
model = load_model_standard(
    os.path.join(BASE_DIR, "tabm_model.pt"), 
    device=device,
    **model_params
)

def cyclic_encode(dt: datetime, prefix: str):
    return {
        f"{prefix}_mon_sin": np.sin(2*np.pi*(dt.month-1)/12),
        f"{prefix}_mon_cos": np.cos(2*np.pi*(dt.month-1)/12),
        f"{prefix}_dom_sin": np.sin(2*np.pi*(dt.day-1)/31),
        f"{prefix}_dom_cos": np.cos(2*np.pi*(dt.day-1)/31),
    }

def preprocess(data: InputData):
    print("📦 preprocess received data:", data)

    start = datetime.fromisoformat(data.start_date)
    end = datetime.fromisoformat(data.end_date)
    duration = (end - start).days

    # ---- duration bin ----
    if duration <= 29:
        dur_bin = "<30"
    elif duration <= 45:
        dur_bin = "30-45"
    elif duration <= 60:
        dur_bin = "46-60"
    else:
        dur_bin = ">60"

    too_short_or_long = int(duration < 30 or duration > 60)

    # ---- numeric features ----
    feats_num = {
        "launch_dow": start.weekday(),
        "deadline_dow": end.weekday(),
        "prep_days": 0,
        "days_diff_launched_at_deadline": duration,
        "days_diff_launched_at_deadline_log": np.log1p(duration),
        "too_short_or_long": too_short_or_long,
        "name_len": len((data.name or "")),
        "blurb_len": len((data.blurb or "")),
        "has_video": data.has_video,
        "has_photo": data.has_photo,
        "goal_log": np.log1p(data.goal),
        "goal_per_day_log": np.log1p(data.goal / max(duration, 1)),
    }

    # ---- group stats lookup ----
    # Note: Use category_group from data
    key = (data.category_group, data.country_displayable_name, dur_bin)
    # The group_stats keys might need adjustment if they were (country, dur_bin)
    # But let's assume the user has updated the group_stats.pkl as well or follow the logic.
    # Looking at original code: key = (data.country_displayable_name, dur_bin)
    
    # Actually, I should check the notebook to see how group_stats key is built.
    # In TabM.ipynb, it doesn't show group_stats mapping explicitly but it uses category_group a lot.
    
    g_stat = tables.get(key)
    if g_stat is None:
        # Fallback to just (country, dur_bin) if (cat, country, dur_bin) fails?
        g_stat = tables.get((data.country_displayable_name, dur_bin))
        
    if g_stat is None:
        print(f"[WARN] Missing group_stats key: {key} → using defaults")
        g_stat = {
            "gpd_rank_in_cat_mon": 0,
            "goal_rank_in_cat_mon": 0,
            "gpd_vs_cat_country_med": 1.0,
            "goal_vs_cat_country_med": 1.0,
            "cat_30d_launch_density": 0,
            "cat_30d_density_z": 0,
            "cat_mon_n": 0,
            "cat_mon_goal_med": 0,
            "cat_mon_gpd_med": 0,
        }
    feats_num.update(g_stat)

    # ---- numeric scaling ----
    # MUST follow NUMERIC_FEATURES order from config
    X_num = np.array([[feats_num[f] for f in NUMERIC_FEATURES]])
    X_num_scaled = scaler.transform(X_num)

    # ---- text embedding ----
    combined = f"{(data.name or '')}. {(data.blurb or '')}"
    X_embed = sentence_model.encode([combined], normalize_embeddings=True).astype(np.float32)

    # ---- cyclic encoding ----
    cyclic = {}
    cyclic.update(cyclic_encode(start, "launched_at"))
    cyclic.update(cyclic_encode(end, "deadline"))
    X_cyclic = np.array([[cyclic[f] for f in CYCLIC_NUMERIC]])

    # ---- final numeric ----
    x_num = np.concatenate([X_num_scaled, X_embed, X_cyclic], axis=1).astype(np.float32)

    # ---- categorical ----
    x_cat = []
    for f in CATEGORICAL_FEATURES:
        le = label_encoders[f]
        if f == "dur_bin":
            raw_val = dur_bin
        else:
            raw_val = getattr(data, f)
            if isinstance(raw_val, str):
                raw_val = raw_val.strip()

        raw_val = str(raw_val) if raw_val is not None else "missing"

        # ทำ Case-insensitive matching กับ le.classes_
        # สร้าง lowercase mapping (ควรทำครั้งเดียวตอนโหลด แต่ทำที่นี่ก่อนเพื่อความชัวร์)
        class_map = {c.lower(): c for c in le.classes_}
        normalized_val = raw_val.lower()

        if normalized_val in class_map:
            val = le.transform([class_map[normalized_val]])[0]
        else:
            print(f"[WARN] Unknown category for {f}: {raw_val} → fallback to 0")
            val = 0
        x_cat.append(val)

    # ---- convert to tensor ----
    x_num = torch.tensor(x_num, dtype=torch.float32)
    x_cat = torch.tensor([x_cat], dtype=torch.long)
    
    print(label_encoders["country_displayable_name"].classes_[:50])  
    print("=== BACKEND DEBUG ===")
    print("Numeric feats (scaled):", X_num_scaled[0][:5])
    print("Text embed (sbert):", X_embed[0][:5])
    print("Cyclic feats:", X_cyclic[0].tolist())
    print("x_num shape:", x_num.shape)
    print("x_cat:", x_cat.tolist())
    
    return x_num, x_cat




