# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array, preferably in seconds)
* `volume`: Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`: Flow array (list or 1D array, preferably in litres/sec)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean flag indicating if the signal is forced expiration only
* `scale`: Numeric scaling factor applied to the input `time` array (e.g., to convert units)

> **Note:** The flow-volume data should be arranged so that the expiratory loop is right skewed and PEF is positive.

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`
  * Ensures signal orientation is standard (expiratory FVL right skewed and PEF positive).

* `standerdize_units()`
  * Converts all input data units to litres and seconds.

* `manual_trim(begin_time=0, end_time=None)`
  * Trims the signal between the given time bounds.

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  * Plots the flow-volume loop or time-series of volume and flow.

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`
  * Implements low-pass filtering using Butterworth filters.

* `smooth_FVL_start(time, vol, flow)`
  * Smoothens the FVL at the start of FE for improved loop shape.

### Index Detection

* `get_Indexes_In_1s(start_index=0)`
  * Returns index corresponding to 1 second from `start_index`.

* `get_PEF_index(indx1, indx2)`
  * Identifies the index of Peak Expiratory Flow (PEF) between the given bounds.

* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`
  * Determines the start/end indices of forced expiration using BEV or threshold-based methods.
  * `check_BEV_criteria` toggles strict BEV validation (if `True`, returns -1 on failure).

* `get_FI_start(index1=None)`
  * Finds the start index of forced inspiration (for combined FI-FE signals).

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`
  * Returns FE segment (time, volume, flow) with optional plotting.  
  * For `BEV` or `thresh_PEF`, the returned segment is padded so flow and volume start/end at zero.

### Trimming & Thresholding

* `backExtrapolate_FEstart()`
  * Uses back-extrapolation to find FE start and validate BEV criteria (returns `(index, BEV_criteria)`).

* `threshPEF_FEstart(thresh_percent_begin)`
  * Uses PEF-based threshold to identify FE start.

* `trim_FE_end(thresh_percent_end)`
  * Uses PEF-based threshold to identify FE end.

### Acceptability Checks

* `check_rise_to_PEF()`
  * Confirms presence of a rise to PEF at signal start.

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`
  * Checks for large gaps in sampling within the first `FE_time_duration` seconds.

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`
  * Evaluates overall acceptability of the spirometry signal, including BEV criteria.

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`
  * Calculates FEV1 and FVC using 1-second interpolated volume.

* `calc_flow_parameters()`
  * Computes PEF, FEF25, FEF50, FEF75, and FEF25-75.

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`
  * Returns predicted reference value for a given parameter using ECCS93 formulas.

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`
  * After acceptability checks, calculates and stores standard spirometry metrics and predicted percentages.  
  * Automatically computes `index1`/`index2` if not already set.

### Internal Attributes (Post-finalization)

* `FEV1`, `FVC`, `Tiff`, `PEF`, `FEF25`, `FEF50`, `FEF75`, `FEF25_75`
* Reference percentages: `FEV1_PerPred`, `FVC_PerPred`, etc.
* `index1`, `index2`: Start/end indices of FE
* `signal_finalized`: Processing completion flag

---

## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow, patientID='P1', trialID='T1', flag_given_signal_is_FE=False, scale=1.0)
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

Ensure these libraries are installed before using the class.

---

## Licensing

This module is intended for educational and research purposes. Validate clinically before any diagnostic or commercial use.
