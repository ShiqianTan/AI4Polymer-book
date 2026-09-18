#!/usr/bin/env python3
"""Chapter 16 case 3: CO2/CH4 gas separation membrane screening.

Real-data pipeline on a public membrane dataset (778 curated records, MIT
licence, jsunn-y/PolymerGasMembraneML; the underlying measurements are compiled
from the literature with year and condition fields). The script

  1. loads and cleans the records with measured CO2 and CH4 permeability,
  2. builds descriptors and a hashed substructure fingerprint,
  3. splits by publication year (time split) and by monomer family,
  4. trains mean/ridge baselines and tree ensembles for log10 permeability,
  5. calibrates split-conformal intervals,
  6. fits an empirical Robeson reference line from the data,
  7. screens 1,124 held-out structures and reports the funnel,
  8. lists final candidates and the failure stages.

Permeability is reported in Barrer. The single-gas/mixed-gas distinction and all
experimental validation have no labels in this dataset and are reported as not
modelled. No value in this script is fabricated.

Run:  python3 run.py
"""

import csv
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
from stdlib_ml import (  # noqa: E402
    GradientBoosting,
    RandomForest,
    conformal,
    descriptors,
    fingerprint,
    fold_split,
    group_split,
    mae,
    metrics,
    monomer_key,
    parse_smiles,
    random_split,
    ridge_fit,
    predict_linear,
    sha256_file,
    slice_rows,
    standardize,
)

DATA = HERE / "data"
OUT = HERE / "results"
SEED = 42
P_MIN_BARRER = 100.0
ALPHA_MIN = 25.0

DATASETS = {
    "datasetA_imputed_all.csv": (
        "496df857061e09dcaee50c1aaeae931635cc53fe631ae1e040035569df0195b8",
    ),
    "datasetD.csv": (
        "89d12bfc7749437bf818d65f44494c4bb1d9252cce6746188ebf676f1e4742b5",
    ),
}


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_measured(path):
    kept = []
    drops = []
    total = 0
    both_gases = 0
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            total += 1
            co2 = to_float(row["CO2"])
            ch4 = to_float(row["CH4"])
            if co2 is None or ch4 is None:
                drops.append({"reason": "missing_gas"})
                continue
            both_gases += 1
            if co2 <= 0.0 or ch4 <= 0.0:
                drops.append({"reason": "nonpositive_permeability"})
                continue
            try:
                atoms, bonds = parse_smiles(row["Smiles"])
            except Exception:
                drops.append({"reason": "parse_failed", "smiles": row["Smiles"]})
                continue
            if len([a for a in atoms if a.symbol != "*"]) < 3:
                drops.append({"reason": "too_few_atoms"})
                continue
            year = int(row["Year"]) if row["Year"].isdigit() else None
            kept.append(
                {
                    "name": row["Name"],
                    "smiles": row["Smiles"],
                    "condition": row["Condition"],
                    "year": year,
                    "atoms": atoms,
                    "bonds": bonds,
                    "co2": co2,
                    "ch4": ch4,
                    "log_co2": math.log10(co2),
                    "log_ch4": math.log10(ch4),
                    "log_alpha": math.log10(co2 / ch4),
                }
            )
    return total, both_gases, kept, drops


def feature_vector(atoms, bonds):
    return descriptors(atoms, bonds) + [float(v) for v in fingerprint(atoms, bonds, n_bits=128)]


def fit_robeson(points):
    ordered = sorted(points, key=lambda item: (-item["log_alpha"], -item["log_co2"]))
    frontier = []
    best_permeability = -1e18
    for item in ordered:
        if item["log_co2"] > best_permeability:
            frontier.append((item["log_alpha"], item["log_co2"]))
            best_permeability = item["log_co2"]
    bin_points = sorted(frontier)
    n = len(bin_points)
    mean_x = sum(p[0] for p in bin_points) / n
    mean_y = sum(p[1] for p in bin_points) / n
    denominator = sum((p[0] - mean_x) ** 2 for p in bin_points)
    slope = sum((p[0] - mean_x) * (p[1] - mean_y) for p in bin_points) / denominator
    intercept = mean_y - slope * mean_x
    return slope, intercept, bin_points


def main():
    random.seed(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    hashes = {}
    for name, (expected,) in DATASETS.items():
        digest = sha256_file(DATA / name)
        hashes[name] = digest
        if digest != expected:
            print("WARNING: {0} SHA256 differs from the recorded value".format(name))

    total, both_gases, kept, drops = load_measured(DATA / "datasetA_imputed_all.csv")
    print("cleaning: {0} records, {1} with both gases, {2} kept, {3} dropped".format(
        total, both_gases, len(kept), len(drops)))

    rows = []
    for item in kept:
        rows.append(
            {
                "smiles": item["smiles"],
                "year": item["year"],
                "features": feature_vector(item["atoms"], item["bonds"]),
                "group": monomer_key(item["atoms"], item["bonds"]),
                "log_co2": item["log_co2"],
                "log_ch4": item["log_ch4"],
                "log_alpha": item["log_alpha"],
            }
        )
    features = [row["features"] for row in rows]
    groups = [row["group"] for row in rows]
    log_co2 = [row["log_co2"] for row in rows]
    log_ch4 = [row["log_ch4"] for row in rows]
    log_alpha = [row["log_alpha"] for row in rows]

    stats = {
        "records": len(rows),
        "unique_smiles": len(set(row["smiles"] for row in rows)),
        "year_min": min(row["year"] for row in rows if row["year"]),
        "year_max": max(row["year"] for row in rows if row["year"]),
        "co2_barrer_min": min(10 ** v for v in log_co2),
        "co2_barrer_max": max(10 ** v for v in log_co2),
        "log_alpha_mean": sum(log_alpha) / len(log_alpha),
        "measured_above_targets": sum(
            1 for row in rows
            if 10 ** row["log_co2"] > P_MIN_BARRER and 10 ** row["log_alpha"] > ALPHA_MIN
        ),
        "families": len(set(groups)),
    }
    print("dataset: {0} records, {1} unique structures, {2} above both targets".format(
        stats["records"], stats["unique_smiles"], stats["measured_above_targets"]))

    random_idx = random_split(len(rows), 0.2, SEED)
    group_idx = group_split(groups, 0.2, SEED)
    year_train = [i for i, row in enumerate(rows) if row["year"] and row["year"] <= 2000]
    year_test = [i for i, row in enumerate(rows) if row["year"] and row["year"] > 2000]
    split_specs = {
        "random": random_idx,
        "monomer_group": group_idx,
        "time_2000": (year_train, year_test, len(set(groups)), None),
    }

    def train_regressor(train_x, train_y, seed):
        model = GradientBoosting(n_estimators=80, max_depth=3, learning_rate=0.05, min_leaf=8, seed=seed)
        model.fit(train_x, train_y)
        return model

    splits = {}
    for label, (train_idx, test_idx, n_groups, n_test_groups) in split_specs.items():
        train_x = slice_rows(features, train_idx)
        train_y = slice_rows(log_co2, train_idx)
        test_x = slice_rows(features, test_idx)
        test_y = slice_rows(log_co2, test_idx)
        scaled_train, others = standardize(train_x, [test_x])
        scaled_test = others[0]
        mean_prediction = [sum(train_y) / len(train_y)] * len(test_y)
        weights = ridge_fit(scaled_train, train_y, 10.0)
        ridge_prediction = predict_linear(scaled_test, weights, sum(train_y) / len(train_y))
        model = train_regressor(train_x, train_y, SEED)
        model_prediction = model.predict(test_x)
        forest = RandomForest(n_estimators=20, max_depth=8, min_leaf=5, max_features=0.4, seed=SEED)
        forest.fit(train_x, train_y)
        forest_prediction = forest.predict(test_x)
        splits[label] = {
            "train": len(train_idx),
            "test": len(test_idx),
            "groups": n_groups,
            "test_groups": n_test_groups,
            "baseline_mean": metrics(test_y, mean_prediction),
            "ridge": metrics(test_y, ridge_prediction),
            "gradient_boosting": metrics(test_y, model_prediction),
            "random_forest": metrics(test_y, forest_prediction),
        }
        print("{0}: train {1}, test {2}, mean MAE {3:.3f}, ridge {4:.3f}, GB {5:.3f} dex".format(
            label, len(train_idx), len(test_idx),
            splits[label]["baseline_mean"]["mae"], splits[label]["ridge"]["mae"],
            splits[label]["gradient_boosting"]["mae"]))

    primary_train, primary_test = group_idx[0], group_idx[1]
    train_x = slice_rows(features, primary_train)
    train_y = slice_rows(log_co2, primary_train)
    test_x = slice_rows(features, primary_test)
    test_y = slice_rows(log_co2, primary_test)
    train_y_ch4 = slice_rows(log_ch4, primary_train)
    test_y_ch4 = slice_rows(log_ch4, primary_test)

    folds = []
    for fold_train, fold_test in fold_split(len(rows), 5, SEED):
        fx, fy = slice_rows(features, fold_train), slice_rows(log_co2, fold_train)
        tx, ty = slice_rows(features, fold_test), slice_rows(log_co2, fold_test)
        model = train_regressor(fx, fy, SEED)
        folds.append(mae(ty, model.predict(tx)))
    cv_mean = sum(folds) / len(folds)
    cv_std = math.sqrt(sum((v - cv_mean) ** 2 for v in folds) / len(folds))
    print("5-fold CV GB MAE {0:.3f} +/- {1:.3f} dex".format(cv_mean, cv_std))

    def factory():
        return GradientBoosting(n_estimators=80, max_depth=3, learning_rate=0.05, min_leaf=8, seed=SEED)

    uncertainty = conformal(train_x, train_y, test_x, test_y, factory, SEED, alpha=0.10)
    print("conformal 90%: coverage {0:.1f}%, width {1:.3f} dex".format(
        uncertainty["coverage"] * 100.0, uncertainty["mean_width"]))

    co2_model = train_regressor(train_x, train_y, SEED)
    ch4_model = train_regressor(train_x, train_y_ch4, SEED)
    predicted_co2 = co2_model.predict(test_x)
    predicted_ch4 = ch4_model.predict(test_x)
    measured_alpha = [10 ** (a - b) for a, b in zip(test_y, test_y_ch4)]
    predicted_alpha = [10 ** (a - b) for a, b in zip(predicted_co2, predicted_ch4)]
    selectivity_error = [
        abs(math.log10(a) - math.log10(b)) for a, b in zip(predicted_alpha, measured_alpha)
    ]
    print("selectivity: MAE {0:.3f} dex".format(sum(selectivity_error) / len(selectivity_error)))

    slope, intercept, bin_points = fit_robeson(rows)
    print("empirical Robeson line: log10 P = {0:.3f} {1:+.3f} log10 alpha".format(intercept, slope))

    screening = []
    with open(DATA / "datasetD.csv", newline="") as handle:
        for row in csv.DictReader(handle):
            smiles = row["Smiles"]
            try:
                atoms, bonds = parse_smiles(smiles)
            except Exception:
                continue
            if len([a for a in atoms if a.symbol != "*"]) < 3:
                continue
            screening.append({"smiles": smiles, "features": feature_vector(atoms, bonds)})

    screening_x = [row["features"] for row in screening]
    scaled = standardize(train_x, [screening_x])[1][0]
    co2_prediction = co2_model.predict(scaled)
    ch4_prediction = ch4_model.predict(scaled)
    scored = []
    for row, log_p_co2, log_p_ch4 in zip(screening, co2_prediction, ch4_prediction):
        alpha = 10 ** (log_p_co2 - log_p_ch4)
        bound = intercept + slope * (log_p_co2 - log_p_ch4)
        scored.append(
            {
                "smiles": row["smiles"],
                "log_p_co2": log_p_co2,
                "p_co2": 10 ** log_p_co2,
                "alpha": alpha,
                "d": log_p_co2 - bound,
                "interval": uncertainty["mean_width"],
            }
        )
    p_hits = [row for row in scored if row["p_co2"] > P_MIN_BARRER]
    both_hits = [row for row in p_hits if row["alpha"] > ALPHA_MIN]
    above_bound = [row for row in both_hits if row["d"] > 0.0]
    ranked = sorted(p_hits, key=lambda row: (-row["d"], -row["alpha"]))
    top5 = ranked[:5]
    max_alpha = max(row["alpha"] for row in scored)
    alpha_20 = sum(1 for row in scored if row["alpha"] > 20.0)
    print(
        "screening: {0} structures -> {1} P>100 -> {2} alpha>25 -> {3} above bound "
        "(max predicted alpha {4:.1f}, alpha>20 {5})".format(
            len(scored), len(p_hits), len(both_hits), len(above_bound), max_alpha, alpha_20
        )
    )

    failures = {
        "low_permeability": [row for row in scored if row["p_co2"] <= P_MIN_BARRER][:5],
        "low_selectivity": [row for row in p_hits if row["alpha"] <= ALPHA_MIN][:5],
        "below_bound": [row for row in both_hits if row["d"] <= 0.0][:5],
    }

    summary = {
        "seed": SEED,
        "inputs": hashes,
        "dataset": stats,
        "cleaning": {
            "total_records": total,
            "with_both_gases": both_gases,
            "kept": len(rows),
            "dropped": len(drops),
            "drops": drops[:50],
        },
        "splits": splits,
        "cross_validation": {"folds": folds, "mean": cv_mean, "std": cv_std},
        "uncertainty": uncertainty,
        "selectivity_mae_dex": sum(selectivity_error) / len(selectivity_error),
        "robeson": {
            "slope": slope,
            "intercept": intercept,
            "bin_points": bin_points,
            "note": "empirical line fitted to the binned upper envelope of this dataset, not the published Robeson 2008 values",
        },
        "screening": {
            "structures": len(scored),
            "p_co2_pass": len(p_hits),
            "alpha_pass": len(both_hits),
            "above_bound": len(above_bound),
            "max_predicted_alpha": max_alpha,
            "alpha_above_20": alpha_20,
        },
        "measured_above_targets": [
            {
                "name": item["name"],
                "smiles": item["smiles"],
                "co2_barrer": item["co2"],
                "ch4_barrer": item["ch4"],
                "alpha": item["co2"] / item["ch4"],
                "year": item["year"],
            }
            for item in kept
            if item["co2"] > P_MIN_BARRER and item["co2"] / item["ch4"] > ALPHA_MIN
        ],
        "top5": [
            {key: row.get(key) for key in ("smiles", "p_co2", "alpha", "d")}
            for row in top5
        ],
        "failures": {
            key: [
                {k: row.get(k) for k in ("smiles", "p_co2", "alpha", "d")}
                for row in value
            ]
            for key, value in failures.items()
        },
        "not_modelled": [
            "mixed-gas selectivity (only single-gas labels)",
            "experimental validation (no synthesis in this book)",
            "high-pressure conditions (pressure is not a feature)",
        ],
    }

    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    columns = ["smiles", "p_co2", "alpha", "d", "interval"]
    with open(OUT / "top5.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in top5:
            writer.writerow({key: row.get(key, "") for key in columns})
    with open(OUT / "candidates.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in ranked:
            writer.writerow({key: row.get(key, "") for key in columns})

    manifest = {"seed": SEED, "inputs": hashes, "outputs": {}}
    for name in ("summary.json", "top5.csv", "candidates.csv"):
        manifest["outputs"][name] = sha256_file(OUT / name)
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    print("top 5 candidates:")
    for row in top5:
        print("  P(CO2) {0:8.1f} Barrer  alpha {1:6.1f}  d {2:+.3f}  {3}".format(
            row["p_co2"], row["alpha"], row["d"], row["smiles"][:44]))
    print("results written to " + str(OUT))


if __name__ == "__main__":
    main()
