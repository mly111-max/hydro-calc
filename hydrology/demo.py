"""工程水文学工具示例，验证 hydro.py。

运行：python hydrology/demo.py
"""

from hydro import (
    empirical_frequency, moments, phi_p, pearson3_value,
    design_value_from_sample, same_frequency_ratios, same_ratio_factors,
    reasoning_formula, runoff_depth, runoff_volume,
)


def main():
    print("=" * 60)
    print("工程水文学计算示例")
    print("=" * 60)

    peaks = [1200, 980, 850, 760, 680, 600, 540, 480, 420, 380]
    n = len(peaks)
    print("\n[经验频率] 数学期望公式")
    for i, x in enumerate(sorted(peaks, reverse=True), start=1):
        print(f"  第{i}位 {x} m³/s, P={empirical_frequency(i, n):.3f}")

    print("\n[矩法统计参数]")
    m = moments(peaks)
    print(f"  均值={m['mean']:.1f}, Cv={m['Cv']:.3f}, Cs={m['Cs']:.3f}")

    print("\n[P-III 型设计值] p=1%（超过频率）")
    d = design_value_from_sample(peaks, 0.01)
    print(f"  Φp={d['Phi']:.3f}, 设计值 xp={d['xp']:.1f} m³/s")

    print("\n[同频率放大倍比]")
    ratios = same_frequency_ratios(
        Qmd=1200, Qmp=2500,
        Wd={1: 0.8, 3: 2.0, 7: 4.0},
        Wp={1: 1.6, 3: 4.2, 7: 8.0},
    )
    for k, v in ratios.items():
        print(f"  {k}: {v:.3f}")

    print("\n[同倍比放大倍比]")
    sr = same_ratio_factors(1200, 2500, {1: 0.8, 3: 2.0, 7: 4.0},
                            {1: 1.6, 3: 4.2, 7: 8.0})
    print(f"  按峰: {sr['by_peak']:.3f}, 按量: "
          + ", ".join(f"{d}d={v:.3f}" for d, v in sr["by_volume"].items()))

    print("\n[推理公式] S=80, n=0.6, μ=3 mm/h, F=50 km², L=12 km, J=0.005, m=0.8")
    r = reasoning_formula(80, 0.6, 3, 50, 12, 0.005, 0.8)
    print(f"  Qm={r['Qm']:.1f} m³/s, τ={r['tau']:.2f} h, 净雨强度={r['i']:.2f} mm/h")

    print("\n[径流] P=800 mm, α=0.45, 面积=200 km²")
    print(f"  径流深={runoff_depth(800, 0.45):.1f} mm, "
          f"径流总量={runoff_volume(800, 0.45, 200):.1f} 万m³")


if __name__ == "__main__":
    main()
