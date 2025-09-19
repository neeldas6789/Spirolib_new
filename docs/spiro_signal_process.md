# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(
    time,
    volume,
    flow,
    patientID,
    trialID,
    flag_given_signal_is_FE,
    scale
)
```

- `scale`: multiplier applied to input `time` array to convert units to seconds (e.g., if `time` is in milliseconds, use `scale=1/1000`).

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array, units scaled by `scale` to seconds)
* `volume`: Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`: Flow array (list or 1D array, preferably in litres/sec)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean flag indicating if the signal is forced expiration only

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`

  * Ensures signal orientation is standard (expiratory FVL right skewed and PEF positive)

* `standerdize_units()`

  * Converts all array units to litres and seconds

* `manual_trim(begin_time=0, end_time=None)`

  * Trims the signal based on provided time bounds and pads start/end as needed

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`

  * Plots the flow-volume loop (FVL) or time-series representations of volume and flow

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`

  * Implements low-pass filtering using Butterworth filters

* `smooth_FVL_start(time, vol, flow)`

  * Smoothens the beginning of FE FVL for better shape quality

### Index Detection

* `get_Indexes_In_1s(start_index=0)`

  * Returns the index corresponding to 1 second from the given start point

* `get_PEF_index(indx1, indx2)`

  * Identifies the index corresponding to Peak Expiratory Flow (PEF)

* `get_FE_start_end(...)`

  * Determines the start and end indices of forced expiration based on BEV or PEF thresholds

* `get_FI_start(index1=None)`

  * Finds the start index of forced inspiration (FI)

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`

  * Extracts the FE segment (time, volume, flow) and optionally plots it. For `BEV` or `thresh_PEF` start types, the output signals are padded to start/end at zero.

---

## Acceptability Checks

* `check_rise_to_PEF()`
  * Verifies a rise to PEF in the signal

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`
  * Checks for large time gaps in the sampling

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`
  * Evaluates overall signal acceptability, including BEV criteria

---

## Spirometry Parameter Computation

* `calc_FEV1_FVC()`
  * Calculates FEV1 and FVC using interpolated volume at 1 second

* `calc_flow_parameters()`
  * Computes PEF, FEF25, FEF50, FEF75, and FEF25-75 parameters

---

## Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`
  * Returns predicted reference values (FVC, FEV1, PEF, etc.) using ECCS93 equations

---

## Finalization

* `finalize_signal(sex=None, age=None, height=None)`
  * Finalizes processing, calculates standard parameters, and reference percentages; signals and indices are set if not already determined

---

## Internal Attributes (Post-finalization)

* `FEV1`, `FVC`, `Tiff`, `PEF`, `FEF25`, `FEF50`, `FEF75`, `FEF25_75`
* Reference percentages: `FEV1_PerPred`, `FVC_PerPred`, etc.
* `index1`, `index2`: Start/end indices of FE segment
* `signal_finalized`: Flag indicating processing completion
