# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale3)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array; preferably in seconds)
* `volume`: Volume array of the manoeuvre (list or 1D array; preferably in litres)
* `flow`: Flow array (list or 1D array; preferably in litres/sec)
* `patientID`: Unique identifier for the patient (string or number)
* `trialID`: Identifier for the trial (string or number; use `'Best'` if only one)
* `flag_given_signal_is_FE`: Boolean flag indicating if the provided signal is forced expiration only
* `scale3`: Scaling factor applied to the `time` vector (e.g., `1` if `time` is already in seconds)

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`
  * Converts signal orientation so that the expiratory FVL is right-skewed and PEF is positive.

* `standerdize_units()`
  * Converts all input data units to litres and seconds.

* `manual_trim(begin_time=0, end_time=None)`
  * Trims the signal between the specified time bounds, padding endpoints appropriately.

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  * Plots the flow-volume loop or time-series representations of volume and flow.

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`
  * Implements low-pass filtering via a Butterworth design.

* `smooth_FVL_start(time, vol, flow)`
  * Smoothens the start of the FE FVL for improved shape quality.

### Index Detection

* `get_Indexes_In_1s(start_index=0)`
  * Returns the index corresponding to 1 s after `start_index`.

* `get_PEF_index(indx1, indx2)`
  * Identifies the index of peak expiratory flow (PEF) between two bounds.

* `get_FE_start_end(...)`
  * Determines the start and end indices of the forced expiration segment, with options for back-extrapolation or threshold-based methods.

* `get_FI_start(index1=None)`
  * Finds the start index of forced inspiration in a combined FI-FE signal.

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`
  * Extracts the FE segment (time, volume, flow), pads for BEV or PEF-based starts, and optionally plots.

### Trimming & Thresholding

* `backExtrapolate_FEstart()`
  * Uses back-extrapolation from PEF to refine the FE start.

* `threshPEF_FEstart(thresh_percent_begin)`
  * Identifies FE start based on a percentage of PEF.

* `trim_FE_end(thresh_percent_end)`
  * Identifies FE end based on a percentage of PEF.

### Acceptability Checks

* `check_rise_to_PEF()`
  * Verifies that flow rises from zero to PEF.

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`
  * Ensures no large gaps in the time sampling.

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`
  * Validates the spirometry curve by multiple criteria (rise to PEF, BEV criteria, time bounds).

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`
  * Calculates FEV1 (interpolated at 1 s) and FVC.

* `calc_flow_parameters()`
  * Computes PEF, FEF25, FEF50, FEF75, and FEF25-75 from the FE segment.

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`
  * Returns reference values (e.g., FEV1, FVC, PEF) based on ECCS93 formulas for a given parameter.

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`
  * After acceptability, computes and stores standard spirometry parameters and reference percentages; also sets `index1`/`index2` if unset.

### Attributes (Post-Finalization)

* Flow/volume outputs: `FEV1`, `FVC`, `Tiff`, `PEF`, `FEF25`, `FEF50`, `FEF75`, `FEF25_75`
* Reference percentages: `FEV1_PerPred`, `FVC_PerPred`, etc.
* Indices of FE segment: `index1`, `index2`
* `signal_finalized`: Boolean flag indicating completion.

---

## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow, patientID='P1', trialID='T1', flag_given_signal_is_FE=False, scale3=1)
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
* `scipy.signal` (Butterworth filter)
* `peakutils`

---

## Licensing

Intended for research and educational use; clinical applications require validation.
