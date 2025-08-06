# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to process and analyze spirometry data, particularly flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(
    time,                   # list or 1D array of time points
    volume,                 # list or 1D array of volume (litres)
    flow,                   # list or 1D array of flow (L/s)
    patientID,              # string or number
    trialID,                # string or number
    flag_given_signal_is_FE,# bool: True if input is FE-only
    scale2                  # float: scaling factor applied to time (use 1 for no scaling)
)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (units as provided).  
* `volume`: Volume array of the manoeuvre (preferably in litres).  
* `flow`: Flow array of the manoeuvre (litres per second).  
* `patientID`: Unique patient identifier (string or number).  
* `trialID`: Identifier for the trial (string, number, or `'Best'`).  
* `flag_given_signal_is_FE`: Boolean indicating if the provided data is FE-only.  
* `scale2`: Scaling factor applied to time vector on initialization (float).

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`  
  Ensures the expiratory flow-volume loop is right-skewed and PEF is positive.

* `standerdize_units()`  
  Converts volume from mL to L, flow from mL/s to L/s, and time from ms to s.

* `manual_trim(begin_time=0, end_time=None)`  
  Trims the time, volume, and flow signals based on provided time bounds.

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`  
  Plots the flow-volume loop and/or time-series of volume and flow.

### Index Detection

* `get_Indexes_In_1s(start_index=0)`  
  Returns the index corresponding to 1 s from `start_index`.

* `get_PEF_index(indx1, indx2)`  
  Finds the index of Peak Expiratory Flow (PEF) between two indices.

* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`  
  Determines FE start and end indices using BEV or threshold-PEF methods.

* `get_FI_start(index1=None)`  
  Identifies the start index of forced inspiration for combined FI-FE signals.

### Signal Extraction & Smoothing

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`  
  Extracts the FE segment (time, volume, flow) with optional plotting.

* `smooth_FVL_start(time, vol, flow)`  
  Smoothens the beginning of the FE loop for better shape quality.

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`  
  Applies a Butterworth low-pass filter to the data.

### Acceptability Checks

* `check_rise_to_PEF()`  
  Verifies a rise to PEF exists.

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`  
  Checks for large sampling gaps.

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`  
  Runs full acceptability checks; rejects if BEV or timing criteria fail.

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`  
  Calculates interpolated FEV1 and FVC.

* `calc_flow_parameters()`  
  Computes PEF, FEF25, FEF50, FEF75, and FEF25–75.

### Reference Predictions (ECCS93)

* `calc_ECCS93_ref(param)`  
  Returns predicted reference value for `param` (e.g., 'FVC', 'FEV1').

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`  
  After acceptability, finalizes and stores all parameters and predicted percentages.

---

## Example Workflow

```python
from spirolib.spiro_signal_process import spiro_signal_process

sp = spiro_signal_process(time, volume, flow, 'P1', 'T1', False, 1)
sp.correct_data_positioning()
sp.standerdize_units()
accepted, reason = sp.check_acceptability_of_spirogram()
if accepted:
    sp.finalize_signal(sex=1, age=35, height=175)
    print(sp.FEV1, sp.FVC, sp.PEF)
```

---

## Dependencies

* `numpy`
* `matplotlib`
* `scipy.signal`
* `peakutils`