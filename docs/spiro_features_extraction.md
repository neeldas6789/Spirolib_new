# spiro_features_extraction

The `spiro_features_extraction` module implements mathematical models to extract advanced features from forced expiratory (FE) spirometry signals. It provides:

- Area under the Flow–Volume Loop (% predicted)
- Angle of Collapse (AC)
- Deflating Balloon model parameters (zeta, ω)

**Assumptions**

- Volume in litres (TLC at 0, RV > 0)
- Flow in litres/sec (FE loop right-skewed)
- Time in seconds
- Signals are properly shifted and standardized

---

## Class: `spiro_features_extraction`

Container class; use its nested classes to compute individual features.

### Subclass: `areaFE`

Calculates the area under the FE loop and its predicted value using ECCS93 reference equations.

#### Initialization
```python
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height)
```

- `FE_volume`, `FE_flow`: 1D arrays of the FE signal
- `sex`: 1 = male, 0 = female
- `age`: in years
- `height`: in cm

#### Methods
- `calc_areaFE()`
  - Returns AUC of the flow–volume loop via `np.trapz()`.
- `calc_AreaPred()`
  - Calculates predicted AUC using ECCS93 equations; returns `None` + warning if demographics missing.

---

### Subclass: `angle_of_collapse`

Fits a two-line model post-PEF to compute the geometric collapse angle.

#### Initialization
```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

- Automatically slices the signal after PEF.

#### Methods
- `generate_linemodel(x, y, index)`
  - Builds piecewise linear model crossing at `(x, y)`.
- `min_line_model_error(plotProcess=False)`
  - Scans all candidate points, returns `(x_hat, y_hat, Jmin, idx)`; set `plotProcess=True` to visualize.
- `get_angle(x_p, y_p)`
  - Computes the angle between the two line segments.
- `calc_AC(plotModel=False, plotProcess=False)`
  - Returns `(angle, Jmin)`; `plotModel=True` overlays best-fitting lines, `plotProcess=True` shows intermediate fits.

---

### Subclass: `deflating_baloon`

Models the expiration as a second-order dynamic ‘balloon’ deflation; fits parameters via differential evolution.

#### Initialization
```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

- `FE_time`, `FE_volume`, `FE_flow`: arrays for the FE phase (shifted so t0=0).

#### Core Methods
- `orient_and_snip_signal()`
  - Orients volume and flow for model fitting (RV→0, flow negative deflation).
- `get_excitation_phase(T1, params)`
  - Computes the pre-PEF (excitation) segment for given parameters.
- `calc_hypothesis(params)`
  - Generates model volume & flow arrays based on `wn`, `zeta`, and (for some modes) `alpha`, `a0`.
- `Cost_Function(params)`
  - Error metric combining volume and flow differences.
- `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  - Fits model via `scipy.optimize.differential_evolution`. The `excitation_type` argument must be one of:
    - `"Linear"`
    - `"Exponential pressure"`
    - `"Non linear"`
    - `""` (default behavior: single-phase ODE starting at PEF)
  - Different bounds and initial conditions are applied based on the chosen type.
  - `plot_model=True` displays the fitted vs. original loop/time series.
- `run_simulation(sim_param='zeta', sim_type='', num_sims=4, percentage_step=10, plot_FVL_only=True)`
  - Varies one parameter (`'zeta'` or `'omega'`), runs multiple fits, and overlays simulated loops.
- `calc_FEV1_FVC()`
  - Interpolates FEV1 at 1 s and computes FVC from the model output.
- `plot_model(only_FVL, add_title_text)`
  - Lower-level plotting utility for original vs. simulated signals.


**Note:** The `excitation_type` argument actively alters the optimization strategy and model form. Pass an empty string (`""`) for the default PEF-driven model.

---

## Example Usage
```python
# AreaFE
af = spiro_features_extraction.areaFE(vol, flow, sex=1, age=40, height=170)
print(af.calc_areaFE(), af.calc_AreaPred())

# Angle of collapse
ac = spiro_features_extraction.angle_of_collapse(vol, flow)
angle, cost = ac.calc_AC(plotModel=True)

# Deflating balloon
db = spiro_features_extraction.deflating_baloon(time, vol, flow)
db.run_model(excitation_type='', plot_model=True)
w, zeta = db.wn, db.zeta
```

---

## Dependencies
- numpy
- matplotlib
- scipy (differential_evolution)
- sklearn.metrics (for MSE, R²)

---

## References
- AreaFE: https://doi.org/10.2147/COPD.S51453
- Angle of Collapse: https://doi.org/10.1186/1465-9921-14-131
