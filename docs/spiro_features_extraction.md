# `spiro_features_extraction` Documentation

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
  Returns predicted AreaFE using demographic inputs.

* `calc_areaFE()`  
  Computes area under the FE curve using trapezoidal integration.

---

### Subclass: `angle_of_collapse`

Implements a data-driven geometric fitting model to compute the angle of collapse after PEF.

#### Initialization

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`  
  Constructs a piecewise linear model intersecting point `(x, y)`.

* `min_line_model_error(plotProcess=False)`  
  Loops through all post-PEF points to find best-fitting point minimizing squared error. Set `plotProcess=True` to visualize the fitting process.

* `get_angle(x_p, y_p)`  
  Computes the geometric angle between two segments joined at `(x_p, y_p)`.

* `calc_AC(plotModel=False, plotProcess=False)`  
  Returns computed angle of collapse and squared error. Set `plotModel=True` to plot the fitted model, and `plotProcess=True` to visualize the fitting process.

---

### Subclass: `deflating_baloon`

Models the FE signal using second-order ODE dynamics. Simulates the lungs as a deflating balloon.

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`  
  Prepares volume/flow signals for modeling by standardizing orientation.

* `reorient_model()`  
  Reverts simulated signal to original coordinate system.

* `get_excitation_phase(T1, params)`  
  Handles the early phase of expiration (excitation) based on selected model parameters.

* `calc_hypothesis(params)`  
  Simulates the flow-volume signal using the chosen model and parameters.

* `Cost_Function(params)`  
  Computes error between predicted and actual volume/flow to be minimized.

* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`  
  Fits model using `differential_evolution` optimizer and plots results. Supports `excitation_type` values:
  - `"Linear"`: linear excitation start (deprecated)
  - `"Exponential pressure"`: exponential pressure model (deprecated)
  - `"Non linear"`: non-linear excitation model
  - `""` (default): uses initial conditions at PEF

* `run_simulation(sim_param, sim_type, num_sims, percentage_step, plot_FVL_only)`  
  Runs sensitivity analysis by varying one model parameter.

* `calc_FEV1_FVC()`  
  Computes interpolated FEV1 and final FVC from model output.

* `plot_model(only_FVL, add_title_text)`  
  Plots comparison between actual and simulated flow/volume signals.

---

## Excitation Types

The `run_model` method supports multiple `excitation_type` options:

* `"Linear"`: legacy linear excitation (module still present)
* `"Exponential pressure"`: legacy exponential model (module still present)
* `"Non linear"`: active non-linear excitation modeling
* `""` (default): employs initial conditions at PEF for deflation modeling

Pass the relevant string to `run_model` to engage the corresponding algorithm.

---

## Optimization Notes

All modeling is done via `scipy.optimize.differential_evolution`. Fit metrics include:

* Mean Squared Error (MSE)
* R² Score (flow and volume)

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
db.run_model(excitation_type="", plot_model=True)  # choose excitation_type as needed
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics` (for MSE and R²)
* `utilities` (custom plotting utility used inside `angle_of_collapse`)

---

## References

* AreaFE: [DOI:10.2147/COPD.S51453](https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD)
* Angle of Collapse: [DOI:10.1186/1465-9921-14-131](https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131)

---

## Licensing

This tool is intended for research and educational purposes. Ensure clinical validation before diagnostic use.
