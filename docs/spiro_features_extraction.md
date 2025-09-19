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

Class for calculating AreaFE % predicted using ECCS93 reference equations.

Requires:
1. FE volume
2. FE flow
3. Sex
4. Age
5. Height
6. Race

Note: This class expects correctly positioned and shifted FE signal
( in the FVL TLC should be at 0 and RV>0, flow>0, FVL is right skewed )
and units standardized (vol in litres, flow in litres/s and time in s).

#### Initialization

```python
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height, race)
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

  * Constructs a piecewise linear model intersecting point `(x, y)`

* `min_line_model_error(plotProcess=False)`

  * Loops through all post-PEF points to find the best-fitting point minimizing squared error. Set `plotProcess=True` to visualize.

* `get_angle(x_p, y_p)`

  * Computes the geometric angle between two segments joined at `(x_p, y_p)`

* `calc_AC(plotModel=False, plotProcess=False)`

  * Returns computed angle of collapse and squared error. Use `plotModel=True` to plot fit.

---

### Subclass: `deflating_baloon`

Models the FE signal using a second-order ODE (deflating balloon concept).

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
* `reorient_model()`
* `get_excitation_phase(T1, params)`
* `calc_hypothesis(params)`
* `Cost_Function(params)`
* `run_model(excitation_type, plot_model=False, ...)`
* `run_simulation(sim_param, num_sims, percentage_step, plot_FVL_only)`
* `calc_FEV1_FVC()`
* `plot_model(only_FVL, add_title_text)`

---

## Excitation Types

Previous `excitation_type` options (`Linear`, `Exponential pressure`, `Non linear`) are no longer actively modeled. The `run_model` method now defaults to using initial PEF conditions for the deflation phase. The `excitation_type` parameter remains for internal classification.

---

## Optimization Notes

All modeling is performed via `scipy.optimize.differential_evolution`. Fit metrics include MSE and R².

---

## Example Usage

```python
# Compute AreaFE % predicted
af = spiro_features_extraction.areaFE(volume, flow, sex, age, height, race)
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()
```
