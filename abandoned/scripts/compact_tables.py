import pathlib
p = pathlib.Path(r"D:\YohannaPaper\manuscript\manuscript.qmd")
txt = p.read_text(encoding="utf-8")
# Compact Table 5: keep 4 columns
old5 = """**Table 5. Density $y$ (points km⁻²) regressed on log area, $N=775$ LGAs.**

| Model | Intercept | log(area) | $\\rho$ / $\\lambda$ | AIC | LR vs OLS | $R^2$ / pseudo-$R^2$ |
|---|---|---|---|---|---|---:|
| OLS | 0.0605 (0.0090)*** | -0.0086 (0.0014)*** | — | -2485.2 | — | 0.048 |
| Lag (Eq. @eq-lag) | 0.0365 (0.0085)*** | -0.0052 (0.0013)*** | $\\rho=0.419$ (0.046)*** | **-2577.5** | 94.25*** | — |
| Error (Eq. @eq-error) | 0.0419 (0.0108)*** | -0.0058 (0.0017)*** | $\\lambda=0.419$ (0.047)*** | -2572.9 | 89.70*** | — |"""
new5 = """**Table 5. Density $y$ (points km⁻²) regressed on log area, $N=775$ LGAs.**

| Model | log(area) | $\\rho$ / $\\lambda$ | AIC |
|---|---|---|---:|
| OLS | -0.0086 (0.0014)*** | — | -2485.2 |
| Lag (Eq. @eq-lag) | -0.0052 (0.0013)*** | $\\rho=0.419$*** | **-2577.5** |
| Error (Eq. @eq-error) | -0.0058 (0.0017)*** | $\\lambda=0.419$*** | -2572.9 |"""
if old5 in txt:
    txt = txt.replace(old5, new5)
    print("Table5 compacted")
else:
    print("Table5 not found")
# Compact Table 6
old6 = """**Table 6. Density with climate, $N=34$ LGAs with ≥1 point and mapped state.**

| Model | log(area) | PRECTOT (mm) | T2M (°C) | $\\rho$ / $\\lambda$ | AIC | $R^2$ |
|---|---|---|---|---|---|---:|
| OLS | -0.0635 (0.0255)* | -0.000085 (0.000073) | -0.0378 (0.1166) | — | -10.51 | 0.239 |
| Lag | -0.0797 (0.0227)*** | -0.000135 (0.000064)* | -0.0464 (0.1005) | $\\rho=-0.438$ (0.180)* | **-12.39** | — |
| Error | -0.0656 (0.0181)*** | -0.000100 (0.000042)* | -0.0522 (0.0706) | $\\lambda=-0.476$ (0.180)** | **-12.75** | — |"""
new6 = """**Table 6. Density with climate, $N=34$ LGAs.**

| Model | log(area) | PRECTOT | $\\rho$ / $\\lambda$ | AIC |
|---|---|---|---|---:|
| OLS | -0.0635* | -0.000085 | — | -10.51 |
| Lag | -0.0797*** | -0.000135* | $\\rho=-0.438$* | **-12.39** |
| Error | -0.0656*** | -0.000100* | $\\lambda=-0.476$** | **-12.75** |"""
if old6 in txt:
    txt = txt.replace(old6, new6)
    print("Table6 compacted")
else:
    print("Table6 not found")
# Also shorten Discussion climate-smart paragraph by 20% (remove one sentence)
txt = txt.replace(
    "HH clusters in hot/dry Kano (27.3°C/404 mm, $\\rho_{T2M}=+0.44$) reflect fadama [@muhammed2022]; rainfall $\\rho=-0.31$ becomes $ -0.00010$ ($p=0.018$) after area/spatial correction (Table 6), implying 1,487 mm contrast →0.15 km⁻² (15% Tarauni). FAO frames water-scarcity raising plot value [@fao2023]; in humid PH benefits shift to cooling [@abubakar2023].",
    "HH clusters in hot/dry Kano reflect fadama [@muhammed2022]; rainfall becomes $ -0.00010$ ($p=0.018$) after correction (Table 6), implying 1,487 mm →0.15 km⁻² (15% Tarauni) [@fao2023]."
)
p.write_text(txt, encoding="utf-8")
print(f"new qmd words {len(txt.split())}")
