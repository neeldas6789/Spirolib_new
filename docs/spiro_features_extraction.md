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
# FE_volume: 1D array of forced expiration volumes (L)
# FE_flow:   1D array of forced expiration flows (L/s)
# sex:      1=male, 0=female
# age:      years
# height:   cm
# race:     string or code (currently stored for future reference)
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height, race)
```

#### Methods

* `calc_AreaPred()`
  * Returns predicted AreaFE using demographic inputs and ECCS93-based formulas.

* `calc_areaFE()`
  * Computes area under the FE loop using trapezoidal integration.

---

### Subclass: `angle_of_collapse`

Implements a data-driven geometric fitting model to compute the angle of collapse after PEF.

#### Initialization

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`
  * Constructs a piecewise linear model intersecting point `(x, y)` in the post-PEF signal.

* `min_line_model_error(plotProcess=False)`
  * Searches all post-PEF points to find the pivot that minimizes squared error.
  * If `plotProcess=True`, overlays intermediate line models.

* `get_angle(x_p, y_p)`
  * Computes the geometric angle between two line segments joined at `(x_p, y_p)`.

* `calc_AC(plotModel=False, plotProcess=False)`
  * Returns `(angle_of_collapse, Jmin)` where `Jmin` is the minimized squared error.
  * Set `plotModel=True` to visualize the best-fit model; `plotProcess=True` to show iteration fits.

---

### Subclass: `deflating_baloon`

Models the FE signal using second-order ODE dynamics, simulating the lungs as a deflating balloon.

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
  * Prepares volume/flow signals for modeling by standardizing orientation.

* `reorient_model()`
  * Reverts simulated signal to original coordinate system after fitting.

* `get_excitation_phase(T1, params)`
  * Handles the early phase of expiration (excitation) based on input parameters.

* `calc_hypothesis(params)`
  * Simulates flow–volume signal using current excitation and deflation parameters.

* `Cost_Function(params)`
  * Computes error between predicted and actual oriented signals.

* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  * Fits model using `scipy.optimize.differential_evolution`.
  * **Supported `excitation_type` values:**
    - `"Linear"`              : legacy linear excitation model
    - `"Exponential pressure"`: pressure-driven excitation
    - `"Non linear"`          : non-linear excitation
    - any other string or empty: default model based solely on PEF initial conditions
  * If `plot_model=True`, plots model vs. actual signal; `plot_FVL_only` restricts to flow–volume loop.

* `run_simulation(sim_param, num_sims, percentage_step, plot_FVL_only)`
  * Performs sensitivity analysis by varying one model parameter (e.g., zeta or omega).

* `calc_FEV1_FVC()`
  * Interpolates 1-second volume (`FEV1`) and computes final `FVC` from the simulated signal.

* `plot_model(only_FVL, add_title_text)`
  * Plots comparison between actual and model-predicted signals (flow–volume, volume–time, flow–time).

---

## Optimization & Metrics

All modeling is performed using `scipy.optimize.differential_evolution`. After fitting, metrics such as Mean Squared Error (MSE) and R² Score (for volume and flow) are computed.

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

# Fit balloon model with default excitation (PEF initial conditions)
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type='', plot_model=True)
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics` (for MSE & R²)
* `utilities` (custom plotting helper)

---

## References

* AreaFE: [DOI:10.2147/COPD.S51453](https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD)
* Angle of Collapse: [DOI:10.1186/1465-9921-14-131](https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131)

---

## Licensing

This tool is intended for research and educational purposes. Ensure clinical validation before diagnostic use.
