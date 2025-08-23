# Documentation: `spiro_features_extraction`

The `spiro_features_extraction` class provides a modular architecture for extracting advanced mathematical features from forced expiratory (FE) spirometry signals. It includes:

* Area under the Flow-Volume Loop (% predicted)
* Angle of Collapse (AC)
* Deflating Baloon Model

All modules assume the FE signal is standardized and oriented such that:

* Volume is in litres (TLC at 0, RV positive)
* Flow is in litres/s and positive
* Signal is right-skewed (normal expiratory flow direction)

---

## Class: `spiro_features_extraction`

Main container class encapsulating multiple feature extraction models.

---

### Subclass: `areaFE`

Calculates the area under the expiratory flow-volume loop and its predicted value using ECCS93 equations.

#### Initialization

```python
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height)
```

#### Methods

* `calc_AreaPred()`
  * Returns predicted AreaFE using demographic inputs.

* `calc_areaFE()`
  * Computes area under the FE curve via trapezoidal integration.

---

### Subclass: `angle_of_collapse`

Implements a geometric fitting model to compute the angle of collapse post-PEF.

#### Initialization

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`
* `min_line_model_error(plotProcess=False)`
* `get_angle(x_p, y_p)`
* `calc_AC(plotModel=False, plotProcess=False)`
  * Returns `(angle_of_collapse, Jmin)`. Use `plotModel=True` or `plotProcess=True` to visualize.

---

### Subclass: `deflating_baloon`

Models the FE signal dynamics using a second-order ODE (deflating balloon analogy).

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
* `reorient_model()`
* `get_excitation_phase(T1, params)`
* `calc_hypothesis(params)`
* `Cost_Function(params)`
* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  * Fits model with `differential_evolution` for the specified `excitation_type` (`"Linear"`, `"Exponential pressure"`, `"Non linear"`, or default). Plots results when `plot_model=True`.
* `run_simulation(sim_param='zeta', sim_type="", num_sims=4, percentage_step=10, plot_FVL_only=True)`
  * Varies one parameter (`sim_param`) in simulation, optionally specifying `sim_type` (e.g., `"Exponential pressure"`).
* `calc_FEV1_FVC()`
* `plot_model(only_FVL, add_title_text)`

---

## Optimization Notes

All fitting uses `scipy.optimize.differential_evolution`.  Fit metrics include:

* Mean Squared Error (MSE)
* R² Score (volume and flow)

---

## Example Usage

```python
# Angle of collapse
ac = spiro_features_extraction.angle_of_collapse(volume, flow)
angle, cost = ac.calc_AC(plotModel=True)

# AreaFE % predicted
af = spiro_features_extraction.areaFE(volume, flow, sex=1, age=35, height=170)
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()

# Deflating balloon model
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type="Non linear", plot_model=True, add_title_text="Test", plot_FVL_only=False)
db.run_simulation(sim_param='zeta', sim_type='', num_sims=5, percentage_step=10, plot_FVL_only=True)
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* `utilities` (for plotting)

Ensure these are installed before use.

---

## References

* AreaFE: https://doi.org/10.2147/COPD.S51453
* Angle of Collapse: https://doi.org/10.1186/1465-9921-14-131

---

## Licensing

Intended for research and education; validate clinically before diagnostic use.