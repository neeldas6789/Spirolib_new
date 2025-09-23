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
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height, race)
```

- `FE_volume`: 1D array of forced expiratory volumes
- `FE_flow`:   1D array of forced expiratory flows
- `sex`:       1 for male, 0 for female
- `age`:       Age in years
- `height`:    Height in cm
- `race`:      Race identifier (not used in prediction formulas but required by constructor)

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
  Constructs a piecewise linear model intersecting at point `(x, y)`.

* `min_line_model_error(plotProcess=False)`  
  Loops through all post-PEF points to find best-fitting point minimizing squared error. Set `plotProcess=True` to visualize the fitting process.

* `get_angle(x_p, y_p)`  
  Computes the geometric angle between two segments joined at `(x_p, y_p)`.

* `calc_AC(plotModel=False, plotProcess=False)`  
  Returns computed angle of collapse and the minimal error. Set `plotModel=True` to plot the fitted model, and `plotProcess=True` to visualize the fitting series.

---

### Subclass: `deflating_baloon`

Models the FE signal using a second-order ODE (deflating balloon) and fits parameters via optimization.

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

- `FE_time`:   1D array of timestamps for FE signal
- `FE_volume`: 1D array of volumes for FE signal
- `FE_flow`:   1D array of flow rates for FE signal

#### Core Methods

* `orient_and_snip_signal()`  
  Prepares volume/flow signals for modeling by orienting them correctly for the deflation phase.

* `reorient_model()`  
  Reverts simulated signal back to original orientation (RV at 0, TLC at max, flow positive/negative orientation).

* `get_excitation_phase(T1, params)`  
  Computes early “excitation” phase of expiration based on default PEF initial conditions or specific excitation models.

* `calc_hypothesis(params)`  
  Simulates volume and flow over time given model parameters (`wn`, `zeta`, and optional `alpha`, `a0`).

* `Cost_Function(params)`  
  Computes the combined squared error between model and actual signals to be minimized.

* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`  
  Fits the deflating balloon model via `scipy.optimize.differential_evolution`.  
  `excitation_type` may be one of:  
  - `"Linear"`, `"Exponential pressure"`, `"Non linear"`, or `""` (default simple PEF-based initial condition).  
  `plot_model=True` will display comparison plots.

* `run_simulation(sim_param='zeta', sim_type='', num_sims=4, percentage_step=10, plot_FVL_only=True)`  
  Performs sensitivity analysis by varying one model parameter (`sim_param`) across `num_sims` steps of size `percentage_step`%.

* `calc_FEV1_FVC()`  
  Computes interpolated FEV1 at 1 second and final FVC from the model output.

* `plot_model(only_FVL, add_title_text)`  
  Plots original vs. simulated flow-volume, volume-time, and flow-time curves with fit metrics.

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

# Fit balloon model
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type="", plot_model=True)
```