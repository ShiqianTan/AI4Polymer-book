#!/usr/bin/env python3
"""Chapter 16 case 2: recyclable vitrimer chemistry screening.

Real-data pipeline on a public vitrimer dataset: 8,424 acid x epoxide
chemistries whose glass transition temperature was computed by high-throughput
molecular dynamics and calibrated to experiment with a Gaussian process
(Zheng et al., VitrimerVAE, MIT licence). The script

  1. loads and cleans the dataset,
  2. builds interpretable descriptors for the two monomers,
  3. splits by epoxide family (group split) and at random,
  4. trains mean/ridge baselines and tree ensembles,
  5. calibrates split-conformal intervals,
  6. enumerates new acid x epoxide pairs and screens them,
  7. ranks and lists final candidates,
  8. validates the label source against 295 measured polymer Tg values.

Only the Python standard library is used. The depolymerization temperature,
modulus and recovery rate have no labels in the source data and are therefore
reported as not modelled; the dynamic-bond and Tg-window filters are declared
proxies, not measured targets. No value in this script is fabricated.

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
TARGET_TG_K = 373.15
TG_WINDOW = (350.0, 420.0)
DENSITY_MIN = 0.08

DATASETS = {
    "tg_vitrimer_calibrated.csv": (
        "3b79d4902ad85366e79721be777c109687ebee0c1f6c901e881dfe4765e6dd4b",
        "acid,epoxide,tg",
    ),
    "tg_calibration.csv": (
        "18ac296b6cc11dc9702597c4570491b86b76a0955340c26855bbda6b5282e301",
        "name,smiles,tg_exp,tg_md,std",
    ),
    "vitrimervae_bo_search1.csv": (
        "2c1af6a92cbd50e1785b75d6cec31d503a7b0b3fd9e498d340017e43b5ae8942",
        "acid,epoxide,pca1,pca2,dist,tg",
    ),
}

OXIRANE = "C1OC1"


def load_vitrimers(path):
    kept = []
    drops = []
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                tg = float(row["tg"])
            except (TypeError, ValueError):
                drops.append({"reason": "missing_tg"})
                continue
            try:
                acid = parse_smiles(row["acid"])
                epoxide = parse_smiles(row["epoxide"])
            except Exception:
                drops.append({"reason": "parse_failed", "acid": row["acid"]})
                continue
            if not (200.0 <= tg <= 700.0):
                drops.append({"reason": "tg_out_of_range", "tg": tg})
                continue
            if len(acid[0]) < 3 or len(epoxide[0]) < 3:
                drops.append({"reason": "too_few_atoms"})
                continue
            kept.append(
                {
                    "acid": row["acid"],
                    "epoxide": row["epoxide"],
                    "tg": tg,
                    "acid_atoms": acid[0],
                    "acid_bonds": acid[1],
                    "epoxide_atoms": epoxide[0],
                    "epoxide_bonds": epoxide[1],
                }
            )
    return kept, drops


def features_for(acid_atoms, acid_bonds, epoxide_atoms, epoxide_bonds):
    return descriptors(acid_atoms, acid_bonds) + descriptors(epoxide_atoms, epoxide_bonds)


def count_oxirane(atoms, bonds):
    total = 0
    for i, atom in enumerate(atoms):
        if atom.symbol != "O":
            continue
        carbons = [j for j in bonds[i] if atoms[j].symbol == "C"]
        if len(carbons) != 2:
            continue
        a, b = carbons
        if b in bonds[a]:
            total += 1
    return total


def main():
    random.seed(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    hashes = {}
    for name, (expected, _) in DATASETS.items():
        digest = sha256_file(DATA / name)
        hashes[name] = digest
        if digest != expected:
            print("WARNING: {0} SHA256 differs from the recorded value".format(name))

    kept, drops = load_vitrimers(DATA / "tg_vitrimer_calibrated.csv")
    print("cleaning: {0} kept, {1} dropped".format(len(kept), len(drops)))

    rows = []
    for item in kept:
        rows.append(
            {
                "acid": item["acid"],
                "epoxide": item["epoxide"],
                "tg": item["tg"],
                "features": features_for(
                    item["acid_atoms"], item["acid_bonds"],
                    item["epoxide_atoms"], item["epoxide_bonds"],
                ),
                "epoxide_group": monomer_key(item["epoxide_atoms"], item["epoxide_bonds"]),
                "acid_group": monomer_key(item["acid_atoms"], item["acid_bonds"]),
            }
        )
    values = [row["tg"] for row in rows]
    features = [row["features"] for row in rows]
    epoxide_groups = [row["epoxide_group"] for row in rows]

    stats = {
        "records": len(rows),
        "unique_acid": len(set(row["acid"] for row in rows)),
        "unique_epoxide": len(set(row["epoxide"] for row in rows)),
        "tg_min": min(values),
        "tg_max": max(values),
        "tg_mean": sum(values) / len(values),
        "tg_std": math.sqrt(sum((v - sum(values) / len(values)) ** 2 for v in values) / len(values)),
        "epoxide_families": len(set(epoxide_groups)),
        "acid_families": len(set(row["acid_group"] for row in rows)),
    }
    print("dataset: {0} rows, {1} acid / {2} epoxide monomers, Tg {3:.1f}-{4:.1f} K".format(
        stats["records"], stats["unique_acid"], stats["unique_epoxide"],
        stats["tg_min"], stats["tg_max"]))

    random_idx = random_split(len(rows), 0.2, SEED)
    group_idx = group_split(epoxide_groups, 0.2, SEED)
    splits = {}
    for label, (train_idx, test_idx, groups, test_groups) in (
        ("random", random_idx), ("epoxide_group", group_idx)
    ):
        train_x = slice_rows(features, train_idx)
        train_y = slice_rows(values, train_idx)
        test_x = slice_rows(features, test_idx)
        test_y = slice_rows(values, test_idx)
        scaled_train, others = standardize(train_x, [test_x])
        scaled_test = others[0]
        mean_prediction = [sum(train_y) / len(train_y)] * len(test_y)
        weights = ridge_fit(scaled_train, train_y, 10.0)
        ridge_prediction = predict_linear(scaled_test, weights, sum(train_y) / len(train_y))
        splits[label] = {
            "train": len(train_idx),
            "test": len(test_idx),
            "groups": groups,
            "test_groups": test_groups,
            "overlap": 0 if label == "epoxide_group" else None,
            "baseline_mean": metrics(test_y, mean_prediction),
            "ridge": metrics(test_y, ridge_prediction),
        }
        print("{0}: train {1}, test {2}, mean MAE {3:.2f}, ridge MAE {4:.2f}".format(
            label, len(train_idx), len(test_idx),
            splits[label]["baseline_mean"]["mae"], splits[label]["ridge"]["mae"]))

    train_idx, test_idx = group_idx[0], group_idx[1]
    train_x, train_y = slice_rows(features, train_idx), slice_rows(values, train_idx)
    test_x, test_y = slice_rows(features, test_idx), slice_rows(values, test_idx)

    forest = RandomForest(n_estimators=20, max_depth=8, min_leaf=10, max_features=0.4, seed=SEED)
    forest.fit(train_x, train_y)
    forest_prediction = forest.predict(test_x)
    boosting = GradientBoosting(n_estimators=80, max_depth=3, learning_rate=0.05, min_leaf=12, seed=SEED)
    boosting.fit(train_x, train_y)
    boosting_prediction = boosting.predict(test_x)
    splits["epoxide_group"]["random_forest"] = metrics(test_y, forest_prediction)
    splits["epoxide_group"]["gradient_boosting"] = metrics(test_y, boosting_prediction)
    splits["epoxide_group"]["random_forest"]["ensemble_std_mean"] = (
        sum(forest.predict_std(test_x)) / len(test_x)
    )
    print("group split: RF MAE {0:.2f}, GB MAE {1:.2f}".format(
        splits["epoxide_group"]["random_forest"]["mae"],
        splits["epoxide_group"]["gradient_boosting"]["mae"]))

    folds = []
    for fold_train, fold_test in fold_split(len(rows), 5, SEED):
        fx, fy = slice_rows(features, fold_train), slice_rows(values, fold_train)
        tx, ty = slice_rows(features, fold_test), slice_rows(values, fold_test)
        model = GradientBoosting(n_estimators=80, max_depth=3, learning_rate=0.05, min_leaf=12, seed=SEED)
        model.fit(fx, fy)
        folds.append(mae(ty, model.predict(tx)))
    cv_mean = sum(folds) / len(folds)
    cv_std = math.sqrt(sum((v - cv_mean) ** 2 for v in folds) / len(folds))
    print("5-fold CV GB MAE {0:.2f} +/- {1:.2f} K".format(cv_mean, cv_std))

    def factory():
        return GradientBoosting(n_estimators=80, max_depth=3, learning_rate=0.05, min_leaf=12, seed=SEED)

    uncertainty = conformal(train_x, train_y, test_x, test_y, factory, SEED, alpha=0.10)
    print("conformal 90%: coverage {0:.1f}%, width {1:.1f} K".format(
        uncertainty["coverage"] * 100.0, uncertainty["mean_width"]))

    acid_counts = {}
    epoxide_counts = {}
    for row in rows:
        acid_counts[row["acid"]] = acid_counts.get(row["acid"], 0) + 1
        epoxide_counts[row["epoxide"]] = epoxide_counts.get(row["epoxide"], 0) + 1
    top_acids = [s for s, _ in sorted(acid_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:60]]
    top_epoxides = [s for s, _ in sorted(epoxide_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:60]]
    known = set((row["acid"], row["epoxide"]) for row in rows)

    enumeration = []
    for acid in top_acids:
        for epoxide in top_epoxides:
            enumeration.append((acid, epoxide))
    new_pairs = [pair for pair in enumeration if pair not in known]
    print("enumeration: {0} acid x epoxide pairs, {1} not in the dataset".format(
        len(enumeration), len(new_pairs)))

    model = GradientBoosting(n_estimators=80, max_depth=3, learning_rate=0.05, min_leaf=12, seed=SEED)
    model.fit(train_x, train_y)

    scored = []
    build_failures = 0
    for acid, epoxide in new_pairs:
        try:
            acid_atoms, acid_bonds = parse_smiles(acid)
            epoxide_atoms, epoxide_bonds = parse_smiles(epoxide)
        except Exception:
            build_failures += 1
            continue
        feat = features_for(acid_atoms, acid_bonds, epoxide_atoms, epoxide_bonds)
        oxirane = count_oxirane(epoxide_atoms, epoxide_bonds)
        dynamic_ok = oxirane >= 1 and feat[21] >= 1
        network_ok = oxirane >= 2 or feat[21] >= 2
        dynamic_density = (feat[21] + oxirane + feat[22]) / max(feat[0] + feat[24], 1)
        scored.append(
            {
                "acid": acid,
                "epoxide": epoxide,
                "features": feat,
                "oxirane": oxirane,
                "carboxyl": feat[21],
                "dynamic_ok": dynamic_ok,
                "network_ok": network_ok,
                "dynamic_density": dynamic_density,
            }
        )
    dynamic_hits = [row for row in scored if row["dynamic_ok"]]
    network_hits = [row for row in dynamic_hits if row["network_ok"]]
    if network_hits:
        scaled = standardize(train_x, [[row["features"] for row in network_hits]])[1][0]
        predictions = model.predict(scaled)
        for row, predicted in zip(network_hits, predictions):
            row["predicted_tg"] = predicted
    window_hits = [
        row for row in network_hits if TG_WINDOW[0] <= row["predicted_tg"] <= TG_WINDOW[1]
    ]
    density_hits = [row for row in window_hits if row["dynamic_density"] >= DENSITY_MIN]
    ranked = sorted(
        density_hits,
        key=lambda row: (-row["dynamic_density"], abs(row["predicted_tg"] - TARGET_TG_K)),
    )
    top5 = ranked[:5]
    print(
        "funnel: {0} enumerated -> {1} built -> {2} dynamic-bond -> {3} network -> "
        "{4} in Tg window -> {5} density pass".format(
            len(new_pairs), len(scored), len(dynamic_hits), len(network_hits),
            len(window_hits), len(density_hits)
        )
    )

    external = []
    with open(DATA / "tg_calibration.csv", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                exp = float(row["tg_exp"])
                md = float(row["tg_md"])
            except (TypeError, ValueError):
                continue
            external.append({"name": row["name"], "tg_exp": exp, "tg_md": md})
    external_mae = mae([r["tg_exp"] for r in external], [r["tg_md"] for r in external])
    external_bias = sum(r["tg_md"] - r["tg_exp"] for r in external) / len(external)
    print("external calibration set: {0} polymers, MD vs experiment MAE {1:.1f} K, bias {2:+.1f} K".format(
        len(external), external_mae, external_bias))

    search_candidates = []
    with open(DATA / "vitrimervae_bo_search1.csv", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                search_candidates.append(
                    {"acid": row["acid"], "epoxide": row["epoxide"], "tg": float(row["tg"])}
                )
            except (TypeError, ValueError):
                continue
    search_scored = []
    for row in search_candidates:
        acid_atoms, acid_bonds = parse_smiles(row["acid"])
        epoxide_atoms, epoxide_bonds = parse_smiles(row["epoxide"])
        feat = features_for(acid_atoms, acid_bonds, epoxide_atoms, epoxide_bonds)
        search_scored.append(feat)
    search_prediction = model.predict(standardize(train_x, [search_scored])[1][0])
    search_errors = [
        abs(pred - row["tg"]) for pred, row in zip(search_prediction, search_candidates)
    ]
    search_mae = sum(search_errors) / len(search_errors)

    summary = {
        "seed": SEED,
        "inputs": hashes,
        "dataset": stats,
        "cleaning": {"kept": len(rows), "dropped": len(drops), "drops": drops[:50]},
        "splits": splits,
        "cross_validation": {"folds": folds, "mean": cv_mean, "std": cv_std},
        "uncertainty": uncertainty,
        "enumeration": {
            "acid_pool": len(top_acids),
            "epoxide_pool": len(top_epoxides),
            "pairs": len(enumeration),
            "new_pairs": len(new_pairs),
            "build_failures": build_failures,
        },
        "funnel": {
            "enumerated": len(new_pairs),
            "built": len(scored),
            "dynamic_bond_pass": len(dynamic_hits),
            "network_pass": len(network_hits),
            "tg_window_pass": len(window_hits),
            "density_pass": len(density_hits),
        },
        "failure_examples": {
            "no_dynamic_bond": [
                {"acid": row["acid"], "epoxide": row["epoxide"],
                 "oxirane": row["oxirane"], "carboxyl": row["carboxyl"]}
                for row in scored if not row["dynamic_ok"]
            ][:5],
            "not_network": [
                {"acid": row["acid"], "epoxide": row["epoxide"],
                 "oxirane": row["oxirane"], "carboxyl": row["carboxyl"]}
                for row in dynamic_hits if not row["network_ok"]
            ][:5],
            "tg_out_of_window": [
                {"acid": row["acid"], "epoxide": row["epoxide"],
                 "predicted_tg": row.get("predicted_tg")}
                for row in network_hits if not (TG_WINDOW[0] <= row.get("predicted_tg", 0) <= TG_WINDOW[1])
            ][:5],
            "low_density": [
                {"acid": row["acid"], "epoxide": row["epoxide"],
                 "predicted_tg": row.get("predicted_tg"), "dynamic_density": row["dynamic_density"]}
                for row in window_hits if row["dynamic_density"] < DENSITY_MIN
            ][:5],
        },
        "top5": [
            {key: row.get(key) for key in ("acid", "epoxide", "predicted_tg", "dynamic_density")}
            for row in top5
        ],
        "external_calibration": {
            "records": len(external),
            "mae_md_vs_exp": external_mae,
            "bias_md_vs_exp": external_bias,
        },
        "bo_search_cross_check": {
            "records": len(search_candidates),
            "mae_vs_paper_tg": search_mae,
        },
        "not_modelled": [
            "depolymerization temperature (no labels)",
            "modulus (no labels)",
            "recovery rate (no labels)",
        ],
    }

    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    columns = [
        "acid", "epoxide", "predicted_tg", "dynamic_density",
    ]
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

    print("top 5 candidates (target Tg {0:.1f} K):".format(TARGET_TG_K))
    for row in top5:
        print("  Tg {0:6.1f} K  density {1:.3f}  acid {2}".format(
            row["predicted_tg"], row["dynamic_density"], row["acid"][:40]))
    print("results written to " + str(OUT))


if __name__ == "__main__":
    main()
