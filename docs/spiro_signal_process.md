# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale1)
```

### Parameters

1. `time`                   : Time array of the spirometry manoeuvre (list or 1D array, preferably in s)
2. `volume`                 : Volume array of the manoeuvre (list or 1D array, preferably in L)
3. `flow`                   : Flow array (list or 1D array, preferably in L/s)
4. `patientID`              : Unique identifier for the patient (string or number)
5. `trialID`                : Identifier for the trial (string or number; e.g., 'Best')
6. `flag_given_signal_is_FE`: Boolean; True if the input signal is forced-expiration only
7. `scale1`                 : Scaling factor applied to `time` (e.g., 0.001 if input is in ms)

*Note:* Internally, `time` is multiplied by `scale1` to ensure consistent units (seconds).

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`

  Ensures signal orientation is standard (expiratory FVL right-skewed and PEF positive).

* `standerdize_units()`

  Converts all input data units to litres and seconds.

* `manual_trim(begin_time=0, end_time=None)`

  Trims the signal between the given time bounds and pads start/end points to maintain FE consistency.

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`

  Plots the flow-volume loop or time-series representations of volume and flow.

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`

  Implements low-pass filtering using Butterworth filters.

* `smooth_FVL_start(time, vol, flow)`

  Smoothens the start of the FE FVL to remove negative flow artifacts.

### Index Detection

* `get_Indexes_In_1s(start_index=0)`

  Returns the sample index corresponding to 1 s from `start_index`.

* `get_PEF_index(indx1, indx2)`

  Identifies the index of Peak Expiratory Flow (PEF) between `indx1` and `indx2`.

* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`

  Determines FE start/end indices using BEV or threshold-of-PEF criteria.

* `get_FI_start(index1=None)`

  Finds the start index of forced inspiration (for combined FI–FE signals).

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`

  Returns FE segment arrays (time, vol, flow) with optional plotting.

### Trimming & Thresholding

* `backExtrapolate_FEstart()`

  Uses back-extrapolation from PEF to detect FE start and checks BEV criteria.

* `threshPEF_FEstart(thresh_percent_begin)`

  Uses a percentage of PEF to detect FE start.

* `trim_FE_end(thresh_percent_end)`

  Uses a percentage of PEF to detect FE end.

### Acceptability Checks

* `check_rise_to_PEF()`

  Verifies that flow rises from zero to PEF.

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`

  Checks for excessive gaps (>1 s) in the first N seconds.

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`

  Comprehensive acceptability test; returns `(True, 'Accepted')` or `(False, 'Rejected: <reason>')`.

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`

  Calculates FEV1 (1‐s volume) and FVC via interpolation.

* `calc_flow_parameters()`

  Computes PEF, FEF25/50/75, and FEF25–75 from the FE segment.

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`

  Returns predicted reference values for key spirometric metrics.

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`

  After acceptability, computes all spirometry parameters, percent‐predicted values, and sets `signal_finalized=True`.

### Internal Attributes (Post-finalization)

* `index1`, `index2`: FE start/end
* `FEV1`, `FVC`, `Tiff`, `PEF`, `FEF25`, `FEF50`, `FEF75`, `FEF25_75`
* Percent-predicted: `FEV1_PerPred`, etc.

---

## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow, 'P1', 'Trial1', False, scale1=0.001)
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
* `matplotlib.pyplot`
* `scipy.signal.butter`, `scipy.signal.lfilter`
* `peakutils`

Ensure these are installed before use.