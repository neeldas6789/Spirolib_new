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

1. `FE_volume`: Forced expiratory volume array
2. `FE_flow`: Forced expiratory flow array
3. `sex`: Binary sex indicator (1 = male, 0 = female)
4. `age`: Patient age in years
5. `height`: Patient height in cm
6. `race`: Patient race or ethnicity (string) for demographic adjustment

#### Methods

* `calc_AreaPred()`

  * Returns predicted AreaFE using demographic inputs.

* `calc_areaFE()`

  * Computes area under the FE curve using trapezoidal integration.

---

### Subclass: `angle_of_collapse`

... (unchanged) ...

---

### Subclass: `deflating_baloon`

... (unchanged) ...

---

## Example Usage

```python
# Compute AreaFE % predicted, now including race
af = spiro_features_extraction.areaFE(
    FE_volume=volume, FE_flow=flow,
    sex=1, age=35, height=170, race='Caucasian'
)
area_pred = af.calc_AreaPred()
area_actual = af.calc_areaFE()
```
