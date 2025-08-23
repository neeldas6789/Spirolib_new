# spirolib: spiro_features_extraction

The `spiro_features_extraction` class provides advanced mathematical models to extract features from forced expiratory (FE) spirometry signals. It supports:

- Area under the Flow-Volume Loop (% predicted)
- Angle of Collapse (AC)
- Deflating Balloon (second-order ODE model)

All modules assume the FE signal is:

- Volume in litres (TLC at 0, RV positive)
- Flow in litres/s (positive)
- Right-skewed flow-volume loop

---

## Class: `spiro_features_extraction`
Container for multiple feature-extraction submodels.

### Subclass: `areaFE`
Calculates actual and predicted area under the FE loop using ECCS93 reference equations.

#### Initialization
```python
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height)
```

#### Methods
- `calc_AreaPred()`
  - Returns predicted AreaFE based on sex, age, height.
- `calc_areaFE()`
  - Computes actual area under FE curve via trapezoidal integration.

---

### Subclass: `angle_of_collapse`
Computes the geometric Angle of Collapse after peak expiratory flow (PEF) by minimizing piecewise-linear model error.

#### Initialization
```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods
- `generate_linemodel(x, y, index)`
  - Builds a two-segment linear approximation through point `(x,y)`.
- `min_line_model_error(plotProcess=False)`
  - Iterates post-PEF points to find the best fit; set `plotProcess=True` to visualize.
- `get_angle(x_p, y_p)`
  - Computes the angle between the two line segments joined at `(x_p, y_p)`.
- `calc_AC(plotModel=False, plotProcess=False)`
  - Returns `(angle, error)`. Use `plotModel=True` to overlay fitted model, `plotProcess=True` to display fitting steps.

---

### Subclass: `deflating_baloon`
Models the deflation phase of FE as a damped oscillator (deflating balloon).

#### Initialization
```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods
- `orient_and_snip_signal()`
  - Prepares and orients data for modeling (RV→0, TLC→max, flow→negative).
- `reorient_model()`
  - Converts simulated output back to original orientation.
- `get_excitation_phase(T1, params)`
  - Handles early excitation phase (default uses actual FE start/PEF).  
- `calc_hypothesis(params)`
  - Simulates volume/flow using ODE parameters `[wn, zeta]`.
- `Cost_Function(params)`
  - Sum of squared errors between model and actual data.
- `run_model(excitation_type, plot_model=False, ...)`
  - Fits the model via `scipy.optimize.differential_evolution`.  
  - Note: only the default PEF-based start is actively modeled; other `excitation_type` options remain for internal tracking.
- `run_simulation(sim_param, num_sims, percentage_step, plot_FVL_only)`
  - Varies one parameter (e.g. zeta) to assess sensitivity.
- `calc_FEV1_FVC()`
  - Interpolates FEV1 at 1 s and final FVC from the simulated curve.
- `plot_model(only_FVL, add_title_text)`
  - Plots original vs. simulated flow-volume and time series.

---

## Optimization & Metrics
- All fits use `scipy.optimize.differential_evolution`.
- Fit quality metrics: MSE and R² for volume and flow.

---

## Example
```python
# AreaFE
af = spiro_features_extraction.areaFE(vol, flow, sex=1, age=35, height=170)
print(af.calc_areaFE(), af.calc_AreaPred())

# Angle of Collapse
ac = spiro_features_extraction.angle_of_collapse(vol, flow)
angle, cost = ac.calc_AC(plotModel=True)

# Deflating balloon
db = spiro_features_extraction.deflating_baloon(time, vol, flow)
db.run_model(excitation_type="", plot_model=True)
```

---

## Dependencies
- numpy
- matplotlib
- scipy.optimize.differential_evolution
- sklearn.metrics (MSE, R²)
- `.utilities` (for consistent plotting)

---

## References
- AreaFE DOI:10.2147/COPD.S51453
- Angle of Collapse DOI:10.1186/1465-9921-14-131