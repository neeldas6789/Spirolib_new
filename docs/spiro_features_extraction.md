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

Class for calculating AreaFE % predicted and actual area under the FE curve.

#### Initialization

```python
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height)
```

#### Methods

* `calc_AreaPred()`
  * Returns predicted AreaFE using ECCS93 demographic equations.
* `calc_areaFE()`
  * Computes actual area under the FE curve using trapezoidal integration.

---

### Subclass: `angle_of_collapse`

Implements a geometric fitting model to compute the angle of collapse after PEF.

#### Initialization

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`
  * Constructs a piecewise linear model intersecting at point `(x, y)`.
* `min_line_model_error(plotProcess=False)`
  * Finds the best-fitting intersection point minimizing mean squared error. Set `plotProcess=True` to visualize the fitting iterations.
* `get_angle(x_p, y_p)`
  * Computes the geometric angle between pre- and post-collapse segments at `(x_p, y_p)`.
* `calc_AC(plotModel=False, plotProcess=False)`
  * Returns `(angle_of_collapse, error)` and optionally plots the fitted model (`plotModel=True`) and/or the fitting process (`plotProcess=True`).

---

### Subclass: `deflating_baloon`

Models the FE signal using a second-order ODE (balloon deflation) framework.

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
  * Prepares oriented volume/flow signals for modeling.
* `reorient_model()`
  * Converts simulated signal back to original coordinates.
* `get_excitation_phase(T1, params)`
  * Handles the early (excitation) phase of expiration based on parameters.
* `calc_hypothesis(params)`
  * Simulates volume and flow trajectories for given ODE parameters.
* `Cost_Function(params)`
  * Computes combined volume and flow error to be minimized.
* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  * Fits the model using `scipy.optimize.differential_evolution`.  
  * **`excitation_type`** selects the modeling branch:
    * `"Linear"`, `"Exponential pressure"`, `"Non linear"` (legacy, less maintained)
    * `""` or any other string: default branch using initial conditions at PEF
  * Plots the original vs modeled signals when `plot_model=True`.
* `run_simulation(sim_param='zeta', sim_type="", num_sims=4, percentage_step=10, plot_FVL_only=True)`
  * Performs sensitivity analysis by varying one model parameter (`sim_param`) in steps of `percentage_step%`.  
  * `sim_type` indicates the excitation type used for model parameter selection in the simulation.
* `calc_FEV1_FVC()`
  * Computes FEV1 and FVC from the simulated volume trace.
* `plot_model(only_FVL, add_title_text)`
  * Generates comparative plots of original vs modeled signals.

---

## Excitation Types

The `run_model` method supports multiple excitation patterns:

* `"Linear"`: simple linear excitation (discarded/legacy)
* `"Exponential pressure"`: exponential pressure excitation (discarded/legacy)
* `"Non linear"`: non-linear excitation (older model)
* `""` (default): uses PEF-based initial conditions for deflation phase

---

## Example Usage

```python
# Compute angle of collapse
ac = spiro_features_extraction.angle_of_collapse(volume, flow)
angle, cost = ac.calc_AC(plotModel=True)

# Compute AreaFE % predicted
af = spiro_features_extraction.areaFE(volume, flow, sex=1, age=35, height=170)
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()

# Fit balloon model
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type="", plot_model=True)
```