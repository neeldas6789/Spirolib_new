# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array)
* `volume`: Volume array of the manoeuvre (list or 1D array)
* `flow`: Flow array of the manoeuvre (list or 1D array)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean flag indicating if the signal is forced expiration only
* `scale`: Scale factor applied to the time array to convert to seconds (e.g., 0.001 if input time is in milliseconds)

---
## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`
  * Ensures expiratory FVL is right-skewed and PEF is positive

* `standerdize_units()`
  * Converts volume to litres and flow/time to seconds

* `manual_trim(begin_time=0, end_time=None)`
  * Trims the signal between the specified time bounds

---
### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  * Plots FVL or time-series of volume/flow

---
### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`
* `smooth_FVL_start(time, vol, flow)`

---
### Index Detection

* `get_Indexes_In_1s(start_index=0)`
* `get_PEF_index(indx1, indx2)`
* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`
* `get_FI_start(index1=None)`

---
### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`

---
### Trimming & Thresholding

* `backExtrapolate_FEstart()`
* `threshPEF_FEstart(thresh_percent_begin)`
* `trim_FE_end(thresh_percent_end)`

---
### Acceptability Checks

* `check_rise_to_PEF()`
* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`
* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`

---
### Spirometry Parameter Computation

* `calc_FEV1_FVC()`
* `calc_flow_parameters()`

---
### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`

---
### Finalization

* `finalize_signal(sex=None, age=None, height=None)`

---
## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow, 'P1', 'T1', False, 0.001)
sp.correct_data_positioning()
sp.standerdize_units()
accepted, reason = sp.check_acceptability_of_spirogram()
```