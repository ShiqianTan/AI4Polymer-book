#!/usr/bin/env python3
"""Chapter 16 flagship case: high-Tg transparent polyimide screening.

Real-data pipeline: load a public measured-Tg dataset, clean it, split by
structural scaffold to avoid leakage, train three baselines and a main model,
fit a learning curve, calibrate uncertainty, enumerate polyimide candidates
from a curated monomer library, screen them, and validate against published
measurements.

Run:  python3 run.py
"""

import csv
import hashlib
import json
import math
import random
import sys
import urllib.request
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*encountered in matmul.*")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
SEED = 42
TARGET_TG_K = 473.15
TARGET_TRANSMITTANCE_PCT = 85.0
TEST_FRACTION = 0.2
CONFORMAL_ALPHA = 0.10

DATASET_NAME = "polymer-tg-dataset.csv"
DATASET_URL = (
    "https://raw.githubusercontent.com/chem-data-extraction/"
    "polymer-Tg-prediction-dataset/main/data/processed/dataset.csv"
)
DATASET_LICENSE = "CC BY 4.0"
DATASET_ACCESSED = "2026-09-17"
DATASET_SHA256 = "c7de4f6e26a321319ada13ed682fd75ea615c72192a2be6a2eef9ccb2df704d0"


def fail(message, code=2):
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(code)


try:
    import numpy as np
except ImportError:
    fail("numpy is required. Install with: pip install numpy")

try:
    from rdkit import Chem, DataStructs, RDLogger
    from rdkit.Chem import AllChem, RDConfig
    from rdkit.Chem.Scaffolds import MurckoScaffold

    RDLogger.DisableLog("rdApp.*")
except ImportError:
    fail("RDKit is required. Install with: pip install rdkit")

try:
    from sklearn.ensemble import (
        HistGradientBoostingRegressor,
        RandomForestRegressor,
    )
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import GroupKFold, GroupShuffleSplit
except ImportError:
    fail("scikit-learn is required. Install with: pip install scikit-learn")

sys.path.append(str(Path(RDConfig.RDContribDir) / "SA_Score"))
try:
    import sascorer

    HAVE_SA = True
except Exception:
    HAVE_SA = False


# --------------------------------------------------------------------------
# Curated monomer library
# --------------------------------------------------------------------------

DIANHYDRIDES = {
    "PMDA": "O=C1OC(=O)c2cc3c(cc21)C(=O)OC3=O",
    "BPDA": "O=C1OC(=O)c2cc(-c3ccc4c(c3)C(=O)OC4=O)ccc21",
    "ODPA": "O=C1OC(=O)c2cc(Oc3ccc4c(c3)C(=O)OC4=O)ccc21",
    "BTDA": "O=C1OC(=O)c2cc(C(=O)c3ccc4c(c3)C(=O)OC4=O)ccc21",
    "6FDA": "O=C1OC(=O)c2cc(C(c3ccc4c(c3)C(=O)OC4=O)(C(F)(F)F)C(F)(F)F)ccc21",
    "DSDA": "O=C1OC(=O)c2cc(S(=O)(=O)c3ccc4c(c3)C(=O)OC4=O)ccc21",
    "HPMDA": "O=C1OC(=O)C2CC3C(=O)OC(=O)C3CC12",
    "BCDA": "O=C1OC(=O)C2C1C3C=CC2C(=O)OC3=O",
    "CBDA": "O=C1OC(=O)C2C1C1C(=O)OC(=O)C21",
    "BPADA": "CC(C)(c1ccc(Oc2ccc3c(c2)C(=O)OC3=O)cc1)c1ccc(Oc2ccc3c(c2)C(=O)OC3=O)cc1",
    "HQDPA": "O=C1OC(=O)c2cc(Oc3ccc(Oc4ccc5c(c4)C(=O)OC5=O)cc3)ccc21",
    "NTDA": "O=C1OC(=O)c2ccc3c4c(ccc(c24)C(=O)OC3=O)C1=O",
}

DIAMINES = {
    "ODA": "Nc1ccc(Oc2ccc(N)cc2)cc1",
    "PDA": "Nc1ccc(N)cc1",
    "mPDA": "Nc1cccc(N)c1",
    "MDA": "Nc1ccc(Cc2ccc(N)cc2)cc1",
    "TFMB": "Nc1ccc(-c2ccc(N)cc2C(F)(F)F)c(C(F)(F)F)c1",
    "BAPS": "Nc1ccc(S(=O)(=O)c2ccc(N)cc2)cc1",
    "DDS33": "Nc1cccc(S(=O)(=O)c2cccc(N)c2)c1",
    "BAPP": "Nc1ccc(C(C)(C)c2ccc(N)cc2)cc1",
    "6FpDA": "Nc1ccc(C(c2ccc(N)cc2)(C(F)(F)F)C(F)(F)F)cc1",
    "APB": "Nc1cccc(Oc2cccc(Oc3cccc(N)c3)c2)c1",
    "TPEQ": "Nc1ccc(Oc2ccc(Oc3ccc(N)cc3)cc2)cc1",
    "BAPB": "Nc1ccc(Oc2ccc(-c3ccc(Oc4ccc(N)cc4)cc3)cc2)cc1",
    "DMB": "Nc1ccc(-c2ccc(N)cc2C)cc1C",
    "TMB": "Nc1cc(C)c(-c2cc(C)c(N)cc2C)c(C)c1",
    "SDA": "Nc1ccc(Sc2ccc(N)cc2)cc1",
    "CHDA": "N[C@H]1CC[C@@H](N)CC1",
    "XYL": "NCc1ccc(CN)cc1",
    "BAPF": "Nc1ccc(C2(c3ccc(N)cc3)c3ccccc3-c3ccccc32)cc1",
    "TPM": "Nc1ccc(C(c2ccccc2)c2ccc(N)cc2)cc1",
    "DABA": "Nc1ccc(NC(=O)c2ccc(N)cc2)cc1",
    "FDAADA": "Nc1ccc(C(=O)Nc2ccc(C3(c4ccc(NC(=O)c5ccc(N)cc5)cc4)c4ccccc4-c4ccccc43)cc2)cc1",
    "ABTFMB": "Nc1ccc(C(=O)Nc2ccc(-c3ccc(NC(=O)c4ccc(N)cc4)cc3C(F)(F)F)c(C(F)(F)F)c2)cc1",
    "MABTFMB": "Cc1cc(NC(=O)c2ccc(N)cc2)ccc1-c1ccc(NC(=O)c2ccc(N)cc2)cc1C",
}

CONFLICT_DIAMINES = {
    "DABA_acid": "Nc1cc(N)cc(C(=O)O)c1",
    "DAP": "Nc1ccc(O)c(N)c1",
    "DADS": "Nc1ccc(SSc2ccc(N)cc2)cc1",
}

LITERATURE = [
    {
        "name": "PI-ref1 (6FDA-FDAADA)",
        "dianhydride": "6FDA",
        "diamine": "FDAADA",
        "tg_c": 401.3,
        "method": "DMA",
        "doi": "10.3390/polym15173549",
    },
    {
        "name": "PI-ref2 (6FDA-ABTFMB)",
        "dianhydride": "6FDA",
        "diamine": "ABTFMB",
        "tg_c": 376.3,
        "method": "DMA",
        "doi": "10.3390/polym15173549",
    },
    {
        "name": "PI-ref3 (6FDA-MABTFMB)",
        "dianhydride": "6FDA",
        "diamine": "MABTFMB",
        "tg_c": 381.4,
        "method": "DMA",
        "doi": "10.3390/polym15173549",
    },
]


# --------------------------------------------------------------------------
# Input acquisition and hashing
# --------------------------------------------------------------------------


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_dataset():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / DATASET_NAME
    if path.is_file():
        return path
    print("dataset missing, downloading from " + DATASET_URL)
    try:
        with urllib.request.urlopen(DATASET_URL, timeout=120) as response:
            payload = response.read()
    except Exception as exc:
        fail("could not download dataset ({0}). Place it at {1}".format(exc, path))
    path.write_bytes(payload)
    return path


# --------------------------------------------------------------------------
# Structure handling
# --------------------------------------------------------------------------


def is_carbonyl_carbon(atom):
    for bond in atom.GetBonds():
        if bond.GetBondType() == Chem.BondType.DOUBLE:
            if bond.GetOtherAtom(atom).GetSymbol() == "O":
                return True
    return False


def anhydride_oxygen_pairs(mol):
    pairs = []
    for atom in mol.GetAtoms():
        if atom.GetSymbol() != "O" or atom.GetDegree() != 2 or not atom.IsInRing():
            continue
        neighbours = [n.GetIdx() for n in atom.GetNeighbors()]
        if all(is_carbonyl_carbon(mol.GetAtomWithIdx(i)) for i in neighbours):
            pairs.append((atom.GetIdx(), neighbours[0], neighbours[1]))
    return pairs


def close_repeat_unit(psmiles):
    mol = Chem.MolFromSmiles(psmiles.replace("[*]", "*"))
    if mol is None:
        return None, "unparsable"
    dummies = [a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum() == 0]
    if len(dummies) != 2:
        return None, "attachment_points={0}".format(len(dummies))
    first = [n.GetIdx() for n in mol.GetAtomWithIdx(dummies[0]).GetNeighbors()]
    second = [n.GetIdx() for n in mol.GetAtomWithIdx(dummies[1]).GetNeighbors()]
    if not first or not second:
        return None, "dangling_attachment"
    editable = Chem.RWMol(mol)
    if editable.GetBondBetweenAtoms(first[0], second[0]) is None:
        editable.AddBond(first[0], second[0], Chem.BondType.SINGLE)
    for index in sorted(dummies, reverse=True):
        editable.RemoveAtom(index)
    try:
        closed = editable.GetMol()
        Chem.SanitizeMol(closed)
    except Exception as exc:
        return None, "sanitize:" + str(exc)[:40]
    return closed, "ok"


def build_repeat_unit(dianhydride_smiles, diamine_smiles):
    anhydride = Chem.MolFromSmiles(dianhydride_smiles)
    diamine = Chem.MolFromSmiles(diamine_smiles)
    if anhydride is None or diamine is None:
        return None, "monomer_unparsable"
    pairs = anhydride_oxygen_pairs(anhydride)
    if len(pairs) != 2:
        return None, "anhydride_groups={0}".format(len(pairs))
    amines = [
        a.GetIdx()
        for a in diamine.GetAtoms()
        if a.GetSymbol() == "N" and a.GetTotalNumHs() == 2 and a.GetDegree() == 1
    ]
    if len(amines) != 2:
        return None, "primary_amines={0}".format(len(amines))
    combined = Chem.CombineMols(anhydride, diamine)
    editable = Chem.RWMol(combined)
    offset = anhydride.GetNumAtoms()
    for (_, carbon_a, carbon_b), amine in zip(pairs, amines):
        editable.AddBond(carbon_a, amine + offset, Chem.BondType.SINGLE)
        editable.AddBond(carbon_b, amine + offset, Chem.BondType.SINGLE)
    for oxygen, _, _ in sorted(pairs, key=lambda item: -item[0]):
        editable.RemoveAtom(oxygen)
    try:
        repeat = editable.GetMol()
        Chem.SanitizeMol(repeat)
    except Exception as exc:
        return None, "sanitize:" + str(exc)[:40]
    return repeat, "ok"


def morgan(mol, n_bits=2048, radius=2):
    return AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)


def fingerprint_matrix(bit_vectors):
    return np.vstack(
        [np.array(bit_vector, dtype=np.float64) for bit_vector in bit_vectors]
    )


def scaffold(mol):
    return MurckoScaffold.MurckoScaffoldSmiles(mol=mol)


# --------------------------------------------------------------------------
# Structural screening functions
# --------------------------------------------------------------------------


def count_cf3(mol):
    total = 0
    for atom in mol.GetAtoms():
        if atom.GetSymbol() != "C":
            continue
        fluorines = sum(1 for n in atom.GetNeighbors() if n.GetSymbol() == "F")
        if fluorines == 3:
            total += 1
    return total


def ring_partition(mol):
    aromatic = []
    aliphatic = []
    for ring in mol.GetRingInfo().AtomRings():
        atoms = [mol.GetAtomWithIdx(i) for i in ring]
        if all(atom.GetSymbol() == "C" and atom.GetIsAromatic() for atom in atoms):
            aromatic.append(ring)
        elif all(atom.GetSymbol() == "C" and not atom.GetIsAromatic() for atom in atoms):
            aliphatic.append(ring)
    return aromatic, aliphatic


def count_fused_aromatic(aromatic_rings):
    fused = 0
    for i in range(len(aromatic_rings)):
        for j in range(i + 1, len(aromatic_rings)):
            if len(set(aromatic_rings[i]) & set(aromatic_rings[j])) >= 2:
                fused += 1
    return fused


def count_substructure(mol, pattern):
    query = Chem.MolFromSmarts(pattern)
    return len(mol.GetSubstructMatches(query))


def ct_complex_risk(mol):
    aromatic_rings, aliphatic_rings = ring_partition(mol)
    n_aromatic = len(aromatic_rings)
    n_fused = count_fused_aromatic(aromatic_rings)
    n_alicyclic = len(aliphatic_rings)
    n_cf3 = count_cf3(mol)
    n_sulfone = count_substructure(mol, "S(=O)(=O)")
    return (
        n_aromatic
        + 2.0 * n_fused
        - 2.0 * n_cf3
        - 2.0 * n_alicyclic
        - 1.0 * n_sulfone
    )


def monomer_conflicts(smiles):
    issues = []
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return ["unparsable"]
    for atom in mol.GetAtoms():
        if atom.GetSymbol() == "O" and atom.GetTotalNumHs() >= 1:
            if atom.GetDegree() == 1 and atom.GetNeighbors()[0].GetSymbol() == "C":
                carbon = atom.GetNeighbors()[0]
                if any(
                    b.GetBondType() == Chem.BondType.DOUBLE
                    and b.GetOtherAtom(carbon).GetSymbol() == "O"
                    for b in carbon.GetBonds()
                ):
                    issues.append("carboxyl")
                else:
                    issues.append("hydroxyl")
        if atom.GetSymbol() == "S":
            if atom.GetTotalNumHs() >= 1:
                issues.append("thiol")
            if any(n.GetSymbol() == "S" for n in atom.GetNeighbors()):
                issues.append("disulfide")
    return sorted(set(issues))


# --------------------------------------------------------------------------
# Data cleaning
# --------------------------------------------------------------------------


def load_clean_polyimides(path):
    with open(path, newline="") as handle:
        raw = list(csv.DictReader(handle))
    kept = []
    drops = []
    for row in raw:
        if row["polymer_class"] != "polyimide":
            continue
        try:
            value = float(row["tg_value"])
        except ValueError:
            drops.append({"record_id": row["record_id"], "reason": "missing_tg"})
            continue
        if row["tg_unit"] == "C":
            value = value + 273.15
        if not (100.0 <= value <= 900.0):
            drops.append({"record_id": row["record_id"], "reason": "tg_out_of_range"})
            continue
        closed, status = close_repeat_unit(row["repeat_unit_smiles"])
        if closed is None:
            drops.append(
                {"record_id": row["record_id"], "reason": "structure:" + status}
            )
            continue
        kept.append(
            {
                "record_id": row["record_id"],
                "tg_k": value,
                "mol": closed,
                "canonical": Chem.MolToSmiles(closed),
                "scaffold": scaffold(closed),
                "source_id": row["source_id"],
            }
        )
    return len(raw), kept, drops


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------


def mean_baseline(train_y, test_y):
    prediction = np.full(len(test_y), float(np.mean(train_y)))
    return prediction


def train_baselines(train_x, train_y, test_x, test_y):
    report = {}
    mean_prediction = mean_baseline(train_y, test_y)
    report["mean"] = {
        "mae": float(mean_absolute_error(test_y, mean_prediction)),
        "r2": float(r2_score(test_y, mean_prediction)),
    }
    ridge = Ridge(alpha=1.0, random_state=SEED)
    ridge.fit(train_x, train_y)
    ridge_prediction = ridge.predict(test_x)
    report["ridge"] = {
        "mae": float(mean_absolute_error(test_y, ridge_prediction)),
        "r2": float(r2_score(test_y, ridge_prediction)),
    }
    forest = RandomForestRegressor(
        n_estimators=300, random_state=SEED, n_jobs=1, min_samples_leaf=1
    )
    forest.fit(train_x, train_y)
    forest_prediction = forest.predict(test_x)
    report["random_forest"] = {
        "mae": float(mean_absolute_error(test_y, forest_prediction)),
        "r2": float(r2_score(test_y, forest_prediction)),
    }
    return report, forest


def train_main(train_x, train_y):
    model = HistGradientBoostingRegressor(
        random_state=SEED, max_iter=400, learning_rate=0.06, max_leaf_nodes=31
    )
    model.fit(train_x, train_y)
    return model


def grouped_cross_validation(fingerprints, values, groups, n_splits=5):
    fold_splitter = GroupKFold(n_splits=n_splits)
    scores = {"mean": [], "ridge": [], "random_forest": [], "main": []}
    for train_idx, test_idx in fold_splitter.split(fingerprints, values, groups):
        train_x, test_x = fingerprints[train_idx], fingerprints[test_idx]
        train_y, test_y = values[train_idx], values[test_idx]
        scores["mean"].append(
            mean_absolute_error(test_y, np.full(len(test_y), train_y.mean()))
        )
        ridge = Ridge(alpha=1.0, random_state=SEED).fit(train_x, train_y)
        scores["ridge"].append(mean_absolute_error(test_y, ridge.predict(test_x)))
        forest = RandomForestRegressor(
            n_estimators=200, random_state=SEED, n_jobs=1
        ).fit(train_x, train_y)
        scores["random_forest"].append(
            mean_absolute_error(test_y, forest.predict(test_x))
        )
        main = train_main(train_x, train_y)
        scores["main"].append(mean_absolute_error(test_y, main.predict(test_x)))
    return {
        name: {
            "mae_mean": round(float(np.mean(values_)), 6),
            "mae_std": round(float(np.std(values_)), 6),
        }
        for name, values_ in scores.items()
    }


# --------------------------------------------------------------------------
# Learning curve
# --------------------------------------------------------------------------


def fit_power_law(sizes, errors, mae_inf_grid):
    sizes = np.array(sizes, dtype=float)
    errors = np.array(errors, dtype=float)
    log_sizes = np.log(sizes)
    best = None
    for mae_inf in mae_inf_grid:
        if mae_inf >= errors.min():
            continue
        log_residual = np.log(errors - mae_inf)
        slope, intercept = np.polyfit(log_sizes, log_residual, 1)
        alpha = -float(slope)
        a = float(np.exp(intercept))
        if alpha <= 0.0 or a <= 0.0:
            continue
        predicted = mae_inf + a * sizes ** (-alpha)
        rss = float(np.sum((errors - predicted) ** 2))
        if best is None or rss < best["rss"]:
            best = {
                "alpha": alpha,
                "mae_inf": float(mae_inf),
                "a": a,
                "rss": rss,
            }
    if best is None:
        return None
    total = float(np.sum((errors - errors.mean()) ** 2))
    best["fit_r2"] = 1.0 - best["rss"] / total if total > 0 else 0.0
    targets = {}
    for target in (35.0, 30.0, 25.0):
        if target > best["mae_inf"]:
            required = (best["a"] / (target - best["mae_inf"])) ** (1.0 / best["alpha"])
            targets["{0:.0f}K".format(target)] = float(math.ceil(required))
        else:
            targets["{0:.0f}K".format(target)] = None
    best["required_n"] = targets
    return best


def learning_curve(train_x, train_y, test_x, test_y, sizes):
    curve = []
    for size in sizes:
        if size > len(train_y):
            continue
        rng = random.Random(SEED)
        indices = list(range(len(train_y)))
        rng.shuffle(indices)
        subset = indices[:size]
        model = train_main(train_x[subset], train_y[subset])
        prediction = model.predict(test_x)
        curve.append(
            {
                "n": size,
                "mae": float(mean_absolute_error(test_y, prediction)),
                "r2": float(r2_score(test_y, prediction)),
            }
        )
    maes = [c["mae"] for c in curve]
    grid = [round(k * 0.5, 1) for k in range(0, int(min(maes)) * 2)]
    fit = fit_power_law([c["n"] for c in curve], maes, grid)
    return curve, fit


# --------------------------------------------------------------------------
# Uncertainty
# --------------------------------------------------------------------------


def conformal(train_x, train_y, test_x, test_y, alphas):
    rng = random.Random(SEED)
    indices = list(range(len(train_y)))
    rng.shuffle(indices)
    split = int(len(indices) * 0.8)
    fit_idx = indices[:split]
    cal_idx = indices[split:]
    model = train_main(train_x[fit_idx], train_y[fit_idx])
    calibration = np.abs(train_y[cal_idx] - model.predict(train_x[cal_idx]))
    test_prediction = model.predict(test_x)
    levels = []
    for alpha in alphas:
        quantile = float(np.quantile(calibration, 1.0 - alpha))
        lower = test_prediction - quantile
        upper = test_prediction + quantile
        levels.append(
            {
                "alpha": alpha,
                "nominal_coverage": 1.0 - alpha,
                "quantile_k": quantile,
                "coverage": float(np.mean((test_y >= lower) & (test_y <= upper))),
                "mean_width_k": float(np.mean(upper - lower)),
            }
        )
    model.fit(train_x, train_y)
    primary = levels[0]
    return {
        "levels": levels,
        "quantile_k": primary["quantile_k"],
        "coverage": primary["coverage"],
        "mean_width_k": primary["mean_width_k"],
        "model": model,
    }


def forest_uncertainty(forest, test_x):
    predictions = np.vstack([tree.predict(test_x) for tree in forest.estimators_])
    return predictions.std(axis=0)


# --------------------------------------------------------------------------
# Candidate enumeration and screening
# --------------------------------------------------------------------------


def enumerate_candidates():
    candidates = []
    for diamine_name, diamine_smiles in DIAMINES.items():
        for dianhydride_name, dianhydride_smiles in DIANHYDRIDES.items():
            repeat, status = build_repeat_unit(dianhydride_smiles, diamine_smiles)
            candidates.append(
                {
                    "dianhydride": dianhydride_name,
                    "diamine": diamine_name,
                    "diamine_smiles": diamine_smiles,
                    "repeat": repeat,
                    "build_status": status,
                }
            )
    for diamine_name, diamine_smiles in CONFLICT_DIAMINES.items():
        for dianhydride_name, dianhydride_smiles in DIANHYDRIDES.items():
            repeat, status = build_repeat_unit(dianhydride_smiles, diamine_smiles)
            candidates.append(
                {
                    "dianhydride": dianhydride_name,
                    "diamine": diamine_name,
                    "diamine_smiles": diamine_smiles,
                    "repeat": repeat,
                    "build_status": status,
                }
            )
    return candidates


def synthesizability(dianhydride_name, diamine_smiles, repeat_mol):
    issues = []
    for label, smiles in (
        ("dianhydride", DIANHYDRIDES[dianhydride_name]),
        ("diamine", diamine_smiles),
    ):
        for problem in monomer_conflicts(smiles):
            issues.append(label + ":" + problem)
        if HAVE_SA:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None and sascorer.calculateScore(mol) > 4.5:
                issues.append(label + ":sa_score>4.5")
    if repeat_mol is not None and repeat_mol.GetNumHeavyAtoms() > 120:
        issues.append("repeat_unit:heavy_atoms>120")
    return sorted(set(issues))


def screen_candidates(candidates, model, train_fingerprints, conformal_width):
    scored = []
    for item in candidates:
        repeat = item["repeat"]
        if repeat is None:
            scored.append(
                {
                    "dianhydride": item["dianhydride"],
                    "diamine": item["diamine"],
                    "build_status": item["build_status"],
                    "pass": False,
                    "reason": "build_failed",
                }
            )
            continue
        bit_vector = morgan(repeat)
        features = np.array(bit_vector, dtype=np.float64).reshape(1, -1)
        predicted = float(model.predict(features)[0])
        risk = ct_complex_risk(repeat)
        issues = synthesizability(item["dianhydride"], item["diamine_smiles"], repeat)
        similarity = float(
            max(DataStructs.BulkTanimotoSimilarity(bit_vector, train_fingerprints))
        )
        scored.append(
            {
                "dianhydride": item["dianhydride"],
                "diamine": item["diamine"],
                "build_status": item["build_status"],
                "smiles": Chem.MolToSmiles(repeat),
                "predicted_tg_k": predicted,
                "predicted_tg_c": predicted - 273.15,
                "interval_k": conformal_width,
                "ct_risk": risk,
                "transparent_proxy": risk <= 1.0,
                "synthesizable": not issues,
                "synth_issues": ";".join(issues),
                "max_train_tanimoto": similarity,
                "novel": similarity < 0.99,
                "pass": True,
            }
        )
    return scored


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in columns})


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    dataset_path = ensure_dataset()
    dataset_sha = sha256_file(dataset_path)
    if dataset_sha != DATASET_SHA256:
        print("WARNING: dataset SHA256 differs from the recorded value")

    total_rows, kept, drops = load_clean_polyimides(dataset_path)
    print(
        "cleaning: {0} polyimide rows kept, {1} dropped (of {2} total records)".format(
            len(kept), len(drops), total_rows
        )
    )

    mols = [row["mol"] for row in kept]
    values = np.array([row["tg_k"] for row in kept], dtype=float)
    groups = np.array([row["scaffold"] for row in kept])
    train_fingerprints = [morgan(mol) for mol in mols]
    fingerprints = fingerprint_matrix(train_fingerprints)

    splitter = GroupShuffleSplit(n_splits=1, test_size=TEST_FRACTION, random_state=SEED)
    train_idx, test_idx = next(splitter.split(fingerprints, values, groups))
    train_x, test_x = fingerprints[train_idx], fingerprints[test_idx]
    train_y, test_y = values[train_idx], values[test_idx]
    print(
        "split: train {0}, test {1}, scaffold overlap {2}".format(
            len(train_idx),
            len(test_idx),
            len(set(groups[train_idx]) & set(groups[test_idx])),
        )
    )

    baselines, forest = train_baselines(train_x, train_y, test_x, test_y)
    main_model = train_main(train_x, train_y)
    main_prediction = main_model.predict(test_x)
    main_metrics = {
        "mae": float(mean_absolute_error(test_y, main_prediction)),
        "r2": float(r2_score(test_y, main_prediction)),
    }
    forest_std = forest_uncertainty(forest, test_x)
    cross_validation = grouped_cross_validation(fingerprints, values, groups)
    print(
        "models: mean MAE {0:.2f} | ridge {1:.2f} | rf {2:.2f} | main {3:.2f}".format(
            baselines["mean"]["mae"],
            baselines["ridge"]["mae"],
            baselines["random_forest"]["mae"],
            main_metrics["mae"],
        )
    )
    print(
        "grouped 5-fold CV: main MAE {0:.2f} +/- {1:.2f} K".format(
            cross_validation["main"]["mae_mean"],
            cross_validation["main"]["mae_std"],
        )
    )

    sizes = [20, 50, 100, 200, 400, 700, 1000, 1400]
    curve, fit = learning_curve(train_x, train_y, test_x, test_y, sizes)
    print(
        "learning curve: MAE_inf {0:.2f} K, A {1:.1f}, alpha {2:.3f}, fit R2 {3:.3f}".format(
            fit["mae_inf"], fit["a"], fit["alpha"], fit["fit_r2"]
        )
    )

    conformal_result = conformal(
        train_x, train_y, test_x, test_y, [CONFORMAL_ALPHA, 0.20]
    )
    print(
        "uncertainty: conformal nominal {0:.0f}% -> achieved {1:.0f}%, width {2:.1f} K".format(
            conformal_result["levels"][0]["nominal_coverage"] * 100.0,
            conformal_result["coverage"] * 100.0,
            conformal_result["mean_width_k"],
        )
    )

    candidates = enumerate_candidates()
    scored = screen_candidates(
        candidates,
        main_model,
        train_fingerprints,
        conformal_result["mean_width_k"],
    )

    valid = [row for row in scored if row.get("pass")]
    tg_hits = [row for row in valid if row["predicted_tg_k"] >= TARGET_TG_K]
    transparent_hits = [row for row in tg_hits if row["transparent_proxy"]]
    synth_hits = [row for row in transparent_hits if row["synthesizable"]]
    ranked = sorted(synth_hits, key=lambda row: -row["predicted_tg_k"])
    top20 = ranked[:20]
    diverse = []
    seen = set()
    for row in ranked:
        key = row["smiles"]
        if key in seen:
            continue
        seen.add(key)
        diverse.append(row)
    top5 = diverse[:5]
    top5_novel = [row for row in diverse if row["novel"]][:5]

    print(
        "funnel: {0} enumerated -> {1} built -> {2} Tg>={3:.0f} K -> "
        "{4} transparent -> {5} synthesizable".format(
            len(scored),
            len(valid),
            TARGET_TG_K,
            len(tg_hits),
            len(transparent_hits),
            len(synth_hits),
        )
    )

    literature_validation = []
    for entry in LITERATURE:
        repeat, status = build_repeat_unit(
            DIANHYDRIDES[entry["dianhydride"]], DIAMINES[entry["diamine"]]
        )
        if repeat is None:
            literature_validation.append(
                {
                    "name": entry["name"],
                    "status": status,
                    "measured_tg_k": entry["tg_c"] + 273.15,
                }
            )
            continue
        bit_vector = morgan(repeat)
        features = np.array(bit_vector, dtype=np.float64).reshape(1, -1)
        predicted = float(main_model.predict(features)[0])
        similarity = float(
            max(DataStructs.BulkTanimotoSimilarity(bit_vector, train_fingerprints))
        )
        literature_validation.append(
            {
                "name": entry["name"],
                "dianhydride": entry["dianhydride"],
                "diamine": entry["diamine"],
                "measured_tg_c": entry["tg_c"],
                "measured_tg_k": entry["tg_c"] + 273.15,
                "predicted_tg_k": predicted,
                "error_k": predicted - (entry["tg_c"] + 273.15),
                "interval_k": conformal_result["mean_width_k"],
                "in_interval": abs(predicted - (entry["tg_c"] + 273.15))
                <= conformal_result["mean_width_k"] / 2.0,
                "max_train_tanimoto": similarity,
                "method": entry["method"],
                "doi": entry["doi"],
            }
        )

    summary = {
        "seed": SEED,
        "dataset": {
            "file": DATASET_NAME,
            "url": DATASET_URL,
            "license": DATASET_LICENSE,
            "accessed": DATASET_ACCESSED,
            "sha256": dataset_sha,
            "total_records": total_rows,
            "polyimide_records": len(kept) + len(drops),
            "kept": len(kept),
            "dropped": len(drops),
        },
        "dataset_statistics": {
            "tg_k_min": float(values.min()),
            "tg_k_max": float(values.max()),
            "tg_k_mean": float(values.mean()),
            "tg_k_std": float(values.std()),
            "tg_k_median": float(np.median(values)),
            "above_target": int((values >= TARGET_TG_K).sum()),
        },
        "split": {
            "method": "GroupShuffleSplit by Bemis-Murcko scaffold",
            "test_fraction": TEST_FRACTION,
            "train": len(train_idx),
            "test": len(test_idx),
            "unique_scaffolds": len(set(groups)),
            "scaffold_overlap": len(set(groups[train_idx]) & set(groups[test_idx])),
        },
        "targets": {
            "tg_k": TARGET_TG_K,
            "transmittance_pct": TARGET_TRANSMITTANCE_PCT,
            "transmittance_note": "no transmittance labels; ct_risk proxy used",
        },
        "models": {
            "baselines": baselines,
            "main": dict(main_metrics, name="HistGradientBoostingRegressor"),
            "grouped_5fold_cv": cross_validation,
        },
        "learning_curve": {"curve": curve, "fit": fit},
        "uncertainty": {
            "levels": conformal_result["levels"],
            "quantile_k": conformal_result["quantile_k"],
            "coverage": conformal_result["coverage"],
            "mean_width_k": conformal_result["mean_width_k"],
            "test_forest_std_mean_k": float(np.mean(forest_std)),
        },
        "funnel": {
            "enumerated": len(scored),
            "built": len(valid),
            "tg_pass": len(tg_hits),
            "transparent_pass": len(transparent_hits),
            "synthesizable_pass": len(synth_hits),
        },
        "top20": top20,
        "top5": top5,
        "top5_novel": top5_novel,
        "literature_validation": literature_validation,
    }

    (RESULTS_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    )
    (RESULTS_DIR / "cleaning_drops.json").write_text(
        json.dumps(drops, ensure_ascii=False, indent=2) + "\n"
    )
    (RESULTS_DIR / "failures.json").write_text(
        json.dumps(
            {
                "build_failures": [
                    row for row in scored if not row.get("pass")
                ],
                "tg_failures": [
                    row for row in valid if row["predicted_tg_k"] < TARGET_TG_K
                ],
                "transparency_failures": [
                    row for row in tg_hits if not row["transparent_proxy"]
                ],
                "synthesizability_failures": [
                    row for row in transparent_hits if not row["synthesizable"]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )

    candidate_columns = [
        "dianhydride",
        "diamine",
        "build_status",
        "smiles",
        "predicted_tg_k",
        "predicted_tg_c",
        "interval_k",
        "ct_risk",
        "transparent_proxy",
        "synthesizable",
        "synth_issues",
        "max_train_tanimoto",
        "novel",
    ]
    write_csv(RESULTS_DIR / "candidates.csv", valid, candidate_columns)
    write_csv(RESULTS_DIR / "top20.csv", top20, candidate_columns)
    write_csv(RESULTS_DIR / "top5.csv", top5, candidate_columns)

    manifest = {
        "seed": SEED,
        "inputs": {DATASET_NAME: dataset_sha},
        "outputs": {},
    }
    for name in (
        "summary.json",
        "cleaning_drops.json",
        "failures.json",
        "candidates.csv",
        "top20.csv",
        "top5.csv",
    ):
        manifest["outputs"][name] = sha256_file(RESULTS_DIR / name)
    (RESULTS_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    )

    print("top 5 candidates:")
    for row in top5:
        print(
            "  {0:6s}-{1:8s} Tg {2:6.1f} K ({3:6.1f} C) risk {4:+.1f} "
            "tanimoto {5:.2f} novel {6}".format(
                row["dianhydride"],
                row["diamine"],
                row["predicted_tg_k"],
                row["predicted_tg_c"],
                row["ct_risk"],
                row["max_train_tanimoto"],
                row["novel"],
            )
        )
    print("results written to " + str(RESULTS_DIR))


if __name__ == "__main__":
    main()
