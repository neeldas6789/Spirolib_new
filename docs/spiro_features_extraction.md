# Class spiro_features_extraction

The `spiro_features_extraction` class provides different mathematical models to extract features from spirometry signals, including:
1. Area under the expiratory Flow-Volume Loop (% predicted)
2. Angle of Collapse (AC)
3. Deflating Balloon Model

All subclasses assume the forced expiratory (FE) signal is:
- Oriented with Total Lung Capacity (TLC) at zero and Residual Volume (RV) positive
- Volume in litres, Flow in litres/s, Time in seconds
- Right-skewed flow-volume loop (positive expiratory flow)

## Subclasses

### 1. areaFE

Calculates actual and predicted area under the expiratory flow-volume loop.

```python
from spirolib.spiro_features_extraction import spiro_features_extraction
# Initialize
area = spiro_features_extraction.areaFE(FE_volume, FE_flow, sex, age, height)
# Actual area
area_actual = area.calc_areaFE()
# Predicted area using ECCS93 equations
area_pred = area.calc_AreaPred()
```

#### Methods

- `calc_areaFE()`: Computes area under the FE curve using `numpy.trapz`.
- `calc_AreaPred()`: Returns predicted area value based on demographic inputs.

### 2. angle_of_collapse

Computes the angle of collapse post-PEF by finding the optimal piecewise linear fit.

```python
ac = spiro_features_extraction.angle_of_collapse(FE_volume, FE_flow)
angle, cost = ac.calc_AC(plotModel=True, plotProcess=False)
```

#### Methods

- `generate_linemodel(x, y, index)`: Builds a two-segment model intersecting at `(x, y)`.
- `min_line_model_error(plotProcess=False)`: Loops through post-PEF points to minimize squared error. Use `plotProcess=True` to visualize.
- `get_angle(x_p, y_p)`: Calculates geometric angle for a given intersection point.
- `calc_AC(plotModel=False, plotProcess=False)`: Returns `(angle_of_collapse, min_error)`. Set `plotModel=True` to overlay the best-fit model.

### 3. deflating_baloon

Models the deflation phase as a second-order system (the “balloon”) and fits model parameters.

```python
db = spiro_features_extraction.deflating_baloon(FE_time, FE_volume, FE_flow)
# Fit model: options for excitation_type: 'Linear', 'Exponential pressure', 'Non linear', or default branch
db.run_model(excitation_type="", plot_model=True)
# Run sensitivity simulation for parameter 'zeta'
db.run_simulation(sim_param='zeta', num_sims=5, percentage_step=10)
```

#### Methods

- `orient_and_snip_signal()`: Prepares oriented volume/flow signals for optimization.
- `reorient_model()`: Converts model output back to original coordinate system.
- `get_excitation_phase(T1, params)`: Handles early-phase (pre-PEF) signal based on `excitation_type`.
- `calc_hypothesis(params)`: Simulates flow/volume for given `[wn, zeta, ...]`.
- `Cost_Function(params)`: Computes cost between simulated and actual signals.
- `run_model(excitation_type, plot_model=False, plot_FVL_only=False, add_title_text="")`: Fits parameters using differential evolution. Supports legacy excitation types plus a default branch using initial conditions at PEF.
- `run_simulation(sim_param, num_sims, percentage_step, plot_FVL_only)`: Performs parameter sensitivity analysis.
- `calc_FEV1_FVC()`: Calculates model-derived FEV1 and FVC.
- `plot_model(only_FVL, add_title_text)`: Plots original vs model signals.

## Dependencies

- `numpy`
- `matplotlib.pyplot`
- `scipy.optimize.differential_evolution`
- `sklearn.metrics` (for MSE and R²)
- Custom `utilities` module for plotting

## References

- AreaFE: https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD
- Angle of Collapse: https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131

---

Ensure your FE signals meet input orientation and unit standards before using these models.
