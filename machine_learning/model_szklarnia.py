import pandas as pd
import glob
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, GridSearchCV, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.svm import SVR
import joblib
from sklearn.metrics import mean_absolute_error
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

pliki = sorted((BASE_DIR / "data").glob("pomiary_TEST*.csv"))
tablica_df =[]

for plik in pliki:
    df_one = pd.read_csv(plik)
    tablica_df.append(df_one)

df = pd.concat(tablica_df, ignore_index=False)

df["czas_pomiaru"] = pd.to_datetime(df["czas_pomiaru"])

df = df.sort_values(["partia_id", "czas_pomiaru"]).reset_index(drop=True)

df["czas_start"] = df.groupby("partia_id")["czas_pomiaru"].transform("min")
df["czas_start_s"] = (df["czas_pomiaru"] - df["czas_start"])
df["czas_start_min"] = df["czas_start_s"].dt.total_seconds() / 60
df["roznica_temp"] = abs(df["temp_gora"] - df["temp_dol"])

df["roznica_temp_diff_gora"] =df.groupby("partia_id")["temp_gora"].diff()
df["roznica_temp_diff_dol"] = df.groupby("partia_id")["temp_dol"].diff()

df["odstep_czasowy"] = df.groupby("partia_id")["czas_pomiaru"].diff().dt.total_seconds()

df["temp_srednia"] = (df["temp_gora"] + df["temp_dol"]) / 2

df["temp_srednia_60_s"] = df.groupby("partia_id")["temp_srednia"].shift(-12)


df = df.dropna(subset = ["roznica_temp_diff_gora", "roznica_temp_diff_dol", "temp_srednia_60_s"])

X= df[[
    "temp_dol",
    "temp_gora",
    "pwm",
    "wentylator",
    "czas_start_min",
    "roznica_temp",
    "roznica_temp_diff_gora",
    "roznica_temp_diff_dol",
    "temp_srednia"
]]

y = df[
    "temp_srednia_60_s"
]

groups = df["partia_id"]

gas = GroupShuffleSplit(
    n_splits=1,
    random_state=42,
    test_size=0.25
)

idx_train, idx_test = next(gas.split(
    X,
    y,
    groups=groups
))

X_train = X.iloc[idx_train]
y_train = y.iloc[idx_train]
X_test = X.iloc[idx_test]
y_test = y.iloc[idx_test]

grupa_trening = groups.iloc[idx_train]
grupa_test = groups.iloc[idx_test]

num_scaler = Pipeline([
    ("scaler", StandardScaler())
])

model_lr = Pipeline([
    ("num", num_scaler),
    ("model", LinearRegression())
])

model_ct = Pipeline([
    ("model", DecisionTreeRegressor(random_state=42))
])

model_rf = Pipeline([
    ("model", RandomForestRegressor(random_state=42))
])

model_knn = Pipeline([
    ("num", num_scaler),
    ("model", KNeighborsRegressor())
])

model_svr = Pipeline([
    ("num", num_scaler),
    ("model", SVR())
])

model_gb = Pipeline([
    ("model", GradientBoostingRegressor(random_state=42))
])

model_xgb = Pipeline([
    ("model", XGBRegressor(random_state=42))
])

modele = {
    "LinearRegression" : model_lr,
    "DecisionTreeRegressor" : model_ct,
    "RandomForestRegressor" : model_rf,
    "KNeighborsRegressor" : model_knn,
    "SVR" : model_svr,
    "GradientBoostingRegressor" : model_gb,
    "XGBRegressor" : model_xgb  
}


cv = GroupKFold(
    n_splits =3
)

model_gb.set_params(
    model__n_estimators=200,
    model__learning_rate=0.05,
    model__max_depth=4,
    model__min_samples_leaf=1,
    model__min_samples_split=2,
    model__subsample=0.5
)

model_xgb.set_params(
    model__colsample_bytree=1.0,
    model__learning_rate=0.2,
    model__max_depth=5,
    model__n_estimators=50,
    model__subsample=1.0
)

cross_gb = cross_val_score(
    model_gb,
    X_train,
    y_train,
    cv = cv,
    scoring="neg_mean_absolute_error",
    groups=grupa_trening
)

cross_xgb = cross_val_score(
    model_xgb,
    X_train,
    y_train,
    cv = cv,
    scoring="neg_mean_absolute_error",
    groups=grupa_trening
)

cross_lr = cross_val_score(
    model_lr,
    X_train,
    y_train,
    cv = cv,
    scoring="neg_mean_absolute_error",
    groups=grupa_trening
)


model_lr.fit(X_train, y_train)

y_pred = model_lr.predict(X_test)

mae_test = mean_absolute_error(y_test, y_pred)

print("MAE na nowych partiach:", mae_test)

model_lr.fit(X, y)

joblib.dump(model_lr, BASE_DIR / "model_lr_60s_final.joblib")

print("Model końcowy zapisany!")
