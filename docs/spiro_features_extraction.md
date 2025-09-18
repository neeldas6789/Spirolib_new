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

#### Parameters

* `FE_volume`: Forced expiratory volume array
* `FE_flow`: Forced expiratory flow array
* `sex`: Integer (1=male, 0=female)
* `age`: Age in years
* `height`: Height in cm
* `race`: Racial group for prediction equations (string or None)

#### Methods

* `calc_AreaPred()`  
  * Returns predicted AreaFE using demographic inputs.

* `calc_areaFE()`  
  * Computes area under the FE curve using trapezoidal integration.

---

### Subclass: `angle_of_collapse`
... (rest unchanged)