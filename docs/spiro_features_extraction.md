# Documentation: `spiro_features_extraction`

The `spiro_features_extraction` class provides a modular architecture for extracting advanced mathematical features from forced expiratory (FE) spirometry signals. It includes:

* Area under the Flow-Volume Loop (% predicted)
* Angle of Collapse (AC)
* Deflating Baloon Model

All modules assume the FE signal is standardized and oriented such that:

* Volume is in litres (TLC at 0, RV positive)
* Flow is in litres/s and positive
* Signal is right-skewed (i.e., normal expiratory flow direction)

---

## Class: `spiro_features_extraction`

Main container class encapsulating multiple feature extraction models.

---

### Subclass: `areaFE`

Class for calculating AreaFE % predicted and actual area under the curve.

#### Initialization

```python
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height, race)
```

#### Parameters

* `FE_volume`: 1D array of forced expiratory volumes (litres)
* `FE_flow`: 1D array of forced expiratory flows (litres/s)
* `sex`: 1 (male) or 0 (female)
* `age`: Age in years
* `height`: Height in cm
* `race`: Subject race string (e.g., 'Caucasian', 'African')

#### Methods

* `calc_AreaPred()`  
  Returns predicted AreaFE using demographic inputs.

* `calc_areaFE()`  
  Computes actual area under the FE curve using trapezoidal integration.

---

### Subclass: `angle_of_collapse`

Implements a geometric fitting model to compute the angle of collapse after PEF.

#### Initialization

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`  
  Constructs piecewise linear model intersecting at `(x, y)`.

* `min_line_model_error(plotProcess=False)`  
  Finds best-fitting collapse point by minimizing squared error. Use `plotProcess=True` to visualize.

* `get_angle(x_p, y_p)`  
  Computes angle between pre- and post-collapse segments at `(x_p, y_p)`.

* `calc_AC(plotModel=False, plotProcess=False)`  
  Returns collapse angle and error. `plotModel=True` overlays model on data.

---

### Subclass: `deflating_baloon`

Models the FE signal using a second-order ODE (deflating balloon analogy).

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`  
  Prepares volume/flow signals for modeling by standardizing orientation.

* `reorient_model()`  
  Reverts simulated signal to original coordinates.

* `get_excitation_phase(T1, params)`  
  Handles early-phase excitation (default branch uses initial conditions at PEF).

* `calc_hypothesis(params)`  
  Simulates flow-volume signal based on model parameters.

* `Cost_Function(params)`  
  Computes composite squared error between model and data.

* `run_model(excitation_type, plot_model=False, ...)`  
  Fits model using `differential_evolution`. Supports multiple `excitation_type` settings (see below).

* `run_simulation(sim_param, num_sims, percentage_step, plot_FVL_only)`  
  Performs sensitivity analysis on a chosen model parameter.

* `calc_FEV1_FVC()`  
  Interpolates FEV1 and final FVC from model output.

* `plot_model(only_FVL, add_title_text)`  
  Plots actual vs. simulated flow-volume and time-volume signals.

---

## Excitation Types

The `run_model` method supports the following `excitation_type` options:

* `"Linear"` – linear excitation model (now legacy).
* `"Exponential pressure"` – exponential pressure model (legacy).
* `"Non linear"` – non-linear excitation model (legacy).
* Default (empty or other string) – uses initial conditions at PEF for deflation-only model.

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
db.run_model(excitation_type='', plot_model=True)  # uses PEF-based default
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

* AreaFE: [DOI:10.2147/COPD.S51453](https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD)
* Angle of Collapse: [DOI:10.1186/1465-9921-14-131](https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131)

---

## Licensing

This tool is intended for research and educational purposes. Ensure clinical validation before diagnostic use.
