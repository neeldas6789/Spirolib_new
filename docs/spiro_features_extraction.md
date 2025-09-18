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

#### Requirements

1. `FE_volume`: array of forced expiratory volumes (litres)
2. `FE_flow`: array of forced expiratory flows (L/s)
3. `sex`: 1 (male) or 0 (female)
4. `age`: in years
5. `height`: in cm
6. `race`: demographic identifier (string or code)

#### Methods

* `calc_AreaPred()`
  * Returns predicted AreaFE based on ECCS93 equations and demographic inputs.
* `calc_areaFE()`
  * Computes the actual area under the FE curve using trapezoidal integration.

---

### Subclass: `angle_of_collapse`

Implements a data-driven geometric fitting model to compute the angle of collapse after PEF.

#### Initialization

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`
  * Constructs a piecewise linear model intersecting at point `(x, y)`.
* `min_line_model_error(plotProcess=False)`
  * Loops through post-PEF points to find the best fit minimizing squared error. Set `plotProcess=True` to visualize the fitting process.
* `get_angle(x_p, y_p)`
  * Computes the angle between two segments joined at `(x_p, y_p)`.
* `calc_AC(plotModel=False, plotProcess=False)`
  * Returns the angle of collapse and the fitting error. Use `plotModel=True` to overlay the fitted model, `plotProcess=True` to show the fitting steps.

---

### Subclass: `deflating_baloon`

Models the FE signal using a second-order ODE ("deflating balloon") dynamics.

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
  * Prepares volume/flow signals for modeling by standardizing orientation (RV→0, TLC at max, flow inverted).
* `reorient_model()`
  * Reverts the simulated signal back to the original coordinate system for comparison.
* `get_excitation_phase(T1, params)`
  * Computes the initial excitation phase of expiration (unused by default model).
* `calc_hypothesis(params)`
  * Simulates the flow–volume trajectory using ODE parameters (`wn`, `zeta`).
* `Cost_Function(params)`
  * Computes the sum of squared errors between simulated and actual signals.
* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  * Fits the balloon model using `differential_evolution`. The `excitation_type` argument is now for internal reference; only the default PEF-based initial condition is actively modeled.
* `run_simulation(sim_param, sim_type, num_sims, percentage_step, plot_FVL_only)`
  * Performs parameter sensitivity analysis by varying one model parameter around its optimum.
* `calc_FEV1_FVC()`
  * Computes predicted FEV1 (1 s) and FVC from the simulated trajectory.
* `plot_model(only_FVL, add_title_text)`
  * Visualizes the original and simulated FE signals.

---

## Excitation Types

Previous `excitation_type` settings (`Linear`, `Exponential pressure`, `Non linear`) are retained for compatibility but are no longer functionally supported. The `run_model` method defaults to using initial conditions at PEF for the deflation phase.

---

## Optimization Notes

All model fitting leverages `scipy.optimize.differential_evolution`. Fit metrics include:
* Mean Squared Error (MSE)
* R² Score (flow and volume)

---

## Example Usage

```python
# Compute angle of collapse
ac = spiro_features_extraction.angle_of_collapse(volume, flow)
angle, error = ac.calc_AC(plotModel=True)

# Compute AreaFE % predicted
af = spiro_features_extraction.areaFE(volume, flow, sex=1, age=35, height=170, race='Caucasian')
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()

# Fit balloon model
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type='', plot_model=True)
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* Custom `utilities` for plotting

---

## References

* AreaFE: [DOI:10.2147/COPD.S51453](https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD)
* Angle of Collapse: [DOI:10.1186/1465-9921-14-131](https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131)

---

## Licensing

This tool is intended for research and educational purposes. Clinical use requires proper validation.
