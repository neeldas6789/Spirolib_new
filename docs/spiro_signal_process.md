# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale2)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array, preferably in seconds)
* `volume`: Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`: Flow array (list or 1D array, preferably in litres/sec)
* `patientID`: Unique identifier for the patient (string or number)
* `trialID`: Identifier for the trial (string or number; use `'Best'` if selecting the best trial)
* `flag_given_signal_is_FE`: Boolean flag indicating if the provided signal is forced expiration only
* `scale2`: Numeric scale factor applied to the input `time` array (e.g., to convert units)

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`

  Ensures the expiratory FVL is right-skewed and PEF is positive by optionally flipping the volume and/or flow signals.

* `standerdize_units()`

  Converts all input data units to litres and seconds by dividing volume and flow by 1000 and time by `scale2` if applied earlier.

* `manual_trim(begin_time=0, end_time=None)`

  Trims the signal between the specified time bounds, padding the start or end with zeros as needed.

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`

  Plots the flow-volume loop or, if `only_FVL=False`, a 1×3 panel showing FVL, volume–time, and flow–time.

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`

  Implements low-pass filtering using a Butterworth filter design.

* `smooth_FVL_start(time, vol, flow)`

  Smoothens the beginning of the FE FVL to eliminate negative dips before PEF.

### Index Detection

* `get_Indexes_In_1s(start_index=0)`

  Returns the index corresponding to 1 s after the given start index.

* `get_PEF_index(indx1, indx2)`

  Identifies the index of peak expiratory flow between `indx1` and `indx2`.

* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`

  Determines the start (back extrapolation or PEF threshold) and end (PEF threshold) indices of forced expiration.

* `get_FI_start(index1=None)`

  Finds the start index of forced inspiration preceding expiration.

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`

  Extracts and returns the FE time, volume, and flow signals (padded with zeros at start and end for certain `start_type`).

### Trimming & Thresholding

* `backExtrapolate_FEstart()`

  Uses a back-extrapolation method based on PEF to locate the FE start and validate the BEV criterion.

* `threshPEF_FEstart(thresh_percent_begin)`

  Uses a percentage threshold of PEF to find when FE begins.

* `trim_FE_end(thresh_percent_end)`

  Uses a percentage threshold of PEF to find when FE ends.

### Acceptability Checks

* `check_rise_to_PEF()`

  Verifies that the flow signal rises from zero to PEF.

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`

  Ensures there are no large time gaps in the early signal.

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`

  Evaluates overall signal quality and returns `(accepted: bool, reason: str)`.

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`

  Calculates FEV1 (interpolated at 1 s) and FVC from the FE volume-time curve.

* `calc_flow_parameters()`

  Computes PEF, FEF25, FEF50, FEF75, and FEF25-75 indices.

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`

  Returns the ECCS93-predicted reference value for the given parameter.

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`

  After acceptability checks and unit standardization, computes and stores FEV1, FVC, PEF, FEF25/50/75, Tiffeneau index, and their % predicted values. Sets `signal_finalized = True`.

---

## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow, patientID='P1', trialID='T1', flag_given_signal_is_FE=False, scale2=1)
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

Make sure these libraries are installed before using the class.

---

## Licensing

This module is intended for educational and research purposes. For clinical or commercial use, ensure proper validation and regulatory compliance.
