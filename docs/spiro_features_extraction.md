# Documentation: `spiro_features_extraction`

The `spiro_features_extraction` class provides a modular architecture for extracting advanced mathematical features from forced expiratory (FE) spirometry signals. It includes:

* Area under the Flow-Volume Loop (% predicted)
* Angle of Collapse (AC)
* Deflating Balloon Model

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
  * Constructs a piecewise linear model intersecting at `(x, y)`.
* `min_line_model_error(plotProcess=False)`
  * Finds the best-fitting point minimizing squared error; set `plotProcess=True` to visualize.
* `get_angle(x_p, y_p)`
  * Computes the geometric angle between segments joined at `(x_p, y_p)`.
* `calc_AC(plotModel=False, plotProcess=False)`
  * Returns `(angle, error)`; `plotModel=True` to show the fitted model.

---

### Subclass: `deflating_baloon`

Models the FE signal using a second-order ODE (deflating balloon analogy).

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
  * Prepares volume/flow signals for modeling by standardizing orientation.
* `reorient_model()`
  * Converts the simulated signal back to original axes (RV→0, TLC→max).
* `get_excitation_phase(T1, params)`
  * Handles the early excitation phase based on `excitation_type`.
* `calc_hypothesis(params)`
  * Simulates the deflation-phase volume and flow using supplied parameters.
* `Cost_Function(params)`
  * Computes the fitting error between model and actual FE signals.
* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  * Fits the model using `differential_evolution`. Supported `excitation_type` values:
    - `"Linear"`, `"Exponential pressure"`, `"Non linear"` (legacy support)
    - `""` (default): uses initial conditions at PEF for excitation.
* `run_simulation(sim_param="zeta", sim_type="", num_sims=4, percentage_step=10, plot_FVL_only=True)`
  * Performs sensitivity analysis by varying one model parameter and plotting results.
* `calc_FEV1_FVC()`
  * Computes interpolated FEV1 and FVC from the simulated output.
* `plot_model(only_FVL, add_title_text)`
  * Plots original vs. simulated FVL, volume–time, and flow–time.

---

## Excitation Types

The `excitation_type` parameter in `run_model()` controls how the initial (excitation) phase is modeled:

* `"Linear"`: linear increase to PEF (legacy)
* `"Exponential pressure"`: exponential pressure-based excitation (legacy)
* `"Non linear"`: non-linear excitation (legacy)
* `""` (empty string): default PEF-based initial conditions

Each option influences `get_excitation_phase()` behavior before the deflation model.

---

## Example Usage

```python
# Compute angle of collapse
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
angle, err = ac.calc_AC(plotModel=True)

# Compute AreaFE % predicted
af = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex=1, age=35, height=170)
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()

# Fit deflating balloon model
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
db.run_model(excitation_type="", plot_model=True)

# Sensitivity simulation
db.run_simulation(sim_param='zeta', sim_type='', num_sims=5, percentage_step=10, plot_FVL_only=True)
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* `utilities` (custom plotting helper)

---

## References

* AreaFE: [DOI:10.2147/COPD.S51453](https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD)
* Angle of Collapse: [DOI:10.1186/1465-9921-14-131](https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131)

---

## Licensing

This tool is intended for research and educational use. Ensure clinical validation before diagnostic application.
