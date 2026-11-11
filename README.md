# 水利三课计算工具包

面向《农田水利学》《工程水文学》《土力学》三门课程的计算函数库。纯 Python 标准库实现，无需联网、无第三方依赖，适合做课后作业的公式校核与结果验算。

## 环境要求

- Python 3.8 及以上
- 无第三方依赖（仅使用 `math`、`statistics`）

## 目录结构

```
water_calc/       农田水利学：灌水率、渠道输水损失、渠系水利用系数、梯形断面水力计算
hydrology/        工程水文学：频率分析、设计洪水、推理公式、汇流演算
soil_mechanics/   土力学：三相指标、渗透、固结沉降、强度与土压力、承载力、边坡稳定
```

每个目录下 `*.py` 是函数库，`demo.py` 是可直接运行的例题演示。

## 快速开始

直接用脚本（无需安装）：

```bash
python water_calc/demo.py
python hydrology/demo.py
python soil_mechanics/demo.py
```

在自己代码里调用：

```python
import sys
sys.path.insert(0, "water_calc")      # 或 hydrology / soil_mechanics
from canal import main_canal_segments

segs = main_canal_segments(lengths=[3.0, 2.0, 1.0], branch_gross=[0.9, 1.31, 1.13], A=1.3, m=0.35)
```

## 模块内容

### 农田水利学 `water_calc/canal.py`

| 功能 | 主要函数 |
|---|---|
| 渠道输水损失（σ、损失流量、毛流量、渠道水利用系数） | `sigma` `loss_flow` `gross_flow` `canal_efficiency` `canal_params` |
| 干渠分段推流、典型支渠效率、支渠设计流量 | `main_canal_segments` `typical_branch_efficiency` `branch_design_flow` |
| 作物需水量、灌溉定额、灌水率 | `crop_water_requirement` `irrigation_quota` `irrigation_application_rate` |
| 续灌/轮灌与加大流量 | `enlarged_flow` `rotation_design_flow` |
| 梯形断面、曼宁公式、正常水深、水力最优断面 | `trapezoid_geometry` `manning_discharge` `normal_depth` `hydraulic_best_ratio` |

### 工程水文学 `hydrology/hydro.py`

| 功能 | 主要函数 |
|---|---|
| 经验频率、矩法参数、P-Ⅲ 曲线与设计值 | `empirical_frequency` `moments` `phi_p` `pearson3_value` `design_value_from_sample` `p3_curve` |
| 同频率 / 同倍比放大 | `same_frequency_ratios` `same_ratio_factors` |
| 推理公式、暴雨强度、下渗 | `reasoning_formula` `storm_intensity` `horton_infiltration` |
| 径流深与径流总量 | `runoff_depth` `runoff_volume` |
| 洪水演算（马斯京根、线性水库） | `muskingum_coefficients` `muskingum_route` `linear_reservoir_route` |
| 重现期、线性相关 | `return_period` `exceedance_probability` `linear_regression` |

### 土力学 `soil_mechanics/soil.py`

| 功能 | 主要函数 |
|---|---|
| 三相指标、达西定律、等效渗透系数 | `phase_relations` `darcy` `equivalent_permeability_horizontal` `equivalent_permeability_vertical` |
| 有效应力、临界水力梯度 | `effective_stress` `critical_hydraulic_gradient` |
| 压缩性、分层总和法沉降、一维固结 | `compression_coefficient` `compression_modulus` `settlement` `settlement_layers` `consolidation_time` |
| 莫尔–库仑强度、主应力 | `mohr_coulomb` `mohr_coulomb_effective` `principal_stresses` |
| 朗肯土压力、挡墙稳定 | `rankine_active` `rankine_passive` `retaining_wall_stability` |
| 太沙基承载力、附加应力 | `terzaghi_bearing_capacity` `boussinesq_point_stress` `vertical_stress_rectangular` |
| 边坡稳定（无限边坡、瑞典条分、毕肖普） | `infinite_slope_fs` `taylor_stability_number` `swedish_slice_fs` `bishop_slice_fs` |

## Excel 模板

`templates/农田水利计算表.xlsx`：5 张表（参数、渠道输水损失、干渠分段推流、渠系水利用系数、梯形断面），黄色格填数、灰色格自动算，可直接用于课程作业与论文附录。数值已与 `water_calc` 中的例题结果核对一致。

## 单位约定

| 课程 | 单位 |
|---|---|
| 农田水利学 | 流量 m³/s、长度 km、面积 万亩 |
| 工程水文学 | 降雨/径流 mm、面积 km²、流量 m³/s、水量 万 m³ |
| 土力学 | 应力 kPa / MPa、重度 kN/m³ |

P-Ⅲ 频率曲线的 `p` 为**超过频率**（设计频率），内部按累积概率 `1-p` 计算。

## 教材依据

| 课程 | 教材 | 版次 | 主编 |
|---|---|---|---|
| 土力学 | 土力学 | 第 4 版（2023.11） | 河海大学《土力学》教材编写组 |
| 工程水文学 | 工程水文学 | 第 5 版（2020.12） | 徐向阳、陈元芳 |
| 农田水利学 | 农田水利学 | 第 2 版（2023.12） | 王春堂、王光辉 |

## 说明

- 公式按上述教材通用写法实现，结果用于课程作业的自查与对比。
- 经验参数（如土壤透水性系数 A、m）需按教材表格取用，代码中未内置的取值不要臆造。
- 未覆盖非恒定流、复杂边界条件等情形，不适用于工程设计与生产计算。
