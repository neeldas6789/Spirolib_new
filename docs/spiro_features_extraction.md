# Documentation: `spiro_features_extraction`

The `spiro_features_extraction` class provides a modular architecture for extracting advanced mathematical features from forced expiratory (FE) spirometry signals. Supported feature extraction models include:

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
  * Constructs a piecewise linear model through point `(x, y)`.
* `min_line_model_error(plotProcess=False)`
  * Searches all post-PEF points to find the one minimizing mean squared error. Set `plotProcess=True` to visualize.
* `get_angle(x_p, y_p)`
  * Computes the geometric angle at point `(x_p, y_p)`.
* `calc_AC(plotModel=False, plotProcess=False)`
  * Returns computed angle of collapse and corresponding error. Use `plotModel=True` to plot the fitted model.

---

### Subclass: `deflating_baloon`

Models the FE signal using a second-order ODE “balloon” dynamic. Supports multiple excitation types:

* **Default** (initial conditions at PEF)
* **Linear**
* **Exponential pressure**
* **Non linear**

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
  * Prepares volume/flow signals for modeling by standardizing orientation.
* `reorient_model()`
  * Converts model output back to original coordinate system.
* `get_excitation_phase(T1, params)`
  * Computes the early (excitation) phase of expiration based on `excitation_type`.
* `calc_hypothesis(params)`
  * Simulates flow-volume using model parameters.
* `Cost_Function(params)`
  * Computes objective error for optimization.
* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  * Fits the balloon model via `differential_evolution`. `excitation_type` may be one of `"Default"`, `"Linear"`, `"Exponential pressure"`, or `"Non linear"`. Set `plot_model=True` to visualize the final fit.
* `run_simulation(sim_param, num_sims, percentage_step, plot_FVL_only)`
  * Performs sensitivity analysis by varying one model parameter (e.g., zeta or omega) and plotting multiple model curves.
* `calc_FEV1_FVC()`
  * Computes interpolated FEV1 and final FVC from model output.
* `plot_model(only_FVL, add_title_text)`
  * Plots comparison between original and simulated signals.

---

## Excitation Types

The `excitation_type` argument in `run_model` actively alters the fitting logic. Valid values:

* `"Default"`: Initial conditions at PEF.
* `"Linear"`: Linear increase of flow to PEF.
* `"Exponential pressure"`: Exponential pleural pressure model.
* `"Non linear"`: Non-linear excitation model.


---

## Optimization Notes

All model fitting uses `scipy.optimize.differential_evolution`. Fit metrics include:

* Mean Squared Error (MSE)
* R² Score (flow and volume)

---

## Example Usage

```python
# Compute area under FE loop (predicted vs actual)
af = spiro_features_extraction.areaFE(volume, flow, sex=1, age=35, height=170)
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()

# Compute angle of collapse
ac = spiro_features_extraction.angle_of_collapse(volume, flow)
angle, cost = ac.calc_AC(plotModel=True)

# Fit deflating balloon model with non-linear excitation
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type="Non linear", plot_model=True)
```

---

## Dependencies

* `numpy`
* `matplotlib`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* `utilities` (custom spirometry plotting/util module)

---

## References

* AreaFE: https://doi.org/10.2147/COPD.S51453
* Angle of Collapse: https://doi.org/10.1186/1465-9921-14-131

---

## Licensing

Intended for research and educational use. Validate clinically before diagnostic applications.
