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
    scale1
)
```

### Parameters
* `time`: Time array of the spirometry manoeuvre (list or 1D array). Units will be multiplied by `scale1` on import.
* `volume`: Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`: Flow array (list or 1D array, preferably in litres/sec)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean flag indicating if the signal is forced expiration only
* `scale1`: Numeric factor to apply to `time` (e.g., 0.001 to convert ms to s)

---

### Core Methods

#### Data Preprocessing
* `correct_data_positioning(flip_vol=False, flip_flow=False)`
  * Ensures signal orientation is standard (expiratory FVL right skewed and PEF positive)
* `standerdize_units()`
  * Converts all input data units to litres and seconds
* `manual_trim(begin_time=0, end_time=None)`
  * Trims the signal between the given time bounds

#### Plotting
* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  * Plots the flow-volume loop or time-series of volume and flow

#### Signal Processing Helpers
* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`
  * Implements low-pass filtering using Butterworth filters
* `smooth_FVL_start(time, vol, flow)`
  * Smoothens the FVL at the start of FE

#### Index Detection
* `get_Indexes_In_1s(start_index=0)`
  * Returns index at 1 s from the given start point
* `get_PEF_index(indx1, indx2)`
  * Identifies the index corresponding to Peak Expiratory Flow (PEF)
* `get_FE_start_end(...)`  
  * Determines the indices corresponding to the start and end of forced expiration
* `get_FI_start(index1=None)`
  * Gets the start index of forced inspiration

#### FE Signal Extraction
* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`
  * Returns FE segment (time, volume, flow) with optional BEV or threshold-based padding

#### Trimming & Thresholding
* `backExtrapolate_FEstart()`
  * Uses back-extrapolation from PEF to determine FE start
* `threshPEF_FEstart(thresh_percent_begin)`
  * Uses a percentage of PEF to define FE start
* `trim_FE_end(thresh_percent_end)`
  * Uses a percentage of PEF to define FE end

#### Acceptability Checks & Finalization
* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`
  * Evaluates acceptability of the spirometry signal
* `finalize_signal(sex=None, age=None, height=None)`
  * Computes all spirometry parameters (FEV1, FVC, PEF, FEFs) and reference percentages

---

## Notes
* Always run `correct_data_positioning()` and `standerdize_units()` before calculations or acceptability checks.
* `scale1` ensures correct time units on import.

---

## Example Workflow
```python
sp = spiro_signal_process(time, volume, flow, 'P1', 'T1', False, scale1=0.001)
sp.correct_data_positioning()
sp.standerdize_units()
accepted, reason = sp.check_acceptability_of_spirogram()
if accepted:
    sp.finalize_signal(sex=1, age=35, height=175)
    print(sp.FEV1, sp.FVC, sp.PEF)
```
