# Documentation: `spiro_features_extraction`

The `spiro_features_extraction` class provides a modular architecture for extracting advanced mathematical features from forced expiratory (FE) spirometry signals. It includes:

* Area under the Flow–Volume Loop (% predicted)
* Angle of Collapse (AC)
* Deflating Balloon Model

All modules assume the FE signal is standardized and oriented such that:

* Volume is in litres (TLC at 0, RV positive)
* Flow is in litres/s and positive
* Signal is right‐skewed (i.e., expiratory flow directed positively)

---
## Class: `spiro_features_extraction`

Main container class encapsulating multiple feature extraction models.

---

### Subclass: `areaFE`
Calculates the area under the expiratory flow–volume loop and its predicted value using ECCS93 equations.

#### Initialization
```python
area = spiro_features_extraction.areaFE(
    FE_volume,    # 1D array of FE volumes
    FE_flow,      # 1D array of FE flows
    sex,          # 1 for male, 0 for female
    age,          # in years
    height,       # in cm
    race          # placeholder for future race-specific equations
)
```

#### Methods

* `calc_AreaPred()`
  - Returns predicted AreaFE (scalar) based on demographics.

* `calc_areaFE()`
  - Computes actual area under the FE curve via `numpy.trapz`.

---

### Subclass: `angle_of_collapse`
Computes the geometric “angle of collapse” after PEF using a piecewise‐linear fit.

#### Initialization
```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`
  - Builds a two‐segment linear model through `(x, y)`.

* `min_line_model_error(plotProcess=False)`
  - Scans all post‐PEF points to minimize squared error. Pass `plotProcess=True` to overlay intermediate fits.

* `get_angle(x_p, y_p)`
  - Returns the collapse angle at `(x_p, y_p)` in degrees.

* `calc_AC(plotModel=False, plotProcess=False)`
  - Returns `(angle_of_collapse, Jmin)`. Use `plotModel=True` to plot final fit, `plotProcess=True` to visualize fitting steps.

---

### Subclass: `deflating_baloon`
Models the FE loop as a second‐order “balloon” deflation system, fit via differential evolution.

#### Initialization
```python
db = spiro_features_extraction.deflating_baloon(
    FE_time,    # time vector for FE segment (s)
    FE_volume,  # volume vector for FE segment (L)
    FE_flow     # flow vector for FE segment (L/s)
)
```

#### Core Methods

* `orient_and_snip_signal()`
  - Orients volume/flow so RV=0, flow negative, then trims to post‐PEF.

* `reorient_model()`
  - Converts model output back to original coordinate system (RV positive, flow positive).

* `get_excitation_phase(T1, params)`
  - Computes early (pre‐PEF) segment `h1` and `h1_dash` based on `excitation_type` settings.

* `calc_hypothesis(params)`
  - Generates combined excitation + deflation hypothesis `(h, h_dash)` for candidate parameters.

* `Cost_Function(params)`
  - Returns scalar error between hypothesis and oriented data (volume & flow).

* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  - Fits the full balloon model via `scipy.optimize.differential_evolution`. 
  - Supported `excitation_type` values: `'Linear'`, `'Exponential pressure'`, `'Non linear'`, or default (`''`).
  - Stores optimized attributes: `wn`, `zeta`, (`alpha`, `a0` if used), and error metrics.

* `run_simulation(sim_param='zeta', num_sims=4, percentage_step=10, plot_FVL_only=True)`
  - Performs sensitivity analysis by varying one model parameter over a range. Plots multiple FVLs.

* `calc_FEV1_FVC()`
  - Interpolates 1 s FEV1 and final FVC from the model output.

* `plot_model(only_FVL, add_title_text)`
  - Generates side‐by‐side plots of measured vs. model volume/flow signals.

---

## Example Usage
```python
# Angle of Collapse
ac_mod = spiro_features_extraction.angle_of_collapse(volume, flow)
angle, cost = ac_mod.calc_AC(plotModel=True)

# AreaFE prediction vs. actual
area_mod = spiro_features_extraction.areaFE(volume, flow, sex=1, age=35, height=170, race=None)
area_pred = area_mod.calc_AreaPred()
area_act  = area_mod.calc_areaFE()

# Balloon model fit and sensitivity
db_mod = spiro_features_extraction.deflating_baloon(time, volume, flow)
db_mod.run_model(excitation_type='', plot_model=True)
db_mod.run_simulation(sim_param='zeta', num_sims=5)
```

---

## Dependencies
* `numpy`
* `matplotlib`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* Internal utility class `utilities` (for plotting in angle_of_collapse)

---

## References
* AreaFE: https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD
* Angle of Collapse: https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131
