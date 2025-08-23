# spirolib: spiro_signal_process

The `spiro_signal_process` class provides comprehensive tools for processing spirometry signals, including flow-volume loops (FVLs), forced expiratory (FE) segments, and standard spirometry parameters (FEV1, FVC, PEF, etc.).

## Initialization
```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE)
```

### Parameters
- `time`: array of timestamps (s)
- `volume`: array of lung volumes (L)
- `flow`: array of airflow (L/s)
- `patientID`: unique patient identifier
- `trialID`: trial identifier (string or number)
- `flag_given_signal_is_FE`: `True` if input is FE only

All inputs are converted to NumPy arrays internally.

---
## Data Preprocessing
- `correct_data_positioning(flip_vol=False, flip_flow=False)`
  - Ensures FVL is right-skewed and PEF positive.
- `standerdize_units()`
  - Converts `time`→s, `volume`→L, `flow`→L/s.
- `manual_trim(begin_time, end_time)`
  - Trims the signal between specified times and pads endpoints.

---
## Plotting
- `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  - Plots FVL and/or time-series (volume vs. time, flow vs. time).

---
## Filtering & Smoothing
- `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`
  - Applies a Butterworth low-pass filter.
- `smooth_FVL_start(time, vol, flow)`
  - Smooths start of FE segment for better FVL shape.

---
## Index Detection
- `get_Indexes_In_1s(start_index=0)`
  - Finds index ~1 s after specified point.
- `get_PEF_index(indx1, indx2)`
  - Locates Peak Expiratory Flow index within FE.
- `backExtrapolate_FEstart()` / `threshPEF_FEstart(thresh_percent_begin)` / `trim_FE_end(thresh_percent_end)`
  - Determine FE start/end using back-extrapolation or PEF thresholds.
- `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`
  - Returns FE start (`index1`) and end (`index2`).
- `get_FI_start(index1=None)`
  - Finds forced inspiration start index.

---
## FE Signal Extraction
- `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`
  - Extracts FE segment (time, volume, flow), with optional padding and plotting.

---
## Acceptability Checks
- `check_rise_to_PEF()`
  - Verifies flow rises to PEF.
- `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`
  - Ensures no large time gaps.
- `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`
  - Performs full acceptability assessment, including BEV criteria. Returns `(accepted, message)`.

---
## Parameter Calculation
- `calc_FEV1_FVC()`
  - Calculates FEV1 (interpolated at 1 s) and FVC.
- `calc_flow_parameters()`
  - Computes PEF, FEF25, FEF50, FEF75, and FEF25-75.

---
## Reference Predictions (ECCS93)
- `calc_ECCS93_ref(param)`
  - Returns predicted reference for `param` (`'FVC'`, `'FEV1'`, `'PEF'`, `'FEF25'`, etc.) based on sex, age, height.

---
## Finalization
- `finalize_signal(sex=None, age=None, height=None)`
  - After acceptability, computes and stores all spirometry parameters and % predicted values.
  - Ensures `index1`/`index2` (FE start/end) are set.

Attributes set on finalization: 
```
FEV1, FVC, Tiff (FEV1/FVC), PEF,
FEF25, FEF50, FEF75, FEF25_75,
FEV1_PerPred, FVC_PerPred, …, FEF25_75_PerPred
```  
Sets `signal_finalized=True`.

---
## Example Workflow
```python
sp = spiro_signal_process(time, volume, flow, 'P1', '1', False)
sp.correct_data_positioning()
sp.standerdize_units()
accepted, msg = sp.check_acceptability_of_spirogram()
if accepted:
    sp.finalize_signal(sex=1, age=35, height=175)
    print(sp.FEV1, sp.FVC, sp.PEF)
```

---
## Dependencies
- numpy
- matplotlib
- scipy.signal (butter, lfilter)
- peakutils

---
## Licensing
Intended for research and educational use. Validate clinically before diagnostic deployment.