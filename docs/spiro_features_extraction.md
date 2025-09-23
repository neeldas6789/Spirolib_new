# Documentation: `spiro_features_extraction`

The `spiro_features_extraction` class provides a modular architecture for extracting advanced mathematical features from forced expiratory (FE) spirometry signals. It includes:

* Area under the Flow-Volume Loop (% predicted)
* Angle of Collapse (AC)
* Deflating balloon model

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
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height, race)
```

#### Methods

* `calc_AreaPred()`
  * Returns predicted AreaFE using demographic inputs.

* `calc_areaFE()`
  * Computes area under the FE curve using trapezoidal integration.

---

### Subclass: `angle_of_collapse`

Implements a data-driven geometric fitting model to compute the angle of collapse after PEF.

#### Initialization

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`
  * Constructs a piecewise linear model intersecting point `(x, y)`.

* `min_line_model_error(plotProcess=False)`
  * Finds best-fitting point minimizing squared error across post-PEF data. Set `plotProcess=True` to visualize iterations.

* `get_angle(x_p, y_p)`
  * Computes the geometric angle between two segments joined at `(x_p, y_p)`.

* `calc_AC(plotModel=False, plotProcess=False)`
  * Returns computed angle of collapse and error `Jmin`. Use `plotModel=True` to plot the fitted model.

---

### Subclass: `deflating_baloon`

Models the FE signal using second-order dynamics (deflating balloon analogy).

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
  * Prepares volume/flow signals by orienting RV/TLC and trimming after PEF.

* `reorient_model()`
  * Converts simulated model back to original coordinate system.

* `get_excitation_phase(T1, params)`
  * Handles the early excitation phase (up to PEF) for various excitation types.

* `calc_hypothesis(params)`
  * Simulates the flow-volume signal beyond the excitation phase using second-order ODE.

* `Cost_Function(params)`
  * Computes error between simulated and observed signals for optimizer.

* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  * Fits model via `differential_evolution`. Available `excitation_type` values:
    - `"Default"` (initial conditions at PEF, no explicit excitation)
    - `"Linear"`
    - `"Exponential pressure"`
    - `"Non linear"`
  * Populates:
    - `wn`, `zeta`, (`alpha`, `a0` if applicable)
    - `model_volume`, `model_flow`
    - Fit metrics: MSE and R² for volume and flow

* `run_simulation(sim_param, sim_type="", num_sims=4, percentage_step=10, plot_FVL_only=True)`
  * Performs sensitivity analysis by varying one parameter (`"zeta"` or `"omega"`).
  * Uses current model results to generate and plot simulated FVLs.

* `calc_FEV1_FVC()`
  * Calculates interpolated FEV1 and final FVC from model output.

* `plot_model(only_FVL, add_title_text)`
  * Plots original vs. simulated flow-volume and time-series data.

---

## Example Usage

```python
# Compute angle of collapse
ac = spiro_features_extraction.angle_of_collapse(volume, flow)
angle, cost = ac.calc_AC(plotModel=True)

# Compute AreaFE % predicted
af = spiro_features_extraction.areaFE(volume, flow, sex=1, age=35, height=170, race='Caucasian')
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()

# Fit balloon model with default excitation
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type="Default", plot_model=True)
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* `utilities` (custom plotting utility)

---

## References

* AreaFE: [DOI:10.2147/COPD.S51453]
* Angle of Collapse: [DOI:10.1186/1465-9921-14-131]

---

## License

This tool is intended for research and educational purposes. Validate clinically before diagnostic use.
