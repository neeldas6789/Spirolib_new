# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale0)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array, units scaled by `scale0`; preferably in seconds)
* `volume`: Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`: Flow array of the manoeuvre (list or 1D array, preferably in litres/s)
* `patientID`: Unique identifier for the patient (string or number)
* `trialID`: Identifier for the trial (string or number; use `'Best'` if only one or best trial is available)
* `flag_given_signal_is_FE`: Boolean flag indicating if the given signal is forced expiration only
* `scale0`: Scale factor for raw time input (multiplies the `time` array). Use `1` for seconds or `1000` for milliseconds, etc.

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`

  This function repositions the data so that the expiratory FVL is right skewed and PEF is positive. Use `flip_vol=True` or `flip_flow=True` to invert the respective signals.

* `standerdize_units()`

  Converts all units to litres and seconds by dividing raw volume, flow, and time arrays by 1000.

* `manual_trim(begin_time=0, end_time=None)`

  Trims the signal based on provided begin and end times, ensuring padded zeros at the new boundaries.

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  
  Plots the flow-volume loop (FVL) or, if `only_FVL=False`, a three-panel figure showing FVL, volume-time, and flow-time plots.

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`

  Implements a Butterworth low-pass filter to smooth data.

* `smooth_FVL_start(time, vol, flow)`

  Smoothens the start of the forced expiratory FVL by fitting a polynomial to the initial segment and interpolating negative values.

### Index Detection

* `get_Indexes_In_1s(start_index=0)`

  Returns the index corresponding to 1 second from `start_index` in the time array.

* `get_PEF_index(indx1, indx2)`

  Identifies the Peak Expiratory Flow (PEF) index between `indx1` and `indx2`.

* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`

  Determines the start (`index1`) and end (`index2`) indices of forced expiration using BEV or threshold-based methods.

* `get_FI_start(index1=None)`

  Finds the start index of forced inspiration for combined FI-FE signals.

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`

  Extracts and returns the FE segment (time, volume, flow), padding zeros at the boundaries for BEV or threshold-based starts.

### Trimming & Thresholding

* `backExtrapolate_FEstart()`

  Uses back-extrapolation from PEF to curate the beginning of FE and checks BEV criteria.

* `threshPEF_FEstart(thresh_percent_begin)`

  Uses a percentage of PEF to define the FE start.

* `trim_FE_end(thresh_percent_end)`

  Uses a percentage of PEF to define the FE end.

### Acceptability Checks

* `check_rise_to_PEF()`

  Returns `False` if PEF occurs at index 0 (no rise), else `True`.

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`

  Verifies there are no large gaps in the time array within the first few seconds.

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`

  Conducts a series of checks on the spirogram and returns a tuple `(accepted: bool, reason: str)`.

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`

  Calculates FEV1 and FVC by interpolating the 1-second volume and final volume, returning rounded values.

* `calc_flow_parameters()`

  Computes key flow parameters: PEF, FEF25, FEF50, FEF75, and FEF25-75 using normalized volume.

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`

  Computes reference values for parameters (`FVC`, `FEV1`, `PEF`, etc.) based on ECCS93 equations.

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`

  Finalizes the signal by computing all spirometry parameters and their percent predicted values. Automatically computes start/end indices if missing.

### Internal Attributes (Post-finalization)

* `FEV1`, `FVC`, `Tiff`, `PEF`, `FEF25`, `FEF50`, `FEF75`, `FEF25_75`
* Percent-predicted values: `FEV1_PerPred`, `FVC_PerPred`, `Tiff_PerPred`, etc.
* `index1`, `index2`: start and end indices of FE segment
* `signal_finalized`: `True` once all parameters are calculated

---

## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow,
                            patientID='P1', trialID='T1',
                            flag_given_signal_is_FE=False,
                            scale0=1)
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

Ensure these packages are installed.

---

## Licensing

This module is intended for educational and research purposes. For clinical or commercial use, perform proper validation and comply with applicable regulations.
