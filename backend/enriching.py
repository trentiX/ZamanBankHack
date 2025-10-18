import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.impute import SimpleImputer

# === ПУТИ ===
USER_JSON_PATH = "Project/user_full_banking_data_enriched.json"
MODEL_PATH = "Project/spontaneous_model.pkl"
OUTPUT_PATH = "Project/user_full_banking_data_enriched2.json"

# === ЗАГРУЗКА МОДЕЛИ ===
with open(MODEL_PATH, "rb") as f:
    bundle = pickle.load(f)
model = bundle["model"]
imputer = bundle["imputer"]
features = bundle["features"]

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
def prepare_features(transactions, monthly_income):
    if not transactions:
        return pd.DataFrame()

    df = pd.DataFrame(transactions)
    df["day_of_week"] = df["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").weekday())
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["transaction_hour"] = np.random.randint(0, 24, len(df))
    df["amount_normalized"] = df["amount"].abs() / (monthly_income if monthly_income else 1)
    df["merchant_frequency"] = df["merchant"].map(df["merchant"].value_counts())
    df["category_frequency"] = df["category"].map(df["category"].value_counts())

    if "balance_after" in df:
        df["balance_before"] = df["balance_after"] - df["amount"]
    else:
        df["balance_before"] = np.nan

    risky = ["Netflix", "Spotify", "AliExpress", "Burger King"]
    df["is_high_risk_merchant"] = df["merchant"].isin(risky).astype(int)
    df["timestamp"] = pd.to_datetime(df["date"])
    df = df.sort_values("timestamp")
    df["delta_time_previous"] = df["timestamp"].diff().dt.total_seconds() / 3600
    df["delta_time_previous"] = df["delta_time_previous"].fillna(0)
    df["mcc_encoded"] = pd.factorize(df.get("mcc", np.nan))[0]

    for col in features:
        if col not in df.columns:
            df[col] = np.nan
    return df[features]

def predict_spontaneous(transactions, monthly_income):
    if not transactions:
        return []
    X = prepare_features(transactions, monthly_income)
    X_imputed = pd.DataFrame(imputer.transform(X), columns=X.columns)
    preds = model.predict(X_imputed)
    for i, tx in enumerate(transactions):
        tx["is_spontanius_predicted"] = bool(preds[i])
    return transactions

# === ОБРАБОТКА JSON ===
with open(USER_JSON_PATH, "r", encoding="utf-8") as f:
    user_data = json.load(f)

income = user_data.get("monthly_income", 0)

for key in ["transactions1", "transactions2", "transactions3Current"]:
    if key in user_data:
        user_data[key] = predict_spontaneous(user_data[key], income)

# === СОХРАНЕНИЕ ===
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(user_data, f, ensure_ascii=False, indent=2)

print(f"✅ Готово! Файл с метками спонтанных покупок сохранён в: {OUTPUT_PATH}")
