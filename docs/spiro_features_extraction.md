# Documentation: `spiro_features_extraction`

The `spiro_features_extraction` class provides a modular architecture for extracting advanced mathematical features from forced expiratory (FE) spirometry signals. It includes:

* Area under the Flow-Volume Loop (% predicted)
* Angle of Collapse (AC)
* Deflating Balloon Model

All modules assume the FE signal is standardized and oriented such that:

* Volume is in litres (TLC at 0, RV positive)
* Flow is in litres/s and positive
* Signal is right-skewed (i.e., normal expiratory flow direction)

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
  * Computes area under the FE curve using trapezoidal integration.

---

### Subclass: `angle_of_collapse`

Implements a geometric fitting model to compute the angle of collapse after PEF.

#### Initialization

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`
  * Constructs a piecewise linear model intersecting point `(x, y)`.
* `min_line_model_error(plotProcess=False)`
  * Finds the point minimizing squared error to the original curve.
* `get_angle(x_p, y_p)`
  * Computes the geometric angle between two segments joined at `(x_p, y_p)`.
* `calc_AC(plotModel=False, plotProcess=False)`
  * Returns `(angle_of_collapse, error)`; use `plotModel=True` to visualize.

---

### Subclass: `deflating_baloon`

Models the FE signal using second-order ODE dynamics. Simulates the lungs as a deflating balloon.

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
  * Prepares volume/flow signals for modeling by standardizing orientation.
* `reorient_model()`
  * Reverts simulated signal to original coordinate system.
* `calc_hypothesis(params)`
  * Simulates the flow-volume signal using the current model parameters.
* `Cost_Function(params)`
  * Computes error between predicted and actual volume/flow to be minimized.
* `run_model(excitation_type="", plot_model=False, add_title_text="", plot_FVL_only=False)`
  * Fits model with `differential_evolution` and optionally plots results. The `excitation_type` argument is now retained for internal tracking; default behavior uses PEF-based initial conditions.
* `run_simulation(sim_param, sim_type, num_sims, percentage_step, plot_FVL_only)`
  * Performs sensitivity analysis by varying one model parameter; `sim_type` is for internal classification only.
* `calc_FEV1_FVC()`
  * Computes interpolated FEV1 and final FVC from model output.
* `plot_model(only_FVL, add_title_text)`
  * Plots comparison between actual and simulated flow/volume signals.

---

## Example Usage

```python
# Compute angle of collapse
ac = spiro_features_extraction.angle_of_collapse(volume, flow)
angle, error = ac.calc_AC(plotModel=True)

# Compute AreaFE % predicted
af = spiro_features_extraction.areaFE(volume, flow, sex=1, age=35, height=170)
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()

# Fit balloon model
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(plot_model=True)
# Sensitivity analysis (internal)
db.run_simulation(sim_param='zeta', sim_type='', num_sims=4, percentage_step=10)
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* `utilities` (custom plotting utility used inside `angle_of_collapse`)

---

## References

* AreaFE: [DOI:10.2147/COPD.S51453]
* Angle of Collapse: [DOI:10.1186/1465-9921-14-131]
