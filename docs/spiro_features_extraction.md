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

Implements a data-driven geometric fitting model to compute the angle of collapse after PEF.

#### Initialization

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`  
  * Constructs a piecewise linear model intersecting point `(x, y)`.

* `min_line_model_error(plotProcess=False)`  
  * Loops through all post-PEF points to find the best-fitting point minimizing squared error. Set `plotProcess=True` to visualize the fitting process.

* `get_angle(x_p, y_p)`  
  * Computes the geometric angle between two segments joined at `(x_p, y_p)`.

* `calc_AC(plotModel=False, plotProcess=False)`  
  * Returns computed angle of collapse and cost Jmin. Set `plotModel=True` to plot the fitted model, and `plotProcess=True` to visualize the fitting process.

---

### Subclass: `deflating_baloon`

Models the FE signal using second-order ODE dynamics, simulating lung deflation.

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`  
  * Orients volume and flow signals for modeling.

* `reorient_model()`  
  * Reverts the simulated signal to the original coordinate system.

* `get_excitation_phase(T1, params)`  
  * Handles the early phase of expiration (excitation) based on `excitation_type` and initial conditions.

* `calc_hypothesis(params)`  
  * Simulates deflation using parameters `[wn, zeta]` (and `alpha`, `a0` for specific excitation types).

* `Cost_Function(params)`  
  * Computes error between predicted and actual oriented signals for optimization.

* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`  
  * Fits the balloon model using `differential_evolution`. Supported `excitation_type` values:
    - "Linear"
    - "Exponential pressure"
    - "Non linear"
    - Any other string for default initial-condition model.

* `run_simulation(sim_param, num_sims, percentage_step, plot_FVL_only)`  
  * Sensitivity analysis by varying specified model parameter (`"zeta"`, `"omega"`, or `"alpha"`).

* `calc_FEV1_FVC()`  
  * Computes FEV1 and FVC from the simulated signal.

* `plot_model(only_FVL, add_title_text)`  
  * Plots comparison between original and simulated flow-volume loops and optional time-series views.

---

## Example Usage

```python
# Compute angle of collapse
ac = spiro_features_extraction.angle_of_collapse(volume, flow)
angle, cost = ac.calc_AC(plotModel=True, plotProcess=False)

# Compute AreaFE % predicted
af = spiro_features_extraction.areaFE(volume, flow, sex=1, age=35, height=170)
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()

# Fit balloon model with default excitation (initial conditions)
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type="default", plot_model=True)

# Run sensitivity on damping ratio
db.run_simulation(sim_param="zeta", num_sims=5, percentage_step=10, plot_FVL_only=True)
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* `utilities` (for plotting helper functions)