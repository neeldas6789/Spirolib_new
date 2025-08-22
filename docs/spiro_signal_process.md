# spiro_signal_process

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (array, in seconds)
* `volume`: Volume array of the manoeuvre (array, in litres)
* `flow`: Flow array (array, in litres/sec)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean indicating if the signal is forced expiration only

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`
  * Ensures signal orientation is standard (expiratory FVL right skewed and PEF positive)

* `standerdize_units()`
  * Converts all input data units to litres and seconds

* `manual_trim(begin_time=0, end_time=None)`
  * Trims the signal between the given time bounds

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  * Plots the flow-volume loop or time-series of volume and flow

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`
  * Low-pass filtering via Butterworth design

* `smooth_FVL_start(time, vol, flow)`
  * Smoothens the start of FE FVL for artifact removal

### Index Detection

* `get_Indexes_In_1s(start_index=0)`
  * Returns index at 1 second from a start point

* `get_PEF_index(indx1, indx2)`
  * Identifies Peak Expiratory Flow (PEF) index

* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`
  * Determines start/end indices of forced expiration via BEV or threshold methods

* `get_FI_start(index1=None)`
  * Finds the start of forced inspiration (for combined signals)

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`
  * Extracts and optionally plots the FE segment (time, volume, flow)

### Acceptability Checks

* `check_rise_to_PEF()`
  * Confirms presence of initial rise to PEF

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`
  * Checks for uniform sampling by detecting time gaps

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`
  * Evaluates spirometry acceptability, including BEV criteria and time bounds

### Parameter Computation

* `calc_FEV1_FVC()`
  * Calculates FEV1 and FVC using interpolated 1-second volume

* `calc_flow_parameters()`
  * Computes PEF, FEF25, FEF50, FEF75, FEF25-75

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`
  * Returns ECCS93-predicted values for parameters (FVC, FEV1, PEF, etc.)

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`
  * Completes all processing, calculates metrics, and stores them. Automatically computes FE indices if unset.

---

## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow, 'P1', 'T1', False)
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
* `scipy.signal` (butter, lfilter)
* `peakutils`

---

## Notes

Ensure `correct_data_positioning()` and `standerdize_units()` run before acceptability checks or metric calculations.