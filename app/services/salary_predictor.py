import logging
import joblib
import yaml

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

ONEHOT_ENCODER = joblib.load("models/onehot_encoder.joblib")
BINARY_ENCODER = joblib.load("models/binary_encoder.joblib")
PREDICT_MODEL = joblib.load("models/catboost_model.joblib")

with open("config/salary_percentiles.yaml", "r", encoding="utf-8") as file:
    PERCENTILES_CONFIG = yaml.safe_load(file)


def build_yoe_label(yoe: int) -> str:
    if yoe < 1:
        return "0"
    elif 1 <= yoe < 3:
        return "1-3"
    elif 3 <= yoe < 6:
        return "3-6"
    else:
        return "6+"


def prepare_data_for_prediction(
    yoe, seniority, work_type, area, best_role, description, tech_stack_embedding
):
    columns = [
        "experience",
        "seniority",
        "work_type",
        "area",
        "best_role",
        "description",
        "tech_stack_embedding",
    ]
    data = [
        build_yoe_label(yoe),
        seniority,
        work_type,
        area,
        best_role,
        description,
        tech_stack_embedding,
    ]

    df = pd.DataFrame([data], columns=columns)

    data_encoded = ONEHOT_ENCODER.transform(
        df[["experience", "seniority", "work_type"]]
    ).toarray()
    feature_names = ONEHOT_ENCODER.get_feature_names_out(
        ["experience", "seniority", "work_type"]
    )
    encoded_df = pd.DataFrame(data_encoded, columns=feature_names, index=df.index)

    binary_encoded = BINARY_ENCODER.transform(df[["area", "best_role"]])
    binary_encoded_df = pd.DataFrame(
        binary_encoded, columns=binary_encoded.columns, index=df.index
    )
    binary_encoded_df.columns = [f"bin_{col}" for col in binary_encoded_df.columns]

    encoded_df = pd.concat(
        [df[["description", "tech_stack_embedding"]], encoded_df, binary_encoded_df],
        axis=1,
    )

    return encoded_df


def predict_salary(encoded_df, role, location, seniority):
    predicted_salary = np.expm1(PREDICT_MODEL.predict(encoded_df))[0]

    role_config = PERCENTILES_CONFIG.get(role, {})
    location_config = role_config.get(location, {})
    seniority_config = location_config.get(seniority, {})

    if seniority_config:
        min_salary = seniority_config.get("percentile_1")
        max_salary = seniority_config.get("percentile_99")

        predicted_salary = np.clip(predicted_salary, min_salary, max_salary)

    predicted_salary = round(predicted_salary / 500) * 500

    return predicted_salary
