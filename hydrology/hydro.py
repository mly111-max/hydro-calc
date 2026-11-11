"""工程水文学计算工具

参考教材：《工程水文学》第 5 版（2020.12），徐向阳、陈元芳，
中国水利水电出版社，ISBN 978-7-5170-9192-9

涵盖：经验频率、矩法统计参数、P-III 型频率曲线与设计值、
设计洪水放大（同频率/同倍比）、推理公式、径流计算。
"""

import math
from statistics import NormalDist

try:
    from scipy.special import gammaincinv
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

_N = NormalDist()


# ---------- 经验频率 ----------
def empirical_frequency(m, n, formula="math"):
    """第 m 项的经验频率。

    formula: 'math' 数学期望公式 m/(n+1)；
             'hazen' 海森公式 (m-0.5)/n。
    """
    if formula == "math":
        return m / (n + 1)
    if formula == "hazen":
        return (m - 0.5) / n
    raise ValueError("formula 只支持 'math' 或 'hazen'")


# ---------- 矩法统计参数 ----------
def moments(x):
    """矩法估计均值、变差系数 Cv、偏态系数 Cs。"""
    n = len(x)
    mean = sum(x) / n
    sigma = math.sqrt(sum((xi - mean) ** 2 for xi in x) / n)
    cv = sigma / mean
    cs = (sum((xi - mean) ** 3 for xi in x) / (n * sigma ** 3)) if sigma else 0.0
    return {"mean": mean, "sigma": sigma, "Cv": cv, "Cs": cs}


# ---------- P-III 型频率曲线 ----------
def normal_quantile(p):
    """标准正态分位数（p 为累积概率）。"""
    return _N.inv_cdf(p)


def phi_p(p, cs):
    """P-III 型离均系数 Φp。

    注意：水文学中 p 为**超过频率**（设计频率），内部换算为累积概率 1-p。
    """
    if not 0 < p < 1:
        raise ValueError("p 必须在 (0, 1) 之间")
    if abs(cs) < 1e-9:
        return normal_quantile(1 - p)
    if cs > 0:
        alpha = 4.0 / cs ** 2
        if _HAS_SCIPY:
            g = gammaincinv(alpha, 1 - p)
            return (cs / 2) * g - 2 / cs
        z = normal_quantile(1 - p)
        return z + (z ** 2 - 1) * cs / 6 - (z ** 3 - 6 * z) * cs ** 2 / 36
    return -phi_p(1 - p, -cs)


def pearson3_value(p, mean, cv, cs):
    """由 P-III 型频率曲线求设计值 xp = x̄(1 + Cv·Φp)。"""
    return mean * (1 + cv * phi_p(p, cs))


def design_value_from_sample(x, p):
    """对样本做矩法估计后求指定超过频率 p 的设计值。"""
    m = moments(x)
    return {
        **m,
        "p": p,
        "Phi": phi_p(p, m["Cs"]),
        "xp": pearson3_value(p, m["mean"], m["Cv"], m["Cs"]),
    }


# ---------- 设计洪水放大 ----------
def same_frequency_ratios(Qmd, Qmp, Wd, Wp):
    """同频率放大倍比。

    Qmd/Qmp：典型/设计洪峰；
    Wd/Wp：典型/设计洪量，dict{days: volume}，如 {1: 0.8, 3: 2.0, 7: 4.0}。
    返回洪峰倍比与各时段（逐段相减）倍比。
    """
    ratios = {"peak": Qmp / Qmd}
    days = sorted(Wd)
    prev = 0
    for d in days:
        ratios[f"{prev}-{d}d"] = (Wp[d] - Wp.get(prev, 0.0)) / (Wd[d] - Wd.get(prev, 0.0))
        prev = d
    return ratios


def same_ratio_factors(Qmd, Qmp, Wd, Wp):
    """同倍比放大：分别给出按峰、按量的倍比。"""
    return {
        "by_peak": Qmp / Qmd,
        "by_volume": {d: Wp[d] / Wd[d] for d in Wd},
    }


# ---------- 推理公式 ----------
def reasoning_formula(S, n, mu, F, L, J, m, tol=1e-6, max_iter=200):
    """中国水科院推理公式（迭代求解）。

    S: 雨力；n: 暴雨递减指数；mu: 损失强度 mm/h；F: 流域面积 km²；
    L: 主河道长度 km；J: 河道平均比降（小数）；m: 汇流参数。
    返回 Qm(m³/s)、τ(h)、净雨强度 i(mm/h)。
    """
    Q = 1.0
    tau = 0.0
    i_net = 0.0
    for _ in range(max_iter):
        tau = 0.278 * L / (m * J ** (1 / 3) * Q ** 0.25)
        i_net = S / tau ** n - mu
        if i_net <= 0:
            return {"Qm": 0.0, "tau": tau, "i": i_net}
        q_new = 0.278 * i_net * F
        if abs(q_new - Q) / q_new < tol:
            Q = q_new
            break
        Q = q_new
    return {"Qm": Q, "tau": tau, "i": i_net}


# ---------- 径流 ----------
def runoff_depth(P_mm, alpha):
    """径流深 R = α·P（mm）。"""
    return alpha * P_mm


def runoff_volume(P_mm, alpha, area_km2):
    """径流总量（万 m³）：P(mm)×面积(km²)×α×0.1。"""
    return alpha * P_mm * area_km2 * 0.1


# ---------- 暴雨与下渗 ----------
def storm_intensity(S, n, t):
    """暴雨强度 i = S/t^n（mm/h，t 单位 h）。"""
    return S / t ** n


def horton_infiltration(f0, fc, k, t):
    """Horton 下渗率 f(t) = fc + (f0 - fc)·e^(-kt)（mm/h）。"""
    return fc + (f0 - fc) * math.exp(-k * t)


def return_period(p):
    """超过概率 p → 重现期 T = 1/p。"""
    return 1.0 / p


def exceedance_probability(T):
    """重现期 T → 超过概率 p = 1/T。"""
    return 1.0 / T


# ---------- 洪水演算 ----------
def muskingum_coefficients(K, x, dt):
    """马斯京根系数 C0、C1、C2。"""
    den = K * (1 - x) + 0.5 * dt
    return {
        "C0": (0.5 * dt - K * x) / den,
        "C1": (0.5 * dt + K * x) / den,
        "C2": (K * (1 - x) - 0.5 * dt) / den,
    }


def muskingum_route(inflow, K, x, dt, outflow0=None):
    """马斯京根洪水演算，返回出流序列。"""
    c = muskingum_coefficients(K, x, dt)
    out = []
    o_prev = inflow[0] if outflow0 is None else outflow0
    i_prev = inflow[0]
    for i in inflow:
        o = c["C0"] * i + c["C1"] * i_prev + c["C2"] * o_prev
        out.append(o)
        o_prev = o
        i_prev = i
    return out


def linear_reservoir_route(inflow, k, dt, outflow0=None):
    """线性水库演算：O2 = [O1(2k/dt - 1) + (I1 + I2)]/(2k/dt + 1)。"""
    out = []
    o_prev = inflow[0] if outflow0 is None else outflow0
    i_prev = inflow[0]
    for i in inflow:
        o = (o_prev * (2 * k / dt - 1) + (i_prev + i)) / (2 * k / dt + 1)
        out.append(o)
        o_prev = o
        i_prev = i
    return out


# ---------- 相关分析 ----------
def linear_regression(x, y):
    """一元线性相关：返回斜率、截距与相关系数 r。"""
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    syy = sum((yi - my) ** 2 for yi in y)
    slope = sxy / sxx
    return {
        "slope": slope,
        "intercept": my - slope * mx,
        "r": sxy / math.sqrt(sxx * syy),
    }


# ---------- P-III 适线曲线 ----------
def p3_curve(p_values, mean, cv, cs):
    """给出一组超过频率 p 对应的 P-III 曲线值，便于适线作图。"""
    return [(p, pearson3_value(p, mean, cv, cs)) for p in p_values]
