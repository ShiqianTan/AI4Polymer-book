#!/usr/bin/env python3
"""Chapter 6 property-prediction benchmark on the public polyimide Tg set.

Pure standard library: no numpy, no RDKit, no scikit-learn. The script loads the
measured-Tg dataset used by the chapter 16 flagship case, keeps the polyimide
subset, builds a Morgan-like substructure fingerprint and a small set of
interpretable graph descriptors from the repeat-unit SMILES with its own parser,
then trains six models under five split protocols and five random seeds.

Everything is deterministic: fixed seeds, fixed input SHA256, all outputs
hashed in results/manifest.json.

Run:  python3 run.py
"""

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "experiments/ch16/flagship/data/polymer-tg-dataset.csv"
OUT = Path(__file__).resolve().parent / "results"
SEEDS = [42, 7, 13, 2024, 99]
PRIMARY_SEED = 42
TEST_FRACTION = 0.2
N_BITS = 256
RADIUS = 2
TARGET_TG_K = 473.15

GNN_COST = ROOT / "calculations/results/gnn-forward-4layer.json"

ORGANIC = ["Cl", "Br", "B", "C", "N", "O", "S", "P", "F", "I"]
AROMATIC = {"b", "c", "n", "o", "p", "s"}


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_hash(text, modulus):
    return int(hashlib.blake2b(text.encode("utf-8"), digest_size=8).hexdigest(), 16) % modulus


class Atom:
    __slots__ = ("symbol", "aromatic", "charge", "hydrogens", "ring")

    def __init__(self, symbol, aromatic=False, charge=0, hydrogens=0):
        self.symbol = symbol
        self.aromatic = aromatic
        self.charge = charge
        self.hydrogens = hydrogens
        self.ring = False


def parse_smiles(smiles):
    atoms = []
    bonds = defaultdict(dict)
    stack = []
    rings = {}
    current = None
    pending = None
    i = 0
    n = len(smiles)
    while i < n:
        ch = smiles[i]
        if ch == "[":
            end = smiles.index("]", i)
            token = smiles[i + 1:end]
            i = end + 1
            symbol = ""
            for part in token:
                if part.isalpha():
                    symbol += part
                else:
                    break
            if symbol and symbol[0].islower():
                symbol = symbol.capitalize()
            aromatic = token[: len(symbol)] in AROMATIC or (
                len(symbol) == 1 and symbol.lower() in AROMATIC
            )
            hydrogens = 0
            if "H" in token:
                pos = token.index("H")
                digits = ""
                j = pos + 1
                while j < len(token) and token[j].isdigit():
                    digits += token[j]
                    j += 1
                hydrogens = int(digits) if digits else 1
            charge = 0
            if "+" in token:
                charge = 1
            if "-" in token:
                charge = -1
            atom = Atom(symbol if symbol else "*", aromatic, charge, hydrogens)
        elif ch in "()":
            if ch == "(":
                stack.append(current)
            elif stack:
                current = stack.pop()
            i += 1
            continue
        elif ch.isdigit() or ch == "%":
            if ch == "%":
                label = smiles[i + 1: i + 3]
                i += 3
            else:
                label = ch
                i += 1
            if label in rings:
                other, order = rings.pop(label)
                if order is None:
                    order = 1.5 if (atoms[current].aromatic and atoms[other].aromatic) else 1
                bonds[current][other] = order
                bonds[other][current] = order
                atoms[current].ring = True
                atoms[other].ring = True
            else:
                rings[label] = (current, pending)
                pending = None
            continue
        elif ch in "-=#:/\\":
            if ch == "=":
                pending = 2
            elif ch == "#":
                pending = 3
            elif ch == ":":
                pending = 1.5
            else:
                pending = 1
            i += 1
            continue
        elif ch == ".":
            current = None
            pending = None
            i += 1
            continue
        else:
            symbol = None
            for candidate in ORGANIC:
                if smiles.startswith(candidate, i):
                    symbol = candidate
                    i += len(candidate)
                    break
            if symbol is None:
                symbol = ch
                i += 1
            aromatic = symbol.lower() in AROMATIC and symbol[0].islower()
            if aromatic:
                symbol = symbol.capitalize()
            atom = Atom(symbol, aromatic)
        atoms.append(atom)
        new_index = len(atoms) - 1
        if current is not None:
            order = pending
            if order is None:
                order = 1.5 if (atoms[current].aromatic and atoms[new_index].aromatic) else 1
            bonds[current][new_index] = order
            bonds[new_index][current] = order
        current = new_index
        pending = None
    return atoms, bonds


def prune_scaffold(atoms, bonds):
    degree = {i: len(bonds[i]) for i in range(len(atoms))}
    alive = set(range(len(atoms)))
    changed = True
    while changed:
        changed = False
        for i in list(alive):
            if atoms[i].ring:
                continue
            if degree[i] <= 1:
                alive.discard(i)
                for j in bonds[i]:
                    degree[j] -= 1
                changed = True
    return alive


def neighbourhood_labels(atoms, bonds, radius, target):
    position = {atom: pos for pos, atom in enumerate(target)}
    labels = []
    for i in target:
        atom = atoms[i]
        labels.append(
            "{}|{}|{}|{}".format(atom.symbol, int(atom.aromatic), atom.charge, len(bonds[i]))
        )
    for _ in range(radius):
        updated = []
        for i in target:
            parts = []
            for j, order in bonds[i].items():
                if j in position:
                    parts.append("{}:{}".format(order, labels[position[j]]))
            parts.sort()
            updated.append(labels[position[i]] + "|" + "|".join(parts))
        labels = updated
    return labels


def fingerprint(atoms, bonds, n_bits=N_BITS, radius=RADIUS):
    target = [i for i in range(len(atoms)) if atoms[i].symbol != "*"]
    position = {atom: pos for pos, atom in enumerate(target)}
    counts = [0] * n_bits
    labels = []
    for i in target:
        atom = atoms[i]
        labels.append("{}|{}|{}|{}".format(atom.symbol, int(atom.aromatic), atom.charge, len(bonds[i])))
    for step in range(radius + 1):
        for label in labels:
            counts[stable_hash(label, n_bits)] += 1
        if step == radius:
            break
        updated = []
        for pos, i in enumerate(target):
            parts = []
            for j, order in bonds[i].items():
                if j in position:
                    parts.append("{}:{}".format(order, labels[position[j]]))
            parts.sort()
            updated.append(labels[pos] + "|" + "|".join(parts))
        labels = updated
    return counts


def descriptors(atoms, bonds):
    heavy = [i for i in range(len(atoms)) if atoms[i].symbol != "*"]
    symbols = Counter(atoms[i].symbol for i in heavy)
    aromatic_atoms = sum(1 for i in heavy if atoms[i].aromatic)
    ring_atoms = sum(1 for i in heavy if atoms[i].ring)
    carbonyl = 0
    ether = 0
    sulfone = 0
    cf3 = 0
    imide = 0
    for i in heavy:
        if atoms[i].symbol == "C":
            double_o = sum(1 for j, o in bonds[i].items() if atoms[j].symbol == "O" and o == 2)
            carbonyl += double_o
            fluorines = sum(1 for j, _ in bonds[i].items() if atoms[j].symbol == "F")
            if fluorines == 3:
                cf3 += 1
        if atoms[i].symbol == "O":
            carbons = sum(1 for j, _ in bonds[i].items() if atoms[j].symbol == "C")
            if carbons >= 2 and not any(o == 2 for o in bonds[i].values()):
                ether += 1
        if atoms[i].symbol == "S":
            double_o = sum(1 for j, o in bonds[i].items() if atoms[j].symbol == "O" and o == 2)
            if double_o == 2:
                sulfone += 1
        if atoms[i].symbol == "N":
            carbonyl_neighbours = sum(
                1
                for j in bonds[i]
                if atoms[j].symbol == "C"
                and any(atoms[k].symbol == "O" and o == 2 for k, o in bonds[j].items())
            )
            if carbonyl_neighbours >= 2:
                imide += 1
    single_bonds = 0
    double_bonds = 0
    seen = set()
    for i in heavy:
        for j, order in bonds[i].items():
            if j not in heavy:
                continue
            key = (min(i, j), max(i, j))
            if key in seen:
                continue
            seen.add(key)
            if order == 1:
                single_bonds += 1
            elif order == 2:
                double_bonds += 1
    count = max(len(heavy), 1)
    return [
        len(heavy),
        symbols.get("C", 0),
        symbols.get("N", 0),
        symbols.get("O", 0),
        symbols.get("F", 0),
        symbols.get("S", 0),
        symbols.get("Si", 0),
        len(heavy) - sum(symbols.get(s, 0) for s in ("C", "N", "O", "F", "S", "Si")),
        ring_atoms,
        aromatic_atoms,
        cf3,
        carbonyl,
        ether,
        sulfone,
        imide,
        double_bonds,
        single_bonds,
        aromatic_atoms / count,
        (count - symbols.get("C", 0)) / count,
        ring_atoms / count,
        len(atoms) - len(heavy),
    ]


DESCRIPTOR_NAMES = [
    "heavy_atoms", "C", "N", "O", "F", "S", "Si", "other",
    "ring_atoms", "aromatic_atoms", "CF3", "carbonyl", "ether", "sulfone", "imide",
    "double_bonds", "single_bonds", "aromatic_fraction", "hetero_fraction",
    "ring_atom_fraction", "attachment_points",
]


def scaffold_key(atoms, bonds):
    alive = prune_scaffold(atoms, bonds)
    if not alive:
        return "empty"
    labels = neighbourhood_labels(atoms, bonds, 3, alive)
    signature = "|".join(sorted(labels))
    return str(stable_hash(signature, 1 << 40))


def monomer_key(atoms, bonds):
    heavy = [i for i in range(len(atoms)) if atoms[i].symbol != "*"]
    symbols = Counter(atoms[i].symbol for i in heavy)
    ring_closures = sum(1 for i in heavy if atoms[i].ring) // 2
    parts = ["{}:{}".format(s, symbols[s]) for s in sorted(symbols)]
    parts.append("rings:{}".format(ring_closures))
    return "|".join(parts)


def chemistry_key(atoms, bonds):
    heavy = [i for i in range(len(atoms)) if atoms[i].symbol != "*"]
    labels = neighbourhood_labels(atoms, bonds, 2, heavy)
    top = sorted(labels)[: 6]
    return str(stable_hash("|".join(top), 1 << 40))


def load_dataset():
    with open(DATA, newline="") as handle:
        rows = list(csv.DictReader(handle))
    kept = []
    drops = []
    for row in rows:
        if row["polymer_class"] != "polyimide":
            continue
        try:
            value = float(row["tg_value"])
        except ValueError:
            drops.append({"record_id": row["record_id"], "reason": "missing_tg"})
            continue
        if row["tg_unit"] == "C":
            value += 273.15
        if not (100.0 <= value <= 900.0):
            drops.append({"record_id": row["record_id"], "reason": "tg_out_of_range"})
            continue
        try:
            atoms, bonds = parse_smiles(row["repeat_unit_smiles"])
        except Exception:
            drops.append({"record_id": row["record_id"], "reason": "parse_failed"})
            continue
        if len(atoms) < 3:
            drops.append({"record_id": row["record_id"], "reason": "too_few_atoms"})
            continue
        kept.append(
            {
                "record_id": row["record_id"],
                "tg_k": value,
                "atoms": atoms,
                "bonds": bonds,
            }
        )
    return len(rows), kept, drops


def build_features(kept):
    descriptor_rows = []
    fingerprint_rows = []
    scaffolds = []
    monomers = []
    chemistries = []
    for row in kept:
        atoms, bonds = row["atoms"], row["bonds"]
        descriptor_rows.append(descriptors(atoms, bonds))
        fingerprint_rows.append(fingerprint(atoms, bonds))
        scaffolds.append(scaffold_key(atoms, bonds))
        monomers.append(monomer_key(atoms, bonds))
        chemistries.append(chemistry_key(atoms, bonds))
    return descriptor_rows, fingerprint_rows, scaffolds, monomers, chemistries


def standardize(train_rows, other_rows):
    n_features = len(train_rows[0])
    means = [0.0] * n_features
    stds = [0.0] * n_features
    for row in train_rows:
        for j, value in enumerate(row):
            means[j] += value
    for j in range(n_features):
        means[j] /= len(train_rows)
    for row in train_rows:
        for j, value in enumerate(row):
            stds[j] += (value - means[j]) ** 2
    for j in range(n_features):
        stds[j] = math.sqrt(stds[j] / len(train_rows)) or 1.0
    def scale(rows):
        return [[(row[j] - means[j]) / stds[j] for j in range(n_features)] for row in rows]
    return scale(train_rows), [scale(rows) for rows in other_rows]


def solve(matrix, vector):
    n = len(vector)
    aug = [matrix[i][:] + [vector[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            continue
        aug[col], aug[pivot] = aug[pivot], aug[col]
        factor = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] /= factor
        for r in range(n):
            if r == col:
                continue
            ratio = aug[r][col]
            if ratio == 0.0:
                continue
            for j in range(col, n + 1):
                aug[r][j] -= ratio * aug[col][j]
    return [aug[i][n] for i in range(n)]


def ridge_fit(x, y, lam):
    n_features = len(x[0])
    gram = [[0.0] * n_features for _ in range(n_features)]
    rhs = [0.0] * n_features
    for row, target in zip(x, y):
        for a in range(n_features):
            value = row[a]
            if value == 0.0:
                continue
            rhs[a] += value * target
            gram_row = gram[a]
            for b in range(a, n_features):
                gram_row[b] += value * row[b]
    for a in range(n_features):
        for b in range(a):
            gram[a][b] = gram[b][a]
        gram[a][a] += lam
    return solve(gram, rhs)


def predict_linear(x, weights, bias):
    return [sum(w * v for w, v in zip(weights, row)) + bias for row in x]


def linear_fit(x, y):
    weights = ridge_fit(x, y, 1e-6)
    bias = sum(y) / len(y)
    return weights, bias


def svr_fit(x, y, epsilon=0.1, lam=1e-3, epochs=60, lr=1e-2, seed=0):
    n_features = len(x[0])
    weights = [0.0] * n_features
    bias = sum(y) / len(y)
    rng = random.Random(seed)
    order = list(range(len(y)))
    for _ in range(epochs):
        rng.shuffle(order)
        for i in order:
            row = x[i]
            residual = sum(w * v for w, v in zip(weights, row)) + bias - y[i]
            if residual > epsilon:
                sign = 1.0
            elif residual < -epsilon:
                sign = -1.0
            else:
                sign = 0.0
            for j in range(n_features):
                weights[j] -= lr * (sign * row[j] + lam * weights[j] / len(y))
            bias -= lr * sign
    return weights, bias


class Tree:
    __slots__ = ("feature", "threshold", "left", "right", "value")

    def __init__(self):
        self.feature = None
        self.threshold = 0.0
        self.left = None
        self.right = None
        self.value = 0.0


def build_tree(x, y, indices, depth, max_depth, min_leaf, max_features, rng, feature_count):
    node = Tree()
    node.value = sum(y[i] for i in indices) / len(indices)
    if depth >= max_depth or len(indices) < 2 * min_leaf:
        return node
    features = rng.sample(range(feature_count), min(max_features, feature_count))
    best = None
    parent_var = sum((y[i] - node.value) ** 2 for i in indices)
    total_sum = sum(y[i] for i in indices)
    total_sq = sum(y[i] ** 2 for i in indices)
    for feature in features:
        order = sorted(indices, key=lambda i: x[i][feature])
        left_sum = 0.0
        left_sq = 0.0
        for pos in range(len(order) - 1):
            i = order[pos]
            left_sum += y[i]
            left_sq += y[i] ** 2
            n_left = pos + 1
            n_right = len(order) - n_left
            if n_left < min_leaf or n_right < min_leaf:
                continue
            if x[order[pos]][feature] == x[order[pos + 1]][feature]:
                continue
            right_sum = total_sum - left_sum
            right_sq = total_sq - left_sq
            var = left_sq - left_sum ** 2 / n_left + right_sq - right_sum ** 2 / n_right
            if best is None or var < best[0]:
                best = (var, feature, (x[order[pos]][feature] + x[order[pos + 1]][feature]) / 2)
    if best is None or best[0] >= parent_var - 1e-9:
        return node
    node.feature = best[1]
    node.threshold = best[2]
    left = [i for i in indices if x[i][node.feature] <= node.threshold]
    right = [i for i in indices if x[i][node.feature] > node.threshold]
    node.left = build_tree(x, y, left, depth + 1, max_depth, min_leaf, max_features, rng, feature_count)
    node.right = build_tree(x, y, right, depth + 1, max_depth, min_leaf, max_features, rng, feature_count)
    return node


def tree_predict(node, row):
    while node.feature is not None:
        node = node.left if row[node.feature] <= node.threshold else node.right
    return node.value


class RandomForest:
    def __init__(self, n_estimators=30, max_depth=10, min_leaf=5, max_features=0.25, seed=0):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_leaf = min_leaf
        self.max_features = max_features
        self.seed = seed
        self.trees = []

    def fit(self, x, y):
        rng = random.Random(self.seed)
        n = len(x)
        feature_count = len(x[0])
        k = max(1, int(feature_count * self.max_features))
        self.trees = []
        for _ in range(self.n_estimators):
            sample = [rng.randrange(n) for _ in range(n)]
            self.trees.append(
                build_tree(x, y, sample, 0, self.max_depth, self.min_leaf, k, rng, feature_count)
            )
        return self

    def predict(self, x):
        return [sum(tree_predict(t, row) for t in self.trees) / len(self.trees) for row in x]

    def predict_std(self, x):
        result = []
        for row in x:
            values = [tree_predict(t, row) for t in self.trees]
            mean = sum(values) / len(values)
            result.append(math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)))
        return result


class GradientBoosting:
    def __init__(self, n_estimators=120, max_depth=3, learning_rate=0.05, min_leaf=8, seed=0):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.min_leaf = min_leaf
        self.seed = seed
        self.trees = []
        self.base = 0.0

    def fit(self, x, y):
        rng = random.Random(self.seed)
        self.base = sum(y) / len(y)
        prediction = [self.base] * len(y)
        feature_count = len(x[0])
        self.trees = []
        for _ in range(self.n_estimators):
            residual = [y[i] - prediction[i] for i in range(len(y))]
            tree = build_tree(
                x, residual, list(range(len(y))), 0, self.max_depth, self.min_leaf,
                max(1, int(feature_count * 0.4)), rng, feature_count,
            )
            self.trees.append(tree)
            for i in range(len(y)):
                prediction[i] += self.learning_rate * tree_predict(tree, x[i])
        return self

    def predict(self, x):
        return [
            self.base + self.learning_rate * sum(tree_predict(t, row) for t in self.trees)
            for row in x
        ]


def mae(y, p):
    return sum(abs(a - b) for a, b in zip(y, p)) / len(y)


def rmse(y, p):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(y, p)) / len(y))


def r2(y, p):
    mean = sum(y) / len(y)
    total = sum((a - mean) ** 2 for a in y)
    residual = sum((a - b) ** 2 for a, b in zip(y, p))
    return 1.0 - residual / total if total else 0.0


def rank(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = average
        i = j + 1
    return ranks


def spearman(y, p):
    a = rank(y)
    b = rank(p)
    n = len(y)
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    cov = sum((x - mean_a) * (z - mean_b) for x, z in zip(a, b))
    var_a = math.sqrt(sum((x - mean_a) ** 2 for x in a))
    var_b = math.sqrt(sum((z - mean_b) ** 2 for z in b))
    return cov / (var_a * var_b) if var_a and var_b else 0.0


def metrics(y, p):
    return {
        "mae": mae(y, p),
        "rmse": rmse(y, p),
        "r2": r2(y, p),
        "spearman": spearman(y, p),
    }


def group_split(keys, test_fraction, seed):
    rng = random.Random(seed)
    counts = Counter(keys)
    unique = sorted(counts)
    rng.shuffle(unique)
    target = int(len(keys) * test_fraction)
    test_groups = set()
    size = 0
    for key in unique:
        if size >= target:
            break
        test_groups.add(key)
        size += counts[key]
    train_idx = [i for i, key in enumerate(keys) if key not in test_groups]
    test_idx = [i for i, key in enumerate(keys) if key in test_groups]
    return train_idx, test_idx, len(unique), len(test_groups)


def random_split(size, test_fraction, seed):
    rng = random.Random(seed)
    indices = list(range(size))
    rng.shuffle(indices)
    cut = int(size * (1 - test_fraction))
    return sorted(indices[:cut]), sorted(indices[cut:]), size, size


def slice_rows(rows, indices):
    return [rows[i] for i in indices]


def run_models(train_x, train_y, test_x, test_y, seed):
    results = {}
    mean_prediction = [sum(train_y) / len(train_y)] * len(test_y)
    results["mean"] = metrics(test_y, mean_prediction)

    weights, bias = linear_fit(train_x, train_y)
    results["linear"] = metrics(test_y, predict_linear(test_x, weights, bias))

    for lam in (0.01, 0.1, 1.0, 10.0):
        weights = ridge_fit(train_x, train_y, lam)
        bias = sum(train_y) / len(train_y)
        results["ridge_lambda_{}".format(lam)] = metrics(test_y, predict_linear(test_x, weights, bias))

    weights, bias = svr_fit(train_x, train_y, seed=seed)
    results["svr"] = metrics(test_y, predict_linear(test_x, weights, bias))

    forest = RandomForest(seed=seed)
    forest.fit(train_x, train_y)
    forest_prediction = forest.predict(test_x)
    results["random_forest"] = metrics(test_y, forest_prediction)
    results["random_forest"]["ensemble_std_mean"] = sum(forest.predict_std(test_x)) / len(test_x)

    boosting = GradientBoosting(seed=seed)
    boosting.fit(train_x, train_y)
    results["gradient_boosting"] = metrics(test_y, boosting.predict(test_x))

    return results, forest, boosting


def conformal(train_x, train_y, test_x, test_y, model, seed, alpha=0.1):
    rng = random.Random(seed)
    indices = list(range(len(train_y)))
    rng.shuffle(indices)
    cut = int(len(indices) * 0.8)
    fit_idx = indices[:cut]
    cal_idx = indices[cut:]
    fit_x = [train_x[i] for i in fit_idx]
    fit_y = [train_y[i] for i in fit_idx]
    cal_x = [train_x[i] for i in cal_idx]
    cal_y = [train_y[i] for i in cal_idx]
    if isinstance(model, RandomForest):
        inner = RandomForest(seed=seed)
    else:
        inner = GradientBoosting(seed=seed)
    inner.fit(fit_x, fit_y)
    residual = [abs(cal_y[i] - inner.predict([cal_x[i]])[0]) for i in range(len(cal_y))]
    residual.sort()
    index = min(len(residual) - 1, math.ceil((1 - alpha) * (len(residual) + 1)) - 1)
    quantile = residual[index]
    prediction = model.predict(test_x)
    covered = sum(
        1 for a, p in zip(test_y, prediction) if p - quantile <= a <= p + quantile
    )
    return {
        "alpha": alpha,
        "nominal_coverage": 1 - alpha,
        "quantile_k": quantile,
        "coverage": covered / len(test_y),
        "mean_width_k": 2 * quantile,
    }


def quantile_boosting(train_x, train_y, seed, quantiles=(0.05, 0.5, 0.95)):
    models = {}
    for q in quantiles:
        model = QuantileBoosting(seed=seed, quantile=q)
        model.fit(train_x, train_y)
        models[q] = model
    return models


class QuantileBoosting:
    def __init__(self, n_estimators=80, max_depth=3, learning_rate=0.05, min_leaf=10,
                 quantile=0.5, seed=0):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.min_leaf = min_leaf
        self.quantile = quantile
        self.seed = seed
        self.trees = []
        self.base = 0.0

    def fit(self, x, y):
        rng = random.Random(self.seed)
        self.base = sorted(y)[int(self.quantile * (len(y) - 1))]
        prediction = [self.base] * len(y)
        feature_count = len(x[0])
        self.trees = []
        for _ in range(self.n_estimators):
            residual = []
            for i in range(len(y)):
                residual.append(self.quantile if y[i] >= prediction[i] else self.quantile - 1)
            tree = build_tree(
                x, residual, list(range(len(y))), 0, self.max_depth, self.min_leaf,
                max(1, int(feature_count * 0.4)), rng, feature_count,
            )
            self.trees.append(tree)
            for i in range(len(y)):
                prediction[i] += self.learning_rate * tree_predict(tree, x[i])
        return self

    def predict(self, x):
        return [
            self.base + self.learning_rate * sum(tree_predict(t, row) for t in self.trees)
            for row in x
        ]


def learning_curve(train_x, train_y, test_x, test_y, seed):
    curve = []
    for size in (50, 100, 200, 400, 800, 1200):
        if size > len(train_y):
            continue
        rng = random.Random(seed)
        indices = list(range(len(train_y)))
        rng.shuffle(indices)
        subset = indices[:size]
        model = GradientBoosting(seed=seed)
        model.fit(slice_rows(train_x, subset), slice_rows(train_y, subset))
        curve.append({"n": size, "mae": mae(test_y, model.predict(test_x))})
    return curve


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    input_sha = sha256_file(DATA)
    total_rows, kept, drops = load_dataset()
    print("cleaning: kept {0}, dropped {1}, of {2} records".format(len(kept), len(drops), total_rows))

    descriptor_rows, fingerprint_rows, scaffolds, monomers, chemistries = build_features(kept)
    values = [row["tg_k"] for row in kept]
    combined = [descriptor_rows[i] + [float(v) for v in fingerprint_rows[i]] for i in range(len(kept))]

    summary = {
        "input": {
            "path": "experiments/ch16/flagship/data/polymer-tg-dataset.csv",
            "sha256": input_sha,
            "total_records": total_rows,
            "polyimide_kept": len(kept),
            "dropped": len(drops),
            "tg_k_min": min(values),
            "tg_k_max": max(values),
            "tg_k_mean": sum(values) / len(values),
            "tg_k_std": math.sqrt(sum((v - sum(values) / len(values)) ** 2 for v in values) / len(values)),
            "above_473K": sum(1 for v in values if v >= TARGET_TG_K),
        },
        "features": {
            "descriptors": DESCRIPTOR_NAMES,
            "fingerprint_bits": N_BITS,
            "fingerprint_radius": RADIUS,
            "combined_dim": len(combined[0]),
        },
        "splits": {},
        "primary_models": {},
        "split_comparison": {},
        "feature_ablation": {},
        "uncertainty": {},
        "learning_curve": {},
        "gnn_cost_reference": {},
        "not_run": [],
    }

    split_keys = {
        "random": None,
        "scaffold": scaffolds,
        "monomer": monomers,
        "chemistry": chemistries,
    }

    primary = {}
    for seed in SEEDS:
        train_idx, test_idx, n_groups, n_test_groups = group_split(scaffolds, TEST_FRACTION, seed)
        train_x_raw = slice_rows(combined, train_idx)
        test_x_raw = slice_rows(combined, test_idx)
        train_y = slice_rows(values, train_idx)
        test_y = slice_rows(values, test_idx)
        train_x, (test_x,) = standardize(train_x_raw, [test_x_raw])
        results, _, _ = run_models(train_x, train_y, test_x, test_y, seed)
        primary[seed] = {
            "train": len(train_idx),
            "test": len(test_idx),
            "groups": n_groups,
            "test_groups": n_test_groups,
            "models": results,
        }
        print("scaffold split seed {0}: GB MAE {1:.2f} K".format(seed, results["gradient_boosting"]["mae"]))

    model_names = sorted(primary[PRIMARY_SEED]["models"])
    aggregate = {}
    for name in model_names:
        for metric in ("mae", "rmse", "r2", "spearman"):
            scores = [primary[s]["models"][name][metric] for s in SEEDS]
            mean = sum(scores) / len(scores)
            std = math.sqrt(sum((v - mean) ** 2 for v in scores) / len(scores))
            aggregate.setdefault(name, {})[metric] = {"mean": mean, "std": std}
        if "ensemble_std_mean" in primary[PRIMARY_SEED]["models"][name]:
            scores = [primary[s]["models"][name]["ensemble_std_mean"] for s in SEEDS]
            aggregate[name]["ensemble_std_mean"] = {"mean": sum(scores) / len(scores), "std": 0.0}
    summary["primary_models"] = {
        "split": "scaffold (grouped by pruned substructure signature)",
        "seeds": SEEDS,
        "aggregate": aggregate,
        "per_seed": {str(s): primary[s] for s in SEEDS},
    }

    for split_name, keys in split_keys.items():
        entries = []
        for seed in SEEDS[:3]:
            if keys is None:
                train_idx, test_idx, n_groups, n_test_groups = random_split(len(kept), TEST_FRACTION, seed)
            else:
                train_idx, test_idx, n_groups, n_test_groups = group_split(keys, TEST_FRACTION, seed)
            train_x_raw = slice_rows(combined, train_idx)
            test_x_raw = slice_rows(combined, test_idx)
            train_y = slice_rows(values, train_idx)
            test_y = slice_rows(values, test_idx)
            train_x, (test_x,) = standardize(train_x_raw, [test_x_raw])
            weights = ridge_fit(train_x, train_y, 1.0)
            bias = sum(train_y) / len(train_y)
            ridge_mae = mae(test_y, predict_linear(test_x, weights, bias))
            boosting = GradientBoosting(seed=seed)
            boosting.fit(train_x, train_y)
            gb_mae = mae(test_y, boosting.predict(test_x))
            entries.append({
                "seed": seed,
                "train": len(train_idx),
                "test": len(test_idx),
                "groups": n_groups,
                "test_groups": n_test_groups,
                "ridge_mae": ridge_mae,
                "gradient_boosting_mae": gb_mae,
            })
        summary["splits"][split_name] = entries
        for metric in ("ridge_mae", "gradient_boosting_mae"):
            scores = [e[metric] for e in entries]
            mean = sum(scores) / len(scores)
            std = math.sqrt(sum((v - mean) ** 2 for v in scores) / len(scores))
            summary["split_comparison"].setdefault(metric, {})[split_name] = {"mean": mean, "std": std}
        print("split {0}: ridge MAE {1:.2f}, GB MAE {2:.2f}".format(
            split_name,
            summary["split_comparison"]["ridge_mae"][split_name]["mean"],
            summary["split_comparison"]["gradient_boosting_mae"][split_name]["mean"],
        ))

    feature_sets = {
        "descriptors_only": descriptor_rows,
        "fingerprint_only": [[float(v) for v in row] for row in fingerprint_rows],
        "combined": combined,
    }
    for name, rows in feature_sets.items():
        train_idx, test_idx, _, _ = group_split(scaffolds, TEST_FRACTION, PRIMARY_SEED)
        train_x_raw = slice_rows(rows, train_idx)
        test_x_raw = slice_rows(rows, test_idx)
        train_y = slice_rows(values, train_idx)
        test_y = slice_rows(values, test_idx)
        train_x, (test_x,) = standardize(train_x_raw, [test_x_raw])
        weights = ridge_fit(train_x, train_y, 1.0)
        bias = sum(train_y) / len(train_y)
        boosting = GradientBoosting(seed=PRIMARY_SEED)
        boosting.fit(train_x, train_y)
        summary["feature_ablation"][name] = {
            "dim": len(train_x_raw[0]),
            "ridge_mae": mae(test_y, predict_linear(test_x, weights, bias)),
            "gradient_boosting_mae": mae(test_y, boosting.predict(test_x)),
        }
        print("features {0}: ridge MAE {1:.2f}, GB MAE {2:.2f}".format(
            name,
            summary["feature_ablation"][name]["ridge_mae"],
            summary["feature_ablation"][name]["gradient_boosting_mae"],
        ))

    train_idx, test_idx, _, _ = group_split(scaffolds, TEST_FRACTION, PRIMARY_SEED)
    train_x_raw = slice_rows(combined, train_idx)
    test_x_raw = slice_rows(combined, test_idx)
    train_y = slice_rows(values, train_idx)
    test_y = slice_rows(values, test_idx)
    train_x, (test_x,) = standardize(train_x_raw, [test_x_raw])
    forest = RandomForest(seed=PRIMARY_SEED)
    forest.fit(train_x, train_y)
    boosting = GradientBoosting(seed=PRIMARY_SEED)
    boosting.fit(train_x, train_y)

    conformal_levels = [conformal(train_x, train_y, test_x, test_y, boosting, PRIMARY_SEED, a)
                        for a in (0.05, 0.1, 0.2)]
    quantile_models = quantile_boosting(train_x, train_y, PRIMARY_SEED)
    lower = quantile_models[0.05].predict(test_x)
    upper = quantile_models[0.95].predict(test_x)
    covered = sum(1 for a, lo, hi in zip(test_y, lower, upper) if lo <= a <= hi)
    widths = [hi - lo for lo, hi in zip(lower, upper)]
    summary["uncertainty"] = {
        "conformal": conformal_levels,
        "quantile_regression": {
            "nominal_coverage": 0.9,
            "coverage": covered / len(test_y),
            "mean_width_k": sum(widths) / len(widths),
        },
        "ensemble_variance": {
            "random_forest_std_mean_k": sum(forest.predict_std(test_x)) / len(test_x),
            "gradient_boosting_note": "single model, no native variance; conformal interval used",
        },
    }
    for level in conformal_levels:
        print("conformal {0:.0f}%: achieved {1:.1%}, width {2:.1f} K".format(
            level["nominal_coverage"] * 100, level["coverage"], level["mean_width_k"]))
    print("quantile regression 90%: achieved {0:.1%}, width {1:.1f} K".format(
        summary["uncertainty"]["quantile_regression"]["coverage"],
        summary["uncertainty"]["quantile_regression"]["mean_width_k"]))

    curve = learning_curve(train_x, train_y, test_x, test_y, PRIMARY_SEED)
    if len(curve) >= 2:
        xs = [math.log(c["n"]) for c in curve]
        ys = [math.log(c["mae"]) for c in curve]
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sum((x - mean_x) ** 2 for x in xs)
        intercept = mean_y - slope * mean_x
        predicted = [intercept + slope * x for x in xs]
        ss_res = sum((y - p) ** 2 for y, p in zip(ys, predicted))
        ss_tot = sum((y - mean_y) ** 2 for y in ys)
        summary["learning_curve"] = {
            "points": curve,
            "power_law_exponent": -slope,
            "power_law_A": math.exp(intercept),
            "fit_r2": 1 - ss_res / ss_tot if ss_tot else 0.0,
        }
        print("learning curve: A {0:.1f}, alpha {1:.3f}, fit R2 {2:.3f}".format(
            math.exp(intercept), -slope, summary["learning_curve"]["fit_r2"]))

    if GNN_COST.is_file():
        gnn = json.loads(GNN_COST.read_text())
        summary["gnn_cost_reference"] = {
            "source": "calculations/results/gnn-forward-4layer.json",
            "parameters": gnn["summary"]["parameters"],
            "total_flops": gnn["summary"]["total_flops"],
            "note": "cost model only; GNN accuracy not measured (no GNN dependency in this pure-stdlib benchmark)",
        }
    summary["not_run"] = [
        "GNN (MPNN/GCN/GAT/Chemprop/equivariant): no graph-network dependency in this stdlib-only benchmark; cost taken from the book cost model, accuracy not measured.",
        "Sequence models (RNN/Transformer/PolyBERT): no deep-learning dependency; not run.",
        "Time split: the dataset carries no publication year or measurement date, so a temporal split cannot be constructed.",
        "Monomer split uses a coarse repeat-unit composition family as a proxy because the dataset has no explicit monomer labels.",
    ]

    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")

    with open(OUT / "model_comparison.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["model", "mae_mean", "mae_std", "rmse_mean", "r2_mean", "spearman_mean"])
        for name in model_names:
            row = aggregate[name]
            writer.writerow([
                name,
                "{:.4f}".format(row["mae"]["mean"]),
                "{:.4f}".format(row["mae"]["std"]),
                "{:.4f}".format(row["rmse"]["mean"]),
                "{:.4f}".format(row["r2"]["mean"]),
                "{:.4f}".format(row["spearman"]["mean"]),
            ])

    with open(OUT / "split_comparison.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["split", "ridge_mae_mean", "ridge_mae_std", "gb_mae_mean", "gb_mae_std",
                         "train_mean", "test_mean", "groups_mean"])
        for split_name in split_keys:
            entries = summary["splits"][split_name]
            writer.writerow([
                split_name,
                "{:.4f}".format(summary["split_comparison"]["ridge_mae"][split_name]["mean"]),
                "{:.4f}".format(summary["split_comparison"]["ridge_mae"][split_name]["std"]),
                "{:.4f}".format(summary["split_comparison"]["gradient_boosting_mae"][split_name]["mean"]),
                "{:.4f}".format(summary["split_comparison"]["gradient_boosting_mae"][split_name]["std"]),
                "{:.1f}".format(sum(e["train"] for e in entries) / len(entries)),
                "{:.1f}".format(sum(e["test"] for e in entries) / len(entries)),
                "{:.1f}".format(sum(e["groups"] for e in entries) / len(entries)),
            ])

    with open(OUT / "feature_ablation.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["feature_set", "dim", "ridge_mae", "gradient_boosting_mae"])
        for name, row in summary["feature_ablation"].items():
            writer.writerow([name, row["dim"], "{:.4f}".format(row["ridge_mae"]),
                             "{:.4f}".format(row["gradient_boosting_mae"])])

    with open(OUT / "learning_curve.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["n", "mae"])
        for point in summary["learning_curve"].get("points", []):
            writer.writerow([point["n"], "{:.4f}".format(point["mae"])])

    manifest = {
        "seed_primary": PRIMARY_SEED,
        "seeds": SEEDS,
        "input": {DATA.name: input_sha},
        "outputs": {},
    }
    for name in ("summary.json", "model_comparison.csv", "split_comparison.csv",
                 "feature_ablation.csv", "learning_curve.csv"):
        manifest["outputs"][name] = sha256_file(OUT / name)
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print("results written to " + str(OUT))


if __name__ == "__main__":
    main()
