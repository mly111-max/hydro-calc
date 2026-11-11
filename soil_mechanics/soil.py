"""土力学计算工具

参考教材：《土力学》第 4 版（2023.11），河海大学《土力学》教材编写组，
高等教育出版社，ISBN 978-7-04-060662-1

涵盖：三相指标换算、渗流与有效应力、压缩与固结沉降、
抗剪强度、朗肯土压力、太沙基承载力、边坡稳定。
"""

import math

G = 9.81          # 由 g/cm³ 换算为 kN/m³ 的系数（1 g/cm³ = 9.81 kN/m³）
GAMMA_W = 9.81    # 水的重度 kN/m³


# ---------- 三相指标换算 ----------
def phase_relations(w, rho, rho_s=2.70, rho_w=1.0):
    """由含水率 w（小数）与天然密度 rho（g/cm³）换算其余指标。

    rho_s 为土粒密度（g/cm³，默认 2.70）；rho_w 为水的密度（g/cm³）。
    返回孔隙比 e、孔隙率 n、饱和度 Sr、干密度、饱和重度、有效重度等。
    """
    e = rho_s * (1 + w) / rho - 1
    n = e / (1 + e)
    Sr = w * rho_s / (e * rho_w)
    rho_d = rho / (1 + w)
    rho_sat = (rho_s + e * rho_w) / (1 + e)
    gamma = rho * G
    gamma_d = rho_d * G
    gamma_sat = rho_sat * G
    gamma_prime = gamma_sat - GAMMA_W
    return {
        "e": e, "n": n, "Sr": Sr,
        "rho_d": rho_d, "rho_sat": rho_sat,
        "gamma": gamma, "gamma_d": gamma_d,
        "gamma_sat": gamma_sat, "gamma_prime": gamma_prime,
    }


# ---------- 渗流与有效应力 ----------
def darcy(k, i, A=1.0):
    """达西定律 Q = k·i·A（m³/s）。k 单位 m/s，i 无量纲，A 单位 m²。"""
    return k * i * A


def critical_hydraulic_gradient(gamma_sat):
    """临界水力梯度 i_cr = (γsat - γw)/γw = γ'/γw（流土判别用）。"""
    return (gamma_sat - GAMMA_W) / GAMMA_W


def equivalent_permeability_horizontal(layers):
    """层状土水平等效渗透系数。layers = [(H, k), ...]，H 为层厚。"""
    total_h = sum(h for h, _ in layers)
    return sum(h * k for h, k in layers) / total_h


def equivalent_permeability_vertical(layers):
    """层状土垂直等效渗透系数。"""
    total_h = sum(h for h, _ in layers)
    return total_h / sum(h / k for h, k in layers)


def effective_stress(sigma, u):
    """有效应力 σ' = σ - u（kPa）。"""
    return sigma - u


# ---------- 压缩与固结沉降 ----------
def compression_coefficient(e1, e2, p1, p2):
    """压缩系数 a = (e1 - e2)/(p2 - p1)，压力单位需一致（如 MPa⁻¹）。"""
    return (e1 - e2) / (p2 - p1)


def compression_modulus(e1, a):
    """压缩模量 Es = (1 + e1)/a。"""
    return (1 + e1) / a


def settlement(a, e1, dp, H):
    """由压缩系数计算沉降 s = a/(1+e1)·Δp·H（a 与 Δp 压力单位一致，H 为 m）。"""
    return a / (1 + e1) * dp * H


def settlement_from_delta_e(delta_e, e1, H):
    """由孔隙比变化计算沉降 s = Δe/(1+e1)·H。"""
    return delta_e / (1 + e1) * H


def tv_from_u(U):
    """一维固结：由固结度 U 求时间因数 T_v（Terzaghi）。"""
    if U < 0.6:
        return math.pi / 4 * U ** 2
    return -0.9332 * math.log10(1 - U) - 0.0851


def u_from_tv(Tv):
    """一维固结：由时间因数 T_v 求固结度 U。"""
    if Tv <= math.pi / 4 * 0.36:
        return math.sqrt(4 * Tv / math.pi)
    return 1 - 10 ** (-(Tv + 0.0851) / 0.9332)


def consolidation_time(cv, H_drain, Tv):
    """固结时间 t = T_v·H²/cv。cv 与 H 的长度单位需一致。"""
    return Tv * H_drain ** 2 / cv


# ---------- 抗剪强度 ----------
def mohr_coulomb(c, sigma_n, phi_deg):
    """总应力抗剪强度 τf = c + σ·tanφ。"""
    return c + sigma_n * math.tan(math.radians(phi_deg))


def mohr_coulomb_effective(c_prime, sigma_prime, phi_prime_deg):
    """有效应力抗剪强度 τf = c' + σ'·tanφ'。"""
    return c_prime + sigma_prime * math.tan(math.radians(phi_prime_deg))


# ---------- 朗肯土压力 ----------
def rankine_coefficients(phi_deg):
    """朗肯主动、被动土压力系数 Ka、Kp。"""
    phi = math.radians(phi_deg)
    ka = math.tan(math.pi / 4 - phi / 2) ** 2
    kp = math.tan(math.pi / 4 + phi / 2) ** 2
    return ka, kp


def rankine_active(gamma, H, phi_deg, q=0.0):
    """朗肯主动土压力（无黏性土，可含均布超载 q）。

    返回 Ka、墙底强度 pa_bottom、合力 Ea、作用点距墙底高度 z。
    """
    ka, _ = rankine_coefficients(phi_deg)
    pa_bottom = ka * (gamma * H + q)
    ea = 0.5 * ka * gamma * H ** 2 + ka * q * H
    if ea == 0:
        z = 0.0
    else:
        z = (0.5 * ka * gamma * H ** 2 * H / 3 + ka * q * H * H / 2) / ea
    return {"Ka": ka, "pa_bottom": pa_bottom, "Ea": ea, "z": z}


def rankine_passive(gamma, H, phi_deg, q=0.0):
    """朗肯被动土压力合力 Ep。"""
    _, kp = rankine_coefficients(phi_deg)
    ep = 0.5 * kp * gamma * H ** 2 + kp * q * H
    return {"Kp": kp, "Ep": ep}


# ---------- 地基承载力（太沙基） ----------
def terzaghi_factors(phi_deg):
    """太沙基承载力系数 Nc、Nq、Nγ（整体剪切破坏）。"""
    phi = math.radians(phi_deg)
    if abs(phi) < 1e-9:
        return {"Nc": 5.7, "Nq": 1.0, "Ngamma": 0.0}
    a = math.exp((1.5 * math.pi - phi) * math.tan(phi))   # e^((3π/2-φ)·tanφ)
    nq = a / (2 * math.cos(math.pi / 4 + phi / 2) ** 2)
    nc = (nq - 1) / math.tan(phi)
    ngamma = 1.8 * (nq - 1) * math.tan(phi)
    return {"Nc": nc, "Nq": nq, "Ngamma": ngamma}


def terzaghi_bearing_capacity(c, gamma, B, D, phi_deg, FS=3.0):
    """太沙基极限承载力 pu = c·Nc + q·Nq + 0.5·γ·B·Nγ，返回 pu 与容许值 pu/FS。"""
    n = terzaghi_factors(phi_deg)
    q = gamma * D
    pu = c * n["Nc"] + q * n["Nq"] + 0.5 * gamma * B * n["Ngamma"]
    return {**n, "pu": pu, "qa": pu / FS}


# ---------- 边坡稳定 ----------
def infinite_slope_fs(c, gamma, H, beta_deg, phi_deg):
    """无限边坡（无渗流）稳定系数 Fs。"""
    beta = math.radians(beta_deg)
    phi = math.radians(phi_deg)
    drive = gamma * H * math.sin(beta) * math.cos(beta)
    resist = c + gamma * H * math.cos(beta) ** 2 * math.tan(phi)
    return resist / drive


def taylor_stability_number(c, gamma, H):
    """泰勒稳定数 Ns = c/(γH)（均质简单边坡初判用）。"""
    return c / (gamma * H)


# ---------- 附加应力 ----------
def boussinesq_point_stress(P, z, r):
    """布辛奈斯克竖向附加应力 σz = 3P/(2π)·z³/(r²+z²)^(5/2)，P 单位 kN。"""
    return 3 * P / (2 * math.pi) * z ** 3 / (r ** 2 + z ** 2) ** 2.5


def vertical_stress_rectangular(q, L, B, z, nx=60, ny=60):
    """矩形均布荷载中心下 z 深度处的竖向附加应力（数值积分布辛奈斯克解）。

    q: 均布荷载(kPa)；L、B: 矩形边长(m)；z: 深度(m)。
    """
    dx = L / nx
    dy = B / ny
    total = 0.0
    x0 = -L / 2 + dx / 2
    y0 = -B / 2 + dy / 2
    z3 = z ** 3
    for i in range(nx):
        x = x0 + i * dx
        for j in range(ny):
            y = y0 + j * dy
            r2 = x * x + y * y
            total += z3 / (r2 + z * z) ** 2.5
    return 3 * q / (2 * math.pi) * total * dx * dy


# ---------- 分层总和法沉降 ----------
def settlement_layers(layers):
    """分层总和法沉降。

    每层可用：
      {'H':H, 'e1':e1, 'a':a, 'dp':dp}  —— 由压缩系数计算；
      {'H':H, 'e1':e1, 'de':de}          —— 由孔隙比变化计算。
    返回总沉降 s（m）。
    """
    s = 0.0
    for layer in layers:
        if "de" in layer:
            s += settlement_from_delta_e(layer["de"], layer["e1"], layer["H"])
        else:
            s += settlement(layer["a"], layer["e1"], layer["dp"], layer["H"])
    return s


# ---------- 应力状态 ----------
def principal_stresses(sigma_x, sigma_z, tau_xz):
    """由一点应力状态求大、小主应力。"""
    avg = (sigma_x + sigma_z) / 2
    radius = math.sqrt(((sigma_x - sigma_z) / 2) ** 2 + tau_xz ** 2)
    return {"sigma1": avg + radius, "sigma3": avg - radius, "R": radius}


# ---------- 挡土墙稳定 ----------
def retaining_wall_stability(G, Ea, Ea_arm, G_arm, phi_base_deg, c_base=0.0, B_base=1.0):
    """重力式挡土墙抗滑 Ks、抗倾覆 Ko（简化）。"""
    ks = (G * math.tan(math.radians(phi_base_deg)) + c_base * B_base) / Ea
    ko = G * G_arm / (Ea * Ea_arm)
    return {"Ks": ks, "Ko": ko}


# ---------- 边坡条分法 ----------
def swedish_slice_fs(slices):
    """瑞典（费伦纽斯）条分法稳定系数。

    slices: [{'W':W,'alpha':α(°),'c':c,'phi':φ(°),'b':b,'u':u}, ...]
    """
    num = 0.0
    den = 0.0
    for s in slices:
        a = math.radians(s["alpha"])
        phi = math.radians(s["phi"])
        u = s.get("u", 0.0)
        num += (s["c"] * s["b"] + (s["W"] * math.cos(a) ** 2 - u * s["b"]) * math.tan(phi)) / math.cos(a)
        den += s["W"] * math.sin(a)
    return num / den


def bishop_slice_fs(slices, tol=1e-6, max_iter=100):
    """简化毕肖普条分法稳定系数（迭代求解）。

    slices 同 swedish_slice_fs。
    """
    fs = 1.2
    for _ in range(max_iter):
        num = 0.0
        den = 0.0
        for s in slices:
            a = math.radians(s["alpha"])
            phi = math.radians(s["phi"])
            u = s.get("u", 0.0)
            den += s["W"] * math.sin(a)
            num += (s["c"] * s["b"] + (s["W"] - u * s["b"]) * math.tan(phi)) / (
                math.cos(a) * (1 + math.tan(a) * math.tan(phi) / fs)
            )
        new_fs = num / den
        if abs(new_fs - fs) < tol:
            return new_fs
        fs = new_fs
    return fs
