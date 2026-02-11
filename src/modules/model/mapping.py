import os, joblib, torch, numpy as np, pandas as pd
import json

BASE_DIR = os.path.dirname(__file__)

# โหลด preprocessors (รวม label_encoders และ scaler)
preprocessors = joblib.load(os.path.join(BASE_DIR, "pkl_files", "preprocessors.pkl"))
label_encoders = preprocessors["label_encoders"]

# ดึง classes ของ category_group ออกมา
category_classes = label_encoders["category_group"].classes_

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