# spiro_signal_process

The `spiro_signal_process` class provides comprehensive tools to process and analyze spirometry signals, with a focus on forced expiratory (FE) manoeuvres and flow-volume loops (FVLs).

## Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE)
```

- **time**: 1D array of time stamps in seconds
- **volume**: 1D array of volume in litres
- **flow**: 1D array of flow in litres/s
- **patientID**: Unique patient identifier
- **trialID**: Trial identifier (string or number)
- **flag_given_signal_is_FE**: `True` if the signal is forced expiration only

---

## Preprocessing Methods

- `correct_data_positioning(flip_vol=False, flip_flow=False)`
  - Ensures FVL is right-skewed and PEF is positive by optionally flipping volume or flow.
- `standerdize_units()`
  - Converts time (ms → s), volume (ml → L), and flow (ml/s → L/s).
- `manual_trim(begin_time=0, end_time=None)`
  - Trims the signal between specified start and end times.

---

## Plotting

- `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  - Plots FVL or time-series subplots of volume and flow.

---

## Signal Filtering

- `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`
  - Apply a Butterworth low-pass filter.
- `smooth_FVL_start(time, vol, flow)`
  - Smooths the start of the FE FVL for better curve shape.

---

## Index Detection

- `get_Indexes_In_1s(start_index=0)`
  - Returns the index corresponding to 1 s after `start_index`.
- `get_PEF_index(indx1, indx2)`
  - Finds Peak Expiratory Flow index between given bounds.
- `backExtrapolate_FEstart()` / `threshPEF_FEstart(thresh_percent_begin)` / `trim_FE_end(thresh_percent_end)`
  - Determine the start/end of FE via back-extrapolation or PEF thresholds.
- `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`
  - Returns indices `(index1, index2)` delineating the FE segment.
- `get_FI_start(index1=None)`
  - Finds the start of forced inspiration when combined FI-FE data are provided.

---

## Forced Expiration Extraction

- `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`
  - Extracts and zero-pads FE time, volume, and flow arrays based on `BEV` or `thresh_PEF` start types.

---

## Acceptability Checks

- `check_rise_to_PEF()`
  - Ensures the signal rises to PEF from the beginning.
- `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`
  - Checks for large gaps in sampling.
- `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`
  - Validates the spirogram based on 1 s volume, BEV criteria, time bounds, and artefact conditions. Returns `(accepted: bool, message: str)`.

---

## Parameter Calculations

- `calc_FEV1_FVC()`
  - Computes FEV1 at 1 s and final FVC with interpolation.
- `calc_flow_parameters()`
  - Calculates PEF, FEF25, FEF50, FEF75, and FEF25–75 from the FE segment.

---

## ECCS93 Reference Values

- `calc_ECCS93_ref(param)`
  - Returns ECCS93-predicted values for parameters (`FVC`, `FEV1`, `Tiff`, etc.) given `sex`, `age`, and `height` attributes.

---

## Finalization

- `finalize_signal(sex=None, age=None, height=None)`
  - After acceptability checks and optional unit/position corrections, computes all spirometry parameters (`FEV1`, `FVC`, `PEF`, etc.) and their % predicted. Sets `signal_finalized=True`.

---

## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow, 'P1', 'T1', False)
sp.correct_data_positioning()
sp.standerdize_units()
accepted, msg = sp.check_acceptability_of_spirogram()
if accepted:
    sp.finalize_signal(sex=1, age=35, height=175)
    print(sp.FEV1, sp.FVC, sp.PEF)
```
