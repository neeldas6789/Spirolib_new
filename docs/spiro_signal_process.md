# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array, preferably in seconds)
* `volume`: Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`: Flow array (list or 1D array, preferably in litres/sec)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean flag indicating if the signal is forced expiration only

---

## Core Methods & Preprocessing

### Data Positioning & Unit Conversion

* `correct_data_positioning(flip_vol=False, flip_flow=False)`
  * Ensures signal orientation is standard (expiratory FVL right-skewed and PEF positive)

* `standerdize_units()`
  * Converts all input data to litres (volume/flow) and seconds (time)

* `shift_TLC_to_orgin()`
  * Recenters volume so that total lung capacity (TLC) aligns to zero before calculations

* `manual_trim(begin_time=0, end_time=None)`
  * Trims the signal between the given time bounds, padding start/end to maintain continuity

### Filtering & Smoothing

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`
  * Implements low-pass filtering using Butterworth filters

* `smooth_FVL_start(time, vol, flow)`
  * Smoothens the beginning of the FE flow-volume loop by fitting a polynomial to the rising phase

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  * Plots the flow-volume loop (FVL) or time-series of volume and flow

---

## Index Detection

* `get_Indexes_In_1s(start_index=0)`
  * Returns the index at approximately 1 s after `start_index`

* `get_PEF_index(indx1, indx2)`
  * Identifies the Peak Expiratory Flow (PEF) index between `indx1` and `indx2`

* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`
  * Determines start/end indices of forced expiration (FE) using BEV or PEF thresholds

* `get_FI_start(index1=None)`
  * Finds the start index of forced inspiration for combined FI-FE signals

---

## FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`
  * Returns FE segment as `(time, volume, flow)`. When using `BEV` or `thresh_PEF`, the returned arrays are padded so that flow and volume start/end at zero.

---

## Trimming & Thresholding Helpers

* `backExtrapolate_FEstart()`
  * Uses back-extrapolation from peak flow to define FE start and validate BEV criteria

* `threshPEF_FEstart(thresh_percent_begin)`
  * Defines FE start based on a percentage threshold of PEF

* `trim_FE_end(thresh_percent_end)`
  * Defines FE end based on a percentage threshold of PEF

---

## Acceptability Checks

* `check_rise_to_PEF()`
  * Confirms presence of a rise to PEF in the signal

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`
  * Ensures there are no large gaps in time samples within the first `FE_time_duration`

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`
  * Evaluates overall acceptability of the spirometry signal. Returns `(accepted: bool, reason: str)`

---

## Spirometry Parameter Computation

* `calc_FEV1_FVC()`
  * Calculates FEV1 (interpolated at 1 s) and FVC from the FE volume/time arrays

* `calc_flow_parameters()`
  * Computes PEF, FEF25, FEF50, FEF75, and FEF25-75 from the FE segment

---

## Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`
  * Returns predicted reference value for `param` (`'FVC'`, `'FEV1'`, `'PEF'`, etc.) using ECCS93 equations

---

## Finalization

* `finalize_signal(sex=None, age=None, height=None)`
  * After acceptability checks, computes and stores all standard metrics:
    - `FEV1`, `FVC`, `Tiff`, `PEF`, `FEF25`, `FEF50`, `FEF75`, `FEF25_75`
    - Reference percentages: `FEV1_PerPred`, `FVC_PerPred`, `Tiff_PerPred`, `PEF_PerPred`, `FEF25_PerPred`, `FEF50_PerPred`, `FEF75_PerPred`, `FEF25_75_PerPred`
  * Sets `signal_finalized = True` upon completion

---

## Internal Attributes (Post-finalization)

* `FEV1`, `FVC`, `Tiff`, `PEF`, `FEF25`, `FEF50`, `FEF75`, `FEF25_75`
* Predicted percentages: `FEV1_PerPred`, `FVC_PerPred`, `Tiff_PerPred`, `PEF_PerPred`, `FEF25_PerPred`, `FEF50_PerPred`, `FEF75_PerPred`, `FEF25_75_PerPred`
* `index1`, `index2`: Start and end indices of the FE segment
* `signal_finalized`: Flag indicating processing completion

---

## Notes

* Always run `correct_data_positioning()` and `standerdize_units()` before performing calculations or acceptability checks
* `shift_TLC_to_orgin()` should be applied if starting volume origin needs to be reset
* Plotting methods visualize raw and processed signals for verification
* ECCS93 reference computations depend on gender, age, and height

---

## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow, patientID='P1', trialID='T1', flag_given_signal_is_FE=False)
sp.correct_data_positioning()
sp.standerdize_units()
accepted, reason = sp.check_acceptability_of_spirogram()
if accepted:
    sp.finalize_signal(sex=1, age=35, height=175)
    print(sp.FEV1, sp.FVC, sp.PEF, sp.FEV1_PerPred)
```

---

## Dependencies

* `numpy`
* `matplotlib.pyplot`
* `scipy.signal.butter`, `scipy.signal.lfilter`
* `peakutils`

Make sure these libraries are installed before using the class.

---

## Licensing

This module is intended for educational and research purposes. If used clinically or commercially, ensure proper validation and compliance with medical device regulations.
