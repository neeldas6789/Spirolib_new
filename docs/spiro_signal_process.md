# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow–volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(
    time,
    volume,
    flow,
    patientID,
    trialID,
    flag_given_signal_is_FE,
    scale2
)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array)
* `volume`: Volume array of the manoeuvre (list or 1D array)
* `flow`: Flow array (list or 1D array)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean flag; if `True`, input signal is forced expiration only
* `scale2`: Numeric factor to scale `time` input (e.g., convert units or apply time dilation)

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`  
  Ensures signal orientation is standard (expiratory FVL right skewed and PEF positive).

* `standerdize_units()`  
  Converts internal units: volume and flow (from mL to L) and time (from ms to s), assuming original inputs require scaling.

* `manual_trim(begin_time=0, end_time=None)`  
  Trims the signal between provided time bounds, padding start/end to maintain continuity.

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`  
  Plots the flow–volume loop or combined time-series (volume & flow vs. time).

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`  
  Implements low-pass filtering using a Butterworth design.

* `smooth_FVL_start(time, vol, flow)`  
  Smoothens the beginning of the FE loop for artifact removal.

### Index Detection

* `get_Indexes_In_1s(start_index=0)`  
  Returns the index corresponding to 1 s from the given start.

* `get_PEF_index(indx1, indx2)`  
  Finds the index of Peak Expiratory Flow (PEF) between two bounds.

* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`  
  Determines start and end indices of forced expiration using back-extrapolation or PEF thresholds.

* `get_FI_start(index1=None)`  
  Finds the start index of forced inspiration for combined manoeuvres.

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`  
  Returns the segmented FE signal (time, volume, flow) with zero-padded start/end when using `BEV` or `thresh_PEF`.

### Trimming & Thresholding

* `backExtrapolate_FEstart()`  
  Uses back-extrapolation from PEF to determine FE start and validate BEV criteria.

* `threshPEF_FEstart(thresh_percent_begin)`  
  Determines FE start based on a percentage threshold of PEF.

* `trim_FE_end(thresh_percent_end)`  
  Determines FE end based on a percentage threshold of PEF.

### Acceptability Checks

* `check_rise_to_PEF()`  
  Validates that the flow signal rises from zero to a positive PEF.

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`  
  Ensures there are no large gaps (> `max_time_interval`) in the initial `FE_time_duration` seconds.

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`  
  Performs comprehensive acceptability checks (BEV criteria, FI start, FE duration) and finalizes `index1`, `index2` on success.

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`  
  Calculates FEV1 and FVC using linear interpolation at 1 s from start of FE.

* `calc_flow_parameters()`  
  Computes PEF, FEF25, FEF50, FEF75, and FEF25–75 from the FE segment.

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`  
  Returns predicted reference value for given parameter (`'FVC'`, `'FEV1'`, `'PEF'`, etc.) using ECCS93 equations.

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`  
  After passing acceptability checks, computes all spirometry metrics and percentages of predicted values. Stores:
  - `FEV1`, `FVC`, `Tiff`, `PEF`, `FEF25`, `FEF50`, `FEF75`, `FEF25_75`  
  - Predicted percentages: `FEV1_PerPred`, `FVC_PerPred`, etc.  
  - Sets `signal_finalized=True`.

---

## Notes

* Always run `correct_data_positioning()` and `standerdize_units()` before index detection or parameter calculations.  
* Padding in `get_FE_signal` ensures signals start/end at zero flow and volume boundaries.  

---

## Example Workflow

```python
sp = spiro_signal_process(
    time, volume, flow,
    patientID='P1', trialID='T1',
    flag_given_signal_is_FE=False,
    scale2=1.0
)
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
