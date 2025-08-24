# spiro_features_extraction

The `spiro_features_extraction` module provides advanced mathematical models to extract features from forced expiratory (FE) spirometry signals. It supports:

- AreaFE and AreaFE % Predicted
- Angle of Collapse
- Deflating Balloon Model

All models require a correctly oriented and standardized FE signal (volume in L, flow in L/s, right-skewed FVL).

---

## Class: `spiro_features_extraction`

Container class for three feature extraction algorithms:

### Subclass: `areaFE`
Calculates actual and predicted areas under the FE flow–volume loop using ECCS93 reference equations.

#### Initialization
```python
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height)
```

#### Methods
- `calc_AreaPred()`
  - Returns predicted area under the FVL based on demographic inputs.
- `calc_areaFE()`
  - Computes actual area under the FE curve via `numpy.trapz`.

---

### Subclass: `angle_of_collapse`
Estimates the geometric angle at the point of maximal collapse post-PEF.

#### Initialization
```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
```

#### Methods
- `generate_linemodel(x, y, index)`
  - Builds a piecewise linear fit through point `(x, y)`.
- `min_line_model_error(plotProcess=False)`
  - Iterates all post-PEF points to find the best-fit hinge minimizing mean squared error. Set `plotProcess=True` to visualize each candidate.
- `get_angle(x_p, y_p)`
  - Computes the angle between two line segments meeting at `(x_p, y_p)`.
- `calc_AC(plotModel=False, plotProcess=False)`
  - Returns `(angle_of_collapse, Jmin)`. `plotModel=True` overlays the optimal fit; `plotProcess=True` shows fitting steps.

---

### Subclass: `deflating_baloon`
Models the deflation phase as a second-order system (deflating balloon). Automatically derives initial conditions at PEF.

#### Initialization
```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
```

#### Core Methods
- `orient_and_snip_signal()`
  - Aligns and truncates original signals so deflation starts at zero.
- `reorient_model()`
  - Converts simulated output back to the original coordinate frame.
- `get_excitation_phase(T1, params)`
  - (Internal) handles initial phase of expiration if specialized excitation is selected.
- `calc_hypothesis(params)`
  - Simulates volume/flow using given `[wn, zeta]` (and additional `alpha`, `a0` for non-default excitation).
- `Cost_Function(params)`
  - Computes the combined MSE between simulated and original signals after the excitation index.
- `run_model(excitation_type, plot_model=False, add_title_text="", plot_FVL_only=False)`
  - Fits model parameters `wn` and `zeta` using `scipy.optimize.differential_evolution`. Optional legacy modes (`Linear`, `Exponential pressure`, `Non linear`) remain available but default to PEF-based initial conditions. Set `plot_model=True` to display final overlay.
- `run_simulation(sim_param='zeta', sim_type='', num_sims=4, percentage_step=10, plot_FVL_only=True)`
  - Performs sensitivity analysis by varying one parameter (`'zeta'` or `'omega'`) across simulations. `sim_type` allows specifying legacy excitation mode if needed.
- `calc_FEV1_FVC()`
  - Interpolates FEV1 at 1 s and final FVC from the simulated trajectory.
- `plot_model(only_FVL, add_title_text)`
  - Displays comparison plots between actual and simulated FE signals.

---

## Example Usage
```python
# AreaFE
af = spiro_features_extraction.areaFE(vol, flow, sex=0, age=30, height=165)
print(af.calc_areaFE(), af.calc_AreaPred())

# Angle of collapse
ac = spiro_features_extraction.angle_of_collapse(vol, flow)
angle, error = ac.calc_AC(plotModel=True)

# Deflating balloon model
db = spiro_features_extraction.deflating_baloon(time, vol, flow)
db.run_model(excitation_type='', plot_model=True)
# Sensitivity
db.run_simulation(sim_param='zeta', num_sims=5, percentage_step=20)
```

---

## Dependencies
- numpy
- matplotlib
- scipy.optimize
- sklearn.metrics (for MSE and R² in legacy modes)
- `utilities.plot_Model` for integrated plotting

---

## References
- AreaFE: DOI:10.2147/COPD.S51453
- Angle of Collapse: DOI:10.1186/1465-9921-14-131
