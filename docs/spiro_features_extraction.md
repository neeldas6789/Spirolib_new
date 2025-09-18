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

##### Parameters

* `FE_volume`: 1D array of forced expiratory volume (litres)
* `FE_flow`: 1D array of forced expiratory flow (litres/s)
* `sex`: `1` for male, `0` for female
* `age`: Age in years
* `height`: Height in cm
* `race`: Race or ethnicity identifier (currently unused but required by constructor)

#### Methods

* `calc_AreaPred()`

  * Returns predicted AreaFE using demographic inputs.

* `calc_areaFE()`

  * Computes area under the FE curve using trapezoidal integration.

---

### Subclass: `angle_of_collapse`

Implements a data-driven geometric fitting model to compute the angle of collapse after PEF.

... (unchanged) ...

---

### Subclass: `deflating_baloon`

Models the FE signal using second-order ODE dynamics. Simulates the lungs as a deflating balloon.

... (unchanged) ...

---

## Excitation Types

The `run_model` method accepts an `excitation_type` parameter to choose the modeling approach. Supported options:

* `"Linear"`             – Linear flow slope model
* `"Exponential pressure"` – Exponential pressure-driven model
* `"Non linear"`         – Nonlinear initial phase model
* `""` (empty string)    – Default behavior using initial conditions at PEF

Pass the desired `excitation_type` to `run_model` to select the corresponding optimization routine.

---

## Example Usage

```python
# Compute angle of collapse
ac = spiro_features_extraction.angle_of_collapse(volume, flow)
angle, cost = ac.calc_AC(plotModel=True)

# Compute AreaFE % predicted
race = 'None'
af = spirolib.spiro_features_extraction.areaFE(volume, flow, sex=1, age=35, height=170, race)
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()

# Fit balloon model
db = spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type="", plot_model=True)
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* `utilities` (custom plotting utility used inside `angle_of_collapse`)

... (rest unchanged) ...