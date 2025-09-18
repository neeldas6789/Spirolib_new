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
# race: string or None (e.g., 'Caucasian', 'African', or None if unknown)
area = spiro_features_extraction.areaFE(
    FE_volume,       # 1D array of volumes during forced expiration
    FE_flow,         # 1D array of flows during forced expiration
    sex,             # 1 = male, 0 = female
    age,             # years
    height,          # cm
    race             # race identifier or None
)
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
  Constructs a piecewise linear model intersecting point `(x, y)`

* `min_line_model_error(plotProcess=False)`  
  Loops through all post-PEF points to find best-fitting point minimizing squared error.

* `get_angle(x_p, y_p)`  
  Computes the geometric angle between two segments joined at `(x_p, y_p)`

* `calc_AC(plotModel=False, plotProcess=False)`  
  Returns computed angle of collapse and squared error. Plot options as described.

---

### Subclass: `deflating_baloon`

Models the FE signal using second-order ODE dynamics. Simulates the lungs as a deflating balloon.

#### Initialization

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`  
  Prepares volume/flow signals for modeling by standardizing orientation

* `reorient_model()`  
  Reverts simulated signal to original coordinate system

* `get_excitation_phase(T1, params)`  
  Handles the early phase of expiration based on default initial conditions.

* `calc_hypothesis(params)`  
  Simulates the flow-volume signal using the selected model and parameters

* `Cost_Function(params)`  
  Computes error between predicted and actual volume/flow to be minimized

* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`  
  Fits model using `differential_evolution` optimizer and plots results.

* `run_simulation(sim_param, num_sims, percentage_step, plot_FVL_only)`  
  Runs sensitivity analysis by varying one model parameter.

* `calc_FEV1_FVC()`  
  Computes interpolated FEV1 and final FVC from model output

* `plot_model(only_FVL, add_title_text)`  
  Plots comparison between actual and simulated flow/volume signals

---

## Example Usage

```python
import spirolib

# Compute angle of collapse
ac = spirolib.spiro_features_extraction.angle_of_collapse(volume, flow)
angle, cost = ac.calc_AC(plotModel=True)

# Compute AreaFE % predicted (now requires race)
sex, age, height, race = 1, 35, 170, None
aFE = spirolib.spiro_features_extraction.areaFE(volume, flow, sex, age, height, race)
area_pred = aFE.calc_AreaPred()
area_actual = aFE.calc_areaFE()

# Fit balloon model
db = spirolib.spiro_features_extraction.deflating_baloon(time, volume, flow)
db.run_model(excitation_type="", plot_model=True)

# Sensitivity analysis (default behavior)
db.run_simulation(sim_param='zeta', num_sims=4, percentage_step=10, plot_FVL_only=True)

# Extract model parameters and fit metrics
wn, zeta = db.wn, db.zeta
R2_vol, R2_flow = db.R2_volume, db.R2_flow
mse_vol, mse_flow = db.mse_volume, db.mse_flow
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.optimize.differential_evolution`
* `sklearn.metrics`
* `utilities` (custom plotting utility used inside `angle_of_collapse`)

Ensure these libraries are installed before using the class.

---

## Licensing

This tool is intended for research and educational purposes. Ensure clinical validation before diagnostic use.
