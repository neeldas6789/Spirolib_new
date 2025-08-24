# spiro_features_extraction

The `spiro_features_extraction` module implements mathematical models to derive advanced features from forced expiratory (FE) spirometry signals. It includes:

* **AreaFE % predicted**
* **Angle of Collapse (AC)**
* **Deflating Balloon Model**

All models expect the FE signal to be:

* **Oriented**: TLC at 0 L, RV > 0 L, flow > 0 L/s, right-skewed FVL
* **Standardized**: volume in litres, flow in litres/s, time in seconds

---

## Class: `spiro_features_extraction`

Container for three feature‐extraction subclasses.

---

### Subclass: `areaFE`
Calculates the area under the FE flow‐volume loop and its predicted value using ECCS93 demographics.

#### Initialization
```python
from spiro_features_extraction import spiro_features_extraction
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height)
```

#### Methods

* `calc_areaFE()`
  Computes actual area under the loop using `numpy.trapz`.

* `calc_AreaPred()`
  Returns predicted area using age, sex, height (ECCS93 formulas).

---

### Subclass: `angle_of_collapse`
Fits a piecewise‐linear model post‐PEF to compute the geometric collapse angle.

#### Initialization
```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods

* `generate_linemodel(x, y, index)`
  Builds left/right linear segments meeting at `(x, y)`.

* `min_line_model_error(plotProcess=False)`
  Scans candidate points to minimize squared error. Use `plotProcess=True` to visualize.

* `get_angle(x_p, y_p)`
  Computes collapse angle at `(x_p, y_p)`.

* `calc_AC(plotModel=False, plotProcess=False)`
  Returns `(angle, error)`. Use `plotModel=True` to overlay fitted model, and `plotProcess=True` for fitting steps.

---

### Subclass: `deflating_baloon`
Models FE decay as a second‐order system (a "deflating balloon").

#### Initialization
```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods

* `orient_and_snip_signal()`
  Prepares oriented volume/flow for fitting.

* `reorient_model()`
  Converts model output back to original coordinates.

* `calc_hypothesis(params)`
  Computes model volume & flow from parameters `[wn, zeta]`.

* `Cost_Function(params)`
  Returns squared‐error cost for optimizer.

* `calc_FEV1_FVC()`
  Interpolates 1 s volume (FEV1) and final FVC from model output.

* `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  Fits the balloon model using `scipy.optimize.differential_evolution`.  
  - **excitation_type**: only the default (initial PEF conditions) is actively modeled; legacy options (`Linear`, `Exponential pressure`, `Non linear`) remain accepted but all resolve to the same fitting routine.  
  - Updates `db.wn`, `db.zeta`, and stores `model_volume`, `model_flow`.
  - Optionally plots flow‐volume and time-domain fits.

* `run_simulation(sim_param, num_sims, percentage_step, plot_FVL_only=True)`
  Performs sensitivity analysis by varying one parameter (`'zeta'` or `'omega'`) around the fitted value.  
  Reports FEV1/FVC for each scenario and overlays curves.

* `plot_model(only_FVL, add_title_text)`
  Plots original vs. simulated signals with fit metrics (MSE, R²).

---

## Example Usage
```python
# AreaFE
af = spiro_features_extraction.areaFE(vol, flow, sex=1, age=40, height=175)
print(af.calc_areaFE(), af.calc_AreaPred())

# Angle of collapse
ac = spiro_features_extraction.angle_of_collapse(vol, flow)
angle, cost = ac.calc_AC(plotModel=True, plotProcess=True)

# Deflating balloon fit
db = spiro_features_extraction.deflating_baloon(time, vol, flow)
db.run_model(excitation_type="", plot_model=True)
# Sensitivity
db.run_simulation(sim_param='zeta', num_sims=5, percentage_step=10)
```

---

## References
* AreaFE: DOI:10.2147/COPD.S51453
* Angle of Collapse: DOI:10.1186/1465-9921-14-131
