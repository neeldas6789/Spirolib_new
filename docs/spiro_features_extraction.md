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
# New signature includes race parameter
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height, race)
```

* `FE_volume`: Array of FE volumes
* `FE_flow`: Array of FE flows
* `sex`: 1 for male, 0 for female
* `age`: Age in years
* `height`: Height in cm
* `race`: Race category (currently stored but not used in prediction)

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

... (rest unchanged)