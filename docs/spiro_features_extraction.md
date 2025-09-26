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
  Returns computed angle of collapse and fit error. Set `plotModel=True` to plot the fitted model, and `plotProcess=True` to visualize the fitting process.

---

### Subclass: `deflating_baloon`

Models the FE signal using second-order ODE dynamics (deflating balloon analogy).

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`  
  Prepares volume/flow signals for modeling by standardizing orientation and segmenting after PEF.

* `reorient_model()`  
  Reverts simulated signal back to original volume/flow orientation.

* `get_excitation_phase(T1, params)`  
  Handles the early phase of expiration (excitation) based on provided initial parameters.

* `calc_hypothesis(params)`  
  Simulates the flow-volume signal using the selected model parameters.

* `Cost_Function(params)`  
  Computes optimization error between simulated and actual signals.

* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`  
  Fits the deflating balloon model using `differential_evolution`.  
  - `excitation_type`: one of `'Linear'`, `'Exponential pressure'`, `'Non linear'`, or any other string for default behavior based on PEF initial conditions.  
  - `plot_model`: if `True`, invokes `plot_model` after fitting.  
  - `add_title_text`: custom title prefix for plots.  
  - `plot_FVL_only`: if `True`, only the flow–volume loop is plotted.

* `run_simulation(sim_param='zeta', sim_type=None, num_sims=4, percentage_step=10, plot_FVL_only=True)`  
  Performs sensitivity analysis by varying a given model parameter (`sim_param`, e.g., `'zeta'`, `'omega'`, or `'alpha'`).  
  - `sim_type` is an internal placeholder (currently not used in simulation).  
  - `num_sims`: number of simulation steps.  
  - `percentage_step`: percentage change per simulation.  
  - `plot_FVL_only`: if `True`, only the FVL plots are generated.

* `calc_FEV1_FVC()`  
  Calculates interpolated FEV1 and FVC from the simulated model output.

* `plot_model(only_FVL, add_title_text)`  
  Plots comparison between actual and simulated flow/volume signals.

---

## Optimization & Outputs

All modeling is done via `scipy.optimize.differential_evolution`. Post-fit metrics include Mean Squared Error (MSE) and R² scores (for both volume and flow when applicable).

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
db.run_model(excitation_type='Default', plot_model=True)
# Sensitivity analysis
, zetas = db.run_simulation(sim_param='zeta', num_sims=5, percentage_step=5)
```

---

## Dependencies

* `numpy`  
* `matplotlib.pyplot`  
* `scipy.optimize.differential_evolution`  
* `sklearn.metrics`  
* `utilities` (custom plotting utility used in angle_of_collapse)

Ensure these libraries are installed before using the class.

---

## References

* AreaFE: [DOI:10.2147/COPD.S51453](https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD)  
* Angle of Collapse: [DOI:10.1186/1465-9921-14-131](https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131)
