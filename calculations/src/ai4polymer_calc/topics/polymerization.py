"""Declared polymerization-kinetics and copolymerization models.

Step-growth Carothers conversion, Flory most-probable and living Poisson chain
length distributions, and Mayo-Lewis instantaneous copolymerization with
composition drift. Every number is a declared model output, not a measurement.
"""
from math import exp, lgamma, log

from ..schema import result
from ..sources import provenance
from ..units import fraction, positive_int, positive_number


def _split_floats(text, name):
    try:
        values = [float(piece) for piece in str(text).replace(":", ",").split(",") if piece.strip()]
    except ValueError as error:
        raise ValueError(f"{name} must list numbers separated by commas") from error
    if not values:
        raise ValueError(f"{name} must list at least one number")
    return values


def _split_ints(text, name):
    values = [int(piece) for piece in str(text).split(",") if piece.strip()]
    if not values:
        raise ValueError(f"{name} must list at least one integer")
    return values


def _split_pairs(text, name):
    pairs = []
    for piece in str(text).split(";"):
        piece = piece.strip()
        if not piece:
            continue
        left, _, right = piece.partition(":")
        if not _:
            raise ValueError(f"{name} entries must look like r1:r2")
        pairs.append((float(left), float(right)))
    if not pairs:
        raise ValueError(f"{name} must list at least one r1:r2 pair")
    return pairs


def _step_growth(conversions):
    rows = []
    for p in conversions:
        fraction(p, "conversion")
        number_average = 1.0 / (1.0 - p)
        weight_average = (1.0 + p) / (1.0 - p)
        rows.append(dict(conversion=p, number_average_dp=number_average,
                         weight_average_dp=weight_average,
                         dispersity=weight_average / number_average))
    return rows


def _living(ratios, conversion):
    rows = []
    for ratio in ratios:
        positive_int(ratio, "monomer_to_initiator")
        nu = conversion * ratio
        number_average = nu + 1.0
        weight_average = (nu * nu + 3.0 * nu + 1.0) / (nu + 1.0)
        rows.append(dict(monomer_to_initiator=ratio, conversion=conversion,
                         number_average_dp=number_average,
                         weight_average_dp=weight_average,
                         dispersity=weight_average / number_average))
    return rows


def _instantaneous_f1(f1, r1, r2):
    f2 = 1.0 - f1
    denominator = r1 * f1 * f1 + 2.0 * f1 * f2 + r2 * f2 * f2
    return (r1 * f1 * f1 + f1 * f2) / denominator


def _azeotrope(r1, r2):
    denominator = 2.0 - r1 - r2
    if abs(denominator) < 1e-12:
        return None
    value = (1.0 - r2) / denominator
    return value if 0.0 < value < 1.0 else None


def _classify(r1, r2):
    if r1 < 1.0 and r2 < 1.0:
        return "交替倾向"
    if r1 > 1.0 and r2 > 1.0:
        return "嵌段倾向"
    if abs(r1 - 1.0) < 1e-9 and abs(r2 - 1.0) < 1e-9:
        return "无规"
    return "梯度/组成漂移"


def _run_lengths(f1, r1, r2):
    f2 = 1.0 - f1
    return (r1 * f1 + f2) / f2, (f1 + r2 * f2) / f1


def _drift(r1, r2, initial_f1, max_conversion, steps):
    def slope(p, f1):
        return (f1 - _instantaneous_f1(f1, r1, r2)) / (1.0 - p)

    points = [dict(conversion=0.0, feed_f1=initial_f1,
                   instantaneous_F1=_instantaneous_f1(initial_f1, r1, r2),
                   cumulative_F1=initial_f1)]
    f1 = initial_f1
    p = 0.0
    dp = max_conversion / steps
    for _ in range(steps):
        k1 = slope(p, f1)
        k2 = slope(p + dp / 2.0, f1 + dp * k1 / 2.0)
        k3 = slope(p + dp / 2.0, f1 + dp * k2 / 2.0)
        k4 = slope(p + dp, f1 + dp * k3)
        f1 = min(max(f1 + dp * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0, 1e-9), 1.0 - 1e-9)
        p += dp
        points.append(dict(conversion=p, feed_f1=f1,
                           instantaneous_F1=_instantaneous_f1(f1, r1, r2),
                           cumulative_F1=(initial_f1 - (1.0 - p) * f1) / p))
    return points


def _flory(conversion, curve_points):
    fraction(conversion, "flory_conversion")
    number_average = 1.0 / (1.0 - conversion)
    n_max = max(2, int(round(6.0 * number_average)))
    stride = max(1, n_max // curve_points)
    n_values = list(range(1, n_max + 1, stride))
    number_fraction = [(1.0 - conversion) * conversion ** (n - 1) for n in n_values]
    weight_fraction = [n * (1.0 - conversion) ** 2 * conversion ** (n - 1) for n in n_values]
    weight_average = (1.0 + conversion) / (1.0 - conversion)
    return dict(conversion=conversion, number_average_dp=number_average,
                weight_average_dp=weight_average,
                dispersity=weight_average / number_average,
                n=n_values, number_fraction=number_fraction,
                weight_fraction=weight_fraction)


def _poisson(mean_dp, curve_points):
    positive_number(mean_dp, "poisson_mean_dp")
    nu = mean_dp - 1.0
    n_max = max(2, int(round(mean_dp + 5.0 * mean_dp ** 0.5)))
    stride = max(1, n_max // curve_points)
    n_values = list(range(1, n_max + 1, stride))
    log_p = [-nu + (n - 1) * log(nu) - lgamma(n) for n in n_values]
    number_fraction = [exp(value) for value in log_p]
    weight_fraction = [n * value / mean_dp for n, value in zip(n_values, number_fraction)]
    weight_average = (nu * nu + 3.0 * nu + 1.0) / (nu + 1.0)
    return dict(mean_dp=mean_dp, number_average_dp=nu + 1.0,
                weight_average_dp=weight_average,
                dispersity=weight_average / (nu + 1.0),
                n=n_values, number_fraction=number_fraction,
                weight_fraction=weight_fraction)


def calculate(step_conversions="0.9,0.99,0.999", living_ratios="50,100,200",
              living_conversion=0.99, copolymer_pairs="0.1:0.1;1:1;10:0.1;0.1:10",
              feed_fraction=0.5, max_conversion=0.99, drift_steps=100,
              flory_conversion=0.99, poisson_mean_dp=100, curve_points=80) -> dict:
    step_rows = _step_growth(_split_floats(step_conversions, "step_conversions"))
    living_rows = _living(_split_ints(living_ratios, "living_ratios"),
                          fraction(living_conversion, "living_conversion"))
    fraction(feed_fraction, "feed_fraction")
    fraction(max_conversion, "max_conversion")
    positive_int(drift_steps, "drift_steps")

    copolymer_rows = []
    for r1, r2 in _split_pairs(copolymer_pairs, "copolymer_pairs"):
        positive_number(r1, "r1")
        positive_number(r2, "r2")
        length_1, length_2 = _run_lengths(feed_fraction, r1, r2)
        copolymer_rows.append(dict(
            r1=r1, r2=r2, classification=_classify(r1, r2),
            azeotrope_f1=_azeotrope(r1, r2),
            feed_fraction_1=feed_fraction,
            instantaneous_F1=_instantaneous_f1(feed_fraction, r1, r2),
            run_length_1=length_1, run_length_2=length_2,
            drift=_drift(r1, r2, feed_fraction, max_conversion, drift_steps)))

    return result(
        calculation="polymerization",
        model="declared-step-growth-flory-mayo-lewis",
        scenario=dict(step_conversions=step_conversions, living_ratios=living_ratios,
                      living_conversion=living_conversion, copolymer_pairs=copolymer_pairs,
                      feed_fraction=feed_fraction, max_conversion=max_conversion,
                      drift_steps=drift_steps, flory_conversion=flory_conversion,
                      poisson_mean_dp=poisson_mean_dp, curve_points=curve_points),
        sources=provenance(["flory-1940", "mayo-lewis-1944", "matyjaszewski-2001"]),
        summary=dict(
            step_growth=step_rows, living=living_rows, copolymer=copolymer_rows,
            flory=_flory(flory_conversion, curve_points),
            poisson=_poisson(poisson_mean_dp, curve_points)),
        assumptions=[
            "逐步聚合采用 Carothers 关系 $\\bar X_n=1/(1-p)$ 与最可几 Flory 分布；$\\bar X_w=(1+p)/(1-p)$，故分散度 $\\bar X_w/\\bar X_n=1+p$，$p\\to1$ 时趋近 2。",
            "活性/可控聚合采用 Poisson 链长分布：$\\nu$ 为单体与引发剂投料比乘转化率，$\\bar X_n=\\nu+1$，分散度 $=(\\nu^2+3\\nu+1)/(\\nu+1)^2$，$\\nu\\to\\infty$ 时趋近 1。",
            "共聚采用 Mayo-Lewis 瞬时组成方程；组成漂移由 $\\mathrm d f_1/\\mathrm d p=(f_1-F_1)/(1-p)$ 以固定步长 RK4 积分，初值为投料组成。",
            "序列长度按 Bernoulli（末端模型）近似：单体 1 的平均连续单元数 $L_1=(r_1f_1+f_2)/f_2$，单体 2 对称。",
            "所有数值为声明模型的解析或数值输出，参数为建模输入，不代表任何实测体系的速率常数或分布。",
        ])
