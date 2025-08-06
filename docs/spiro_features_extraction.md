# Documentation: `spiro_features_extraction`

The `spiro_features_extraction` class provides a modular architecture for extracting advanced mathematical features from forced expiratory (FE) spirometry signals. It includes:

* **AreaFE % predicted** (https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD)
* **Angle of Collapse (AC)** (https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131)
* **Deflating Balloon Model**

> **Note:** FE = Forced Expiratory manoeuvre; signal must be standardized and oriented.

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
  * Computes actual area under the FE curve (trapezoidal rule).

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
  * Finds the best-fitting post-PEF point minimizing squared error.

* `get_angle(x_p, y_p)`
  * Computes geometric angle between two line segments at `(x_p, y_p)`.

* `calc_AC(plotModel=False, plotProcess=False)`
  * Returns `(angle, error)`; optionally plots model (`plotModel`) and fitting process (`plotProcess`).

---

### Subclass: `deflating_baloon`

Models the FE signal using a second-order differential equation (deflating balloon analogy).

#### Initialization
```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`  
  Prepares and snips volume/flow data around PEF for modeling.

* `reorient_model()`  
  Reverts simulated model output to original coordinate orientation.

* `get_excitation_phase(T1, params)`  
  Handles the initial excitation phase before balloon deflation.

* `calc_hypothesis(params)`  
  Simulates volume & flow trajectories using parameters `[wn, zeta, ...]`.

* `Cost_Function(params)`  
  Objective function for model fitting (volume & flow error).

* `run_model(excitation_type="", plot_model=False, add_title_text="", plot_FVL_only=False)`  
  Fits the model using `differential_evolution`; stores `wn`, `zeta`, (and `alpha`, `a0` if used). Optionally plots results.  
  **Note:** `excitation_type` now mainly labels the fitting approach; default PEF-based initialization is active.

* `run_simulation(sim_param, sim_type="", num_sims=4, percentage_step=10, plot_FVL_only=False)`  
  Performs sensitivity analysis by varying one model parameter at a time.  
  **Note:** `sim_type` parameter is for internal tracking and does not alter the default model behavior.

* `calc_FEV1_FVC()`  
  Calculates interpolated FEV1 and final FVC from the simulated trajectory.

* `plot_model(only_FVL, add_title_text)`  
  Plots comparison of original FE loop vs. model output.

---

## Example Usage

```python
# AreaFE % predicted
aFE = spiro_features_extraction.areaFE(FE_vol, FE_flow, sex=1, age=60, height=175)
area_pred = aFE.calc_AreaPred()
area_act = aFE.calc_areaFE()

# Angle of collapse
ac = spiro_features_extraction.angle_of_collapse(FE_vol, FE_flow)
angle, err = ac.calc_AC(plotModel=True, plotProcess=True)

# Deflating balloon model
db = spiro_features_extraction.deflating_baloon(FE_time, FE_vol, FE_flow)
db.run_model(excitation_type="", plot_model=True, add_title_text='Subject1')
# Sensitivity analysis on 'zeta'
db.run_simulation(sim_param='zeta', sim_type='', num_sims=4, percentage_step=10, plot_FVL_only=True)

# Extract parameters
wn, zeta = db.wn, db.zeta
mse_vol, mse_flow = db.mse_volume, db.mse_flow
```