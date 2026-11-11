"""复现两道农田水利学作业题，验证 canal.py 的计算结果。

运行：python water_calc/demo.py
"""

from canal import (canal_params, branch_design_flow,
                   main_canal_segments, typical_branch_efficiency)


def example_1():
    """简答题：典型支渠 → 各支渠 → 干渠设计流量。"""
    print("=" * 64)
    print("第1题（简答题）：干、支渠道设计流量")
    print("=" * 64)
    q = 0.8            # m³/(s·万亩)
    eta_field = 0.95
    A, m = 1.9, 0.4    # 中壤土

    r = typical_branch_efficiency(
        A, m, q,
        area_total=1.08, n_dou=6, n_nong=10,
        L_zhiqu=4.0, L_dou=1.8, L_nong=0.8,
        eta_field=eta_field,
    )
    print("\n[典型支渠(三支) 各级效率]")
    print(f"  农渠净流量 Q农净 = {r['Q_nong_net']:.5f} m³/s，η农 = {r['eta_nong']:.4f}")
    print(f"  斗渠净流量 Q斗净 = {r['Q_dou_net']:.5f} m³/s，η斗 = {r['eta_dou']:.4f}")
    print(f"  支渠净流量 Q支净 = {r['Q_zhi_net']:.5f} m³/s，η支 = {r['eta_zhi']:.4f}")
    print(f"  渠系水利用系数 η系 = {r['eta_system']:.4f}")

    eta_sub = eta_field * r["eta_nong"] * r["eta_dou"]
    branches = [("一支", 4.2, 0.85), ("二支", 4.6, 1.24), ("三支", 4.0, 1.08)]

    print("\n[各支渠设计流量]")
    total_gross = 0.0
    for name, L, area in branches:
        p = branch_design_flow(A, m, q, area, L, eta_sub)
        total_gross += p["Q_gross"]
        print(f"  {name}: L={L}km, A={area}万亩, Q净={p['Q_net']:.3f}, "
              f"σ={p['sigma']:.5f}, Q损={p['Q_loss']:.3f}, "
              f"Q设(毛)={p['Q_gross']:.3f} m³/s")

    pm = canal_params(A, m, total_gross, 5.7)
    print("\n[干渠]")
    print(f"  Q净={pm['Q_net']:.3f} m³/s, σ={pm['sigma']:.5f}, "
          f"Q损={pm['Q_loss']:.3f}, 渠首设计流量 Q设={pm['Q_gross']:.3f} m³/s")
    print("\n结论：干渠渠首约 3.56 m³/s；一支 0.90、二支 1.31、三支 1.13 m³/s。")


def example_2():
    """干渠分三段：由下游向上游逐段推算设计流量。"""
    print("\n" + "=" * 64)
    print("第2题：干渠各段设计流量（重壤土 A=1.3, m=0.35）")
    print("=" * 64)
    lengths = [3.0, 2.0, 1.0]           # OA, AB, BC
    branch_gross = [3.0, 2.0, 1.6]      # 支一、支二、支三毛流量
    rows = main_canal_segments(lengths, branch_gross, A=1.3, m=0.35)

    print("\n[各段结果]")
    for name, p in zip(["OA", "AB", "BC"], rows):
        print(f"  {name}段: L={p['L']}km, Q净={p['Q_net']:.3f}, "
              f"σ={p['sigma']:.5f}, Q损={p['Q_loss']:.3f}, "
              f"设计流量 Q设={p['Q_gross']:.3f} m³/s")
    print("\n结论：OA 6.81、AB 3.68、BC 1.62 m³/s。")


if __name__ == "__main__":
    example_1()
    example_2()
