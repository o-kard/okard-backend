import os, joblib, torch, numpy as np, pandas as pd
import json

BASE_DIR = os.path.dirname(__file__)

# โหลด label_encoders ที่เซฟจาก training
label_encoders = joblib.load(os.path.join(BASE_DIR, "pkl_files", "label_encoders.pkl"))

# ดึง classes ของ category_group ออกมา
category_classes = label_encoders["category_group"].classes_

path = os.path.join("src", "modules", "model", "pkl_files", "recommend_mapping.json")
with open(path, "r", encoding="utf-8") as f:
    recommend_mapping = json.load(f)

# สร้าง mapping auto
OUTPUT_MAPPINGS = {
    "success_cls": {
        0: "Failed",
        1: "Successful",
    },
    "risk_level": {
        0: "Low Risk",
        1: "Medium Risk",
        2: "High Risk",
    },
    "days_to_state_change": {
        0: "≤ 15 days",
        1: "16–30 days",
        2: "31–60 days",
        3: "> 60 days",
    },
    # ใช้ classes จาก encoder โดยตรง
    # "recommend_category": {i: c for i, c in enumerate(category_classes)},
    "recommend_category": {int(k): v for k, v in recommend_mapping.items()},
    "goal_eval": {
        0: "Under Goal",
        1: "Fair Goal",
        2: "Over Goal",
    },
    "stretch_potential_cls": {
        0: "Low Stretch Potential",
        1: "Medium Stretch Potential",
        2: "High Stretch Potential",
    },
}