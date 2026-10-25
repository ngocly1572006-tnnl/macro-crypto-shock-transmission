"""Smoke tests for committed Macro–Crypto data and model outputs.

Run from the repository root:
    python -m pytest tests/test_pipeline.py -v

These tests validate committed artifacts and internal consistency. They do NOT
retrain models, reproduce source downloads, or prove the dashboard's UI is correct.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "outputs" / "model_results"
TABLES = ROOT / "outputs" / "tables"

ASSETS = {"BTC", "ETH"}
SHOCKS = {"US2Y", "DXY", "VIX"}


def csv(path):
    assert path.is_file(), f"Thiếu file: {path.relative_to(ROOT)}"
    df = pd.read_csv(path, encoding="utf-8-sig")
    assert not df.empty, f"File rỗng: {path.relative_to(ROOT)}"
    assert df.columns.is_unique, f"Cột bị trùng: {path.relative_to(ROOT)}"
    return df


def require(df, columns):
    missing = set(columns) - set(df.columns)
    assert not missing, f"Thiếu cột: {sorted(missing)}"


def dates(df, column="date"):
    require(df, [column])
    result = pd.to_datetime(df[column], errors="coerce")
    assert result.notna().all(), f"Ngày không hợp lệ ở {column}"
    return result


def test_required_artifacts_exist():
    paths = [
        PROCESSED / "model_dataset.csv",
        PROCESSED / "ml_dataset.csv",
        TABLES / "descriptive_stats.csv",
        TABLES / "correlation_matrix.csv",
        RESULTS / "lp_results.csv",
        RESULTS / "lp_fdr.csv",
        RESULTS / "irf_results.csv",
        RESULTS / "subperiod_results.csv",
        RESULTS / "subperiod_difference_fdr.csv",
        RESULTS / "regime_results.csv",
        RESULTS / "regime_difference_fdr.csv",
        RESULTS / "model_comparison.csv",
        RESULTS / "forecast_results.csv",
        RESULTS / "forecast_significance.csv",
        ROOT / "dashboard" / "12_dashboard_app.py",
        ROOT / "config" / "research_config.json",
    ]
    missing = [str(p.relative_to(ROOT)) for p in paths if not p.is_file()]
    assert not missing, f"Thiếu artifact: {missing}"


def test_model_dataset_dates_are_unique_and_daily():
    df = csv(PROCESSED / "model_dataset.csv")
    d = dates(df)
    assert d.is_unique, "Ngày bị trùng trong model_dataset"
    assert d.is_monotonic_increasing, "Ngày chưa sắp xếp tăng dần"
    assert d.iloc[0] == pd.Timestamp("2018-01-01")
    assert d.iloc[-1] == pd.Timestamp("2025-12-31")
    assert (d.diff().dropna() == pd.Timedelta(days=1)).all()


def test_model_dataset_core_schema_and_returns():
    df = csv(PROCESSED / "model_dataset.csv")
    require(df, ["BTC", "ETH", "US2Y", "DXY", "VIX",
                 "BTC_log_return_pct", "ETH_log_return_pct",
                 "US2Y_change_pp", "DXY_log_return_pct", "VIX_change_points"])
    for asset in ASSETS:
        assert (df[asset].dropna() > 0).all(), f"Giá {asset} không dương"
        returns = df[f"{asset}_log_return_pct"]
        assert pd.to_numeric(returns, errors="coerce").notna().sum() > 0
        assert np.isfinite(returns.dropna().to_numpy(dtype=float)).all()


def test_macro_missing_values_and_observation_flags():
    df = csv(PROCESSED / "model_dataset.csv")
    for shock in SHOCKS:
        flag = f"{shock}_observed"
        require(df, [flag, f"{shock}_observation_gap_days"])
        observed = pd.to_numeric(df[flag], errors="coerce")
        assert observed.isin([0, 1]).all(), f"Flag {flag} phải là 0/1"
        assert (df.loc[observed.eq(0), shock].isna()).all(), (
            f"{shock} có dữ liệu tại ngày không có quan sát"
        )
        gaps = pd.to_numeric(df[f"{shock}_observation_gap_days"], errors="coerce").dropna()
        assert (gaps > 0).all(), f"Khoảng cách quan sát {shock} phải dương"


def test_ml_dataset_dates_and_next_day_target():
    df = csv(PROCESSED / "ml_dataset.csv")
    d = dates(df)
    require(df, ["target_date"])
    target_dates = pd.to_datetime(df["target_date"], errors="coerce")
    assert d.is_unique and d.is_monotonic_increasing
    valid = target_dates.notna()
    assert valid.sum() == len(df) - 1, "Chỉ ngày cuối được thiếu target_date"
    assert not valid.iloc[-1]
    assert (target_dates[valid] == d[valid] + pd.Timedelta(days=1)).all()
    for asset in ASSETS:
        col = f"{asset}_target_nextday_abs_pct"
        require(df, [col])
        target = pd.to_numeric(df[col], errors="coerce").dropna()
        assert len(target) > 0 and (target >= 0).all()


def test_lp_schema_and_horizon_units():
    df = csv(RESULTS / "lp_results.csv")
    require(df, ["response", "shock", "horizon", "estimate", "ci_lower",
                 "ci_upper", "p_value", "horizon_unit"])
    assert set(df["response"]).issubset(ASSETS)
    assert set(df["shock"]).issubset(SHOCKS)
    assert df["horizon"].between(0, 30).all()
    assert df["horizon_unit"].eq("calendar_days").all()
    assert df["p_value"].between(0, 1).all()
    assert (df["ci_lower"] <= df["estimate"]).all()
    assert (df["estimate"] <= df["ci_upper"]).all()


def test_lp_fdr_preserves_original_estimates():
    base = csv(RESULTS / "lp_results.csv")
    fdr = csv(RESULTS / "lp_fdr.csv")
    keys = ["response", "shock", "horizon"]
    require(fdr, keys + ["estimate", "p_value", "p_value_fdr",
                         "significant_fdr_5pct"])
    assert not base.duplicated(keys).any()
    assert not fdr.duplicated(keys).any()
    joined = base[keys + ["estimate", "p_value"]].merge(
        fdr[keys + ["estimate", "p_value"]], on=keys, how="outer",
        validate="one_to_one", suffixes=("_base", "_fdr"), indicator=True)
    assert joined["_merge"].eq("both").all()
    assert np.allclose(joined["estimate_base"], joined["estimate_fdr"],
                       rtol=1e-9, atol=1e-9)
    assert np.allclose(joined["p_value_base"], joined["p_value_fdr"],
                       rtol=1e-9, atol=1e-9)
    assert fdr["p_value_fdr"].between(0, 1).all()
    assert (fdr["significant_fdr_5pct"].astype(str).str.lower().eq("true")
            == fdr["p_value_fdr"].le(0.05)).all()


def test_irf_horizon_is_macro_sessions_not_calendar_days():
    df = csv(RESULTS / "irf_results.csv")
    require(df, ["response", "shock", "horizon", "estimate", "horizon_unit"])
    assert set(df["response"]).issubset(ASSETS)
    assert set(df["shock"]).issubset(SHOCKS)
    assert df["horizon"].ge(0).all()
    assert df["horizon_unit"].eq("macro_trading_observations").all(), (
        "VAR/IRF dùng phiên vĩ mô, không được ghi thành ngày lịch"
    )


def test_subperiod_results_have_expected_labels():
    df = csv(RESULTS / "subperiod_results.csv")
    require(df, ["response", "shock", "period", "horizon", "estimate"])
    assert set(df["period"]) == {"pre_2020", "post_2020"}
    assert set(df["response"]).issubset(ASSETS)


def test_subperiod_difference_fdr_values():
    df = csv(RESULTS / "subperiod_difference_fdr.csv")
    require(df, ["response", "shock", "horizon", "pre_beta", "post_beta",
                 "difference", "difference_p_value", "p_value_fdr"])
    assert df["difference_p_value"].between(0, 1).all()
    assert df["p_value_fdr"].between(0, 1).all()
    assert np.allclose(df["post_beta"] - df["pre_beta"],
                       df["difference"], atol=1e-7, rtol=1e-7)


def test_regime_results_use_defined_threshold():
    df = csv(RESULTS / "regime_results.csv")
    require(df, ["response", "shock", "regime", "horizon",
                 "stress_threshold", "stress_definition", "n_regime"])
    assert set(df["regime"]) == {"Calm", "Stress"}
    assert df["stress_threshold"].eq(30).all()
    assert df["stress_definition"].eq("previous_macro_session_vix").all()
    assert (df["n_regime"] > 0).all()


def test_regime_difference_fdr_values():
    df = csv(RESULTS / "regime_difference_fdr.csv")
    require(df, ["response", "shock", "horizon", "difference_p_value",
                 "p_value_fdr"])
    assert df["difference_p_value"].between(0, 1).all()
    assert df["p_value_fdr"].between(0, 1).all()


def test_forecast_is_out_of_sample_2025():
    df = csv(RESULTS / "forecast_results.csv")
    require(df, ["date", "origin_date", "asset", "actual", "predicted",
                 "split", "model", "feature_set"])
    d = dates(df)
    origin = dates(df, "origin_date")
    assert d.between("2025-01-01", "2025-12-31").all()
    assert (origin < d).all(), "Ngày phát dự báo phải trước ngày mục tiêu"
    assert df["split"].eq("test").all()
    assert set(df["asset"]) == ASSETS
    assert df["actual"].ge(0).all()
    assert df["predicted"].ge(0).all()
    assert np.isfinite(df[["actual", "predicted"]].to_numpy(dtype=float)).all()
    for _, part in df.groupby(["asset", "model", "feature_set"]):
        assert len(part) == 365
        assert dates(part).is_unique


def test_model_comparison_metrics_match_forecasts():
    forecasts = csv(RESULTS / "forecast_results.csv")
    comparison = csv(RESULTS / "model_comparison.csv")
    require(comparison, ["asset", "model", "feature_set", "metric",
                         "value", "n_obs"])
    assert comparison["metric"].isin(["MAE", "RMSE"]).all()
    assert (comparison["value"] >= 0).all()
    for row in comparison.itertuples(index=False):
        part = forecasts.loc[
            (forecasts["asset"] == row.asset)
            & (forecasts["model"] == row.model)
            & (forecasts["feature_set"] == row.feature_set)
        ]
        assert len(part) == row.n_obs, (row.asset, row.model, row.feature_set)
        errors = part["actual"].to_numpy() - part["predicted"].to_numpy()
        expected = (np.abs(errors).mean() if row.metric == "MAE"
                    else np.sqrt(np.mean(errors ** 2)))
        assert np.isclose(expected, row.value, atol=2e-4, rtol=1e-5), (
            f"Sai {row.metric}: {row.asset}/{row.model}/{row.feature_set}"
        )


def test_forecast_significance_intervals():
    df = csv(RESULTS / "forecast_significance.csv")
    require(df, ["asset", "mae_reduction", "ci95_lower", "ci95_upper",
                 "n_obs", "block_days", "bootstrap_reps", "ci_excludes_zero"])
    assert df["n_obs"].eq(365).all()
    assert df["block_days"].gt(0).all()
    assert df["bootstrap_reps"].gt(0).all()
    assert (df["ci95_lower"] <= df["ci95_upper"]).all()
    expected = (df["ci95_lower"] > 0) | (df["ci95_upper"] < 0)
    actual = df["ci_excludes_zero"].astype(str).str.lower().eq("true")
    assert (expected == actual).all()

