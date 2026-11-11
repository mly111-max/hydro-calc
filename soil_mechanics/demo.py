"""土力学工具示例，验证 soil.py。

运行：python soil_mechanics/demo.py
"""

from soil import (
    phase_relations, darcy, critical_hydraulic_gradient,
    equivalent_permeability_horizontal, equivalent_permeability_vertical,
    compression_coefficient, compression_modulus, settlement,
    tv_from_u, consolidation_time,
    mohr_coulomb, rankine_active, rankine_passive,
    terzaghi_bearing_capacity, infinite_slope_fs,
)


def main():
    print("=" * 60)
    print("土力学计算示例")
    print("=" * 60)

    r = phase_relations(w=0.20, rho=1.85, rho_s=2.70)
    print("\n[三相指标] w=20%, ρ=1.85 g/cm³, ρs=2.70")
    print(f"  e={r['e']:.3f}, n={r['n']:.3f}, Sr={r['Sr']:.3f}")
    print(f"  γ={r['gamma']:.2f}, γd={r['gamma_d']:.2f}, "
          f"γsat={r['gamma_sat']:.2f}, γ'={r['gamma_prime']:.2f} kN/m³")

    print("\n[渗流]")
    print(f"  达西 Q = {darcy(k=1e-4, i=0.5, A=2.0):.2e} m³/s")
    print(f"  临界梯度 i_cr = {critical_hydraulic_gradient(gamma_sat=19.5):.3f}")
    layers = [(2.0, 1e-4), (3.0, 2e-5)]
    print(f"  水平等效 k = {equivalent_permeability_horizontal(layers):.2e}")
    print(f"  垂直等效 k = {equivalent_permeability_vertical(layers):.2e}")

    print("\n[压缩与沉降] e1=0.95, e2=0.85, Δp=0.1 MPa(100 kPa), H=4 m")
    a = compression_coefficient(0.95, 0.85, 0.1, 0.2)   # MPa⁻¹
    es = compression_modulus(0.95, a)
    s = settlement(a, 0.95, 0.1, 4)
    print(f"  a={a:.3f} MPa⁻¹, Es={es:.3f} MPa, s={s*100:.2f} cm")

    print("\n[固结] U=80%")
    tv = tv_from_u(0.8)
    print(f"  Tv={tv:.4f}, t={consolidation_time(cv=2e-7, H_drain=2.0, Tv=tv)/86400:.1f} d")

    print("\n[抗剪强度] c=10 kPa, σn=100 kPa, φ=25°")
    print(f"  τf = {mohr_coulomb(10, 100, 25):.2f} kPa")

    print("\n[朗肯土压力] γ=18 kN/m³, H=5 m, φ=30°")
    act = rankine_active(18, 5, 30)
    pas = rankine_passive(18, 5, 30)
    print(f"  Ka={act['Ka']:.3f}, Ea={act['Ea']:.2f} kN/m, z={act['z']:.2f} m")
    print(f"  Kp={pas['Kp']:.3f}, Ep={pas['Ep']:.2f} kN/m")

    print("\n[太沙基承载力] c=10, γ=18, B=2, D=1.5, φ=30°")
    bc = terzaghi_bearing_capacity(10, 18, 2, 1.5, 30, FS=3.0)
    print(f"  Nc={bc['Nc']:.2f}, Nq={bc['Nq']:.2f}, Nγ={bc['Ngamma']:.2f}")
    print(f"  pu={bc['pu']:.2f} kPa, 容许 qa={bc['qa']:.2f} kPa")

    print("\n[边坡] c=10, γ=18, H=5, β=30°, φ=25°")
    print(f"  Fs = {infinite_slope_fs(10, 18, 5, 30, 25):.3f}")


if __name__ == "__main__":
    main()
