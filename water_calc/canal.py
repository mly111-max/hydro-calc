"""农田水利学 —— 渠道输水损失与设计流量计算工具

参考教材：《农田水利学》第 2 版（2023.12），王春堂、王光辉，
中国水利水电出版社，ISBN 978-7-5226-1063-4

核心公式：
    sigma = A / (100 * Q_net ** m)      # 每公里损失系数，Q_net 单位 m³/s
    Q_loss = sigma * L * Q_net
    Q_gross = Q_net + Q_loss = Q_net * (1 + sigma * L)
    eta_canal = Q_net / Q_gross = 1 / (1 + sigma * L)
"""

import math

# 教材中的土壤透水性参数（仅收录题目已确认的两种，其余按教材参数表补充）
SOIL = {
    "重壤土": {"A": 1.3, "m": 0.35},
    "中壤土": {"A": 1.9, "m": 0.40},
}


def sigma(A: float, m: float, Q_net: float) -> float:
    """每公里渠道输水损失系数（无量纲，除以 100 后为小数）。"""
    if Q_net <= 0:
        raise ValueError("Q_net 必须为正数")
    return A / (100.0 * Q_net ** m)


def loss_flow(A: float, m: float, Q_net: float, L: float) -> float:
    """渠道输水损失流量 Q损（m³/s）。"""
    return sigma(A, m, Q_net) * L * Q_net


def gross_flow(A: float, m: float, Q_net: float, L: float) -> float:
    """渠道毛流量 Q毛（m³/s）。"""
    return Q_net + loss_flow(A, m, Q_net, L)


def canal_efficiency(A: float, m: float, Q_net: float, L: float) -> float:
    """渠道水利用系数 η = Q净 / Q毛。"""
    return 1.0 / (1.0 + sigma(A, m, Q_net) * L)


def canal_params(A: float, m: float, Q_net: float, L: float) -> dict:
    """一次性返回渠道的净流量、σ、损失、毛流量与水利用系数。"""
    s = sigma(A, m, Q_net)
    q_loss = s * L * Q_net
    q_gross = Q_net + q_loss
    return {
        "Q_net": Q_net,
        "sigma": s,
        "L": L,
        "Q_loss": q_loss,
        "Q_gross": q_gross,
        "eta": Q_net / q_gross,
    }


def main_canal_segments(lengths, branch_gross, A: float, m: float) -> list:
    """干渠分段由下游向上游推算设计流量。

    参数：
        lengths      —— 各段长度 km，按“渠首→渠尾”顺序，如 [3, 2, 1]
        branch_gross —— 各段末端分出的支渠毛流量 m³/s，如 [3.0, 2.0, 1.6]
        A, m         —— 土壤透水性参数
    返回：
        每段一个 dict（含 Q_net、sigma、Q_loss、Q_gross），顺序同输入。
    """
    n = len(lengths)
    if len(branch_gross) != n:
        raise ValueError("段数与支渠数必须一致")

    Q_net = [0.0] * n
    # 最下游一段的净流量 = 该段末端支渠毛流量
    Q_net[-1] = branch_gross[-1]
    # 向上游逐段累加：本段净流量 = 本段支渠毛流量 + 下游段毛流量
    for i in range(n - 2, -1, -1):
        Q_net[i] = branch_gross[i] + gross_flow(A, m, Q_net[i + 1], lengths[i + 1])

    rows = []
    for i in range(n):
        p = canal_params(A, m, Q_net[i], lengths[i])
        p["segment"] = i + 1
        rows.append(p)
    return rows


def typical_branch_efficiency(A: float, m: float, q: float,
                              area_total: float, n_dou: int, n_nong: int,
                              L_zhiqu: float, L_dou: float, L_nong: float,
                              eta_field: float) -> dict:
    """由典型支渠（支—斗—农—田）逐级推算渠系水利用系数。

    参数：
        q           —— 设计灌水率 m³/(s·万亩)
        area_total  —— 典型支渠控制面积 万亩
        n_dou       —— 斗渠条数
        n_nong      —— 每条斗渠下的农渠条数
        L_zhiqu     —— 支渠长度 km
        L_dou       —— 斗渠长度 km
        L_nong      —— 农渠长度 km
        eta_field   —— 田间水利用系数
    返回：
        dict，含各级净流量、渠道水利用系数与综合渠系水利用系数 eta_system。
    """
    A_nong = area_total / (n_dou * n_nong)          # 每条农渠控制面积
    Q_field_net = q * A_nong                        # 田间净流量
    Q_nong_net = Q_field_net / eta_field            # 农渠净流量
    eta_nong = canal_efficiency(A, m, Q_nong_net, L_nong)
    Q_dou_net = n_nong * Q_nong_net / eta_nong      # 斗渠净流量
    eta_dou = canal_efficiency(A, m, Q_dou_net, L_dou)
    Q_zhi_net = n_dou * Q_dou_net / eta_dou         # 支渠净流量
    eta_zhi = canal_efficiency(A, m, Q_zhi_net, L_zhiqu)
    eta_system = eta_zhi * eta_dou * eta_nong * eta_field

    return {
        "A_nong": A_nong,
        "Q_field_net": Q_field_net,
        "Q_nong_net": Q_nong_net,
        "eta_nong": eta_nong,
        "Q_dou_net": Q_dou_net,
        "eta_dou": eta_dou,
        "Q_zhi_net": Q_zhi_net,
        "eta_zhi": eta_zhi,
        "eta_system": eta_system,
    }


def branch_design_flow(A: float, m: float, q: float, area: float,
                       L_branch: float, eta_sub: float) -> dict:
    """单条支渠设计流量。

    eta_sub = η田·η农·η斗（支渠以下各级效率，支渠自身损失单独按长度计）。
    """
    Q_net = q * area / eta_sub
    return canal_params(A, m, Q_net, L_branch)


# ---------- 作物需水与灌溉制度 ----------
def crop_water_requirement(kc, et0):
    """作物需水量 ET = Kc·ET0（mm/d 或 mm）。"""
    return kc * et0


def irrigation_quota(et, pe=0.0, gw=0.0):
    """净灌溉定额 M净 = ET - Pe - Gw（mm），不小于 0。"""
    return max(et - pe - gw, 0.0)


def irrigation_application_rate(alpha, m, T, eta=1.0, m_unit="mm"):
    """设计灌水率 q（m³/(s·万亩)）。

    alpha: 种植比；T: 灌水延续时间(d)；eta: 灌溉水利用系数。
    m_unit='mm'   时 m 为灌水定额(mm)，q = 0.07716·α·m/(T·η)；
    m_unit='m3mu' 时 m 为灌水定额(m³/亩)，q = 0.11574·α·m/(T·η)。
    """
    k = 0.07716 if m_unit == "mm" else 0.11574
    return k * alpha * m / (T * eta)


def enlarged_flow(q_design, factor=1.25):
    """加大流量 = 设计流量 × 加大系数。"""
    return q_design * factor


def rotation_design_flow(q_continuous, n_groups):
    """轮灌渠道设计流量 = 续灌流量 × 轮灌组数。"""
    return q_continuous * n_groups


# ---------- 渠道断面水力计算 ----------
def trapezoid_geometry(b, h, m):
    """梯形断面几何：面积 A、湿周 P、水面宽 Bw、水力半径 R。"""
    A = (b + m * h) * h
    P = b + 2 * h * math.sqrt(1 + m * m)
    Bw = b + 2 * m * h
    return {"A": A, "P": P, "Bw": Bw, "R": A / P}


def manning_discharge(n, A, R, S):
    """曼宁公式 Q = (1/n)·A·R^(2/3)·S^(1/2)。"""
    return A * R ** (2 / 3) * math.sqrt(S) / n


def hydraulic_best_ratio(m):
    """梯形水力最优断面宽深比 b/h = 2(√(1+m²) - m)。"""
    return 2 * (math.sqrt(1 + m * m) - m)


def normal_depth(Q, n, m, S, b, h_min=0.01, h_max=20.0, tol=1e-6):
    """已知底宽 b，用二分法求正常水深 h（满足曼宁公式）。"""
    def f(h):
        g = trapezoid_geometry(b, h, m)
        return manning_discharge(n, g["A"], g["R"], S) - Q

    lo, hi = h_min, h_max
    if f(lo) >= 0:
        return lo
    if f(hi) <= 0:
        raise ValueError("h_max 过小，未找到正常水深")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)
