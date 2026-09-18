"""Pure-standard-library chemistry and ML helpers for the chapter 16 cases.

The module is shared by experiments/ch16/case2 and experiments/ch16/case3 so the
two scripts stay readable and both depend on nothing outside the Python standard
library. It reuses the same conventions as experiments/ch06/benchmark: a minimal
SMILES graph parser, interpretable descriptors, a hashed substructure
fingerprint, CART-based tree ensembles, ridge regression, grouped and random
splits, and split conformal intervals.

Only the standard library is imported. Randomness is always seeded by the caller.
"""

import hashlib
import math
import random
from collections import Counter, defaultdict

ORGANIC = ("Cl", "Br", "Si", "Na", "Li", "Ca", "Fe", "Zn", "Al", "Mg")
AROMATIC = {"c", "n", "o", "s", "p", "se", "as"}


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


def fingerprint(atoms, bonds, n_bits=256, radius=2):
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
    carboxyl = 0
    hydroxyl = 0
    ester = 0
    for i in heavy:
        if atoms[i].symbol == "C":
            double_o = sum(1 for j, o in bonds[i].items() if atoms[j].symbol == "O" and o == 2)
            carbonyl += double_o
            fluorines = sum(1 for j, _ in bonds[i].items() if atoms[j].symbol == "F")
            if fluorines == 3:
                cf3 += 1
        if atoms[i].symbol == "O":
            carbons = sum(1 for j, _ in bonds[i].items() if atoms[j].symbol == "C")
            single_o = not any(o == 2 for o in bonds[i].values())
            if carbons >= 2 and single_o:
                ether += 1
                ester += 1
            if carbons == 1 and single_o:
                neighbour = [j for j in bonds[i] if atoms[j].symbol == "C"][0]
                if any(atoms[k].symbol == "O" and o == 2 for k, o in bonds[neighbour].items()):
                    carboxyl += 1
                else:
                    hydroxyl += 1
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
        carboxyl,
        hydroxyl,
        ester,
    ]


DESCRIPTOR_NAMES = [
    "heavy_atoms", "C", "N", "O", "F", "S", "Si", "other",
    "ring_atoms", "aromatic_atoms", "CF3", "carbonyl", "ether", "sulfone", "imide",
    "double_bonds", "single_bonds", "aromatic_fraction", "hetero_fraction",
    "ring_atom_fraction", "attachment_points", "carboxyl", "hydroxyl", "ester",
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


def predict_linear(x, weights, bias=0.0):
    return [sum(w * v for w, v in zip(weights, row)) + bias for row in x]


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


def conformal(train_x, train_y, test_x, test_y, model_factory, seed, alpha=0.1):
    rng = random.Random(seed)
    indices = list(range(len(train_y)))
    rng.shuffle(indices)
    cut = int(len(indices) * 0.8)
    fit_idx = indices[:cut]
    cal_idx = indices[cut:]
    fit_x = slice_rows(train_x, fit_idx)
    fit_y = slice_rows(train_y, fit_idx)
    cal_x = slice_rows(train_x, cal_idx)
    cal_y = slice_rows(train_y, cal_idx)
    inner = model_factory()
    inner.fit(fit_x, fit_y)
    residual = sorted(abs(cal_y[i] - inner.predict([cal_x[i]])[0]) for i in range(len(cal_y)))
    index = min(len(residual) - 1, math.ceil((1 - alpha) * (len(residual) + 1)) - 1)
    quantile = residual[index]
    model = model_factory()
    model.fit(train_x, train_y)
    prediction = model.predict(test_x)
    covered = sum(1 for a, p in zip(test_y, prediction) if p - quantile <= a <= p + quantile)
    return {
        "alpha": alpha,
        "nominal_coverage": 1 - alpha,
        "quantile": quantile,
        "coverage": covered / len(test_y),
        "mean_width": 2 * quantile,
    }


def fold_split(size, n_splits, seed):
    rng = random.Random(seed)
    indices = list(range(size))
    rng.shuffle(indices)
    folds = [[] for _ in range(n_splits)]
    for pos, index in enumerate(indices):
        folds[pos % n_splits].append(index)
    for fold in range(n_splits):
        test = folds[fold]
        train = [i for k, f in enumerate(folds) if k != fold for i in f]
        yield train, test
