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

* `FE_volume`: Array of forced expiration volumes (litres)
* `FE_flow`: Array of forced expiration flows (litres/s)
* `sex`: 1 for male, 0 for female
* `age`: Age in years
* `height`: Height in cm
* `race`: Race identifier (affects predictive equations if extended)

#### Methods

* `calc_AreaPred()`  

  * Returns predicted AreaFE using demographic inputs.

* `calc_areaFE()`  

  * Computes area under the FE curve using trapezoidal integration.

---

... (rest unchanged until Excitation Types section)

## Excitation Types

The `excitation_type` parameter in the `run_model` method can be set to one of the legacy modes (`Linear`, `Exponential pressure`, `Non linear`) or left as the default (`""`), which uses initial conditions at PEF for the deflation phase. All modes remain implemented, though legacy modes may be experimental.

---

... (rest unchanged)