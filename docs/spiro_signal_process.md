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
    scale2
)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array, units may vary)
* `volume`: Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`: Flow array (list or 1D array, preferably in litres/sec)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean flag indicating if the signal is forced expiration only
* `scale2`: Numeric factor applied to `time` to convert input time units to seconds

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`  
  Ensures signal orientation is standard (expiratory FVL right skewed and PEF positive).
* `standerdize_units()`  
  Converts all signals to litres and seconds.
* `manual_trim(begin_time=0, end_time=None)`  
  Trims the signal between the given time bounds.
* `smooth_FVL_start(time, vol, flow)`  
  Smoothens early FE by fitting a polynomial to remove initial negative dips.
* `shift_TLC_to_origin()`  
  Re-centers volume so that TLC (start of FE) is at zero.

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`  
  Plots the flow-volume loop (FVL) or time-series representations.

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`  
  Implements low-pass filtering using Butterworth filters.

### Index Detection

* `get_Indexes_In_1s(start_index=0)`  
  Returns index at 1 s from the given start point.
* `get_PEF_index(indx1, indx2)`  
  Identifies the index of Peak Expiratory Flow (PEF).
* `get_FE_start_end(...)`  
  Determines the start and end indices of forced expiration.
* `get_FI_start(index1=None)`  
  Gets the start index of forced inspiration.

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`  
  Returns FE segment (time, volume, flow) and optionally plots. Pads start/end with zeros for FE.

### Trimming & Thresholding

* `backExtrapolate_FEstart()`  
  Uses back-extrapolation to detect FE start and validate BEV criteria.
* `threshPEF_FEstart(thresh_percent_begin)`  
  Finds FE start based on a percentage of PEF.
* `trim_FE_end(thresh_percent_end)`  
  Finds FE end based on a percentage of PEF.

### Acceptability Checks

* `check_rise_to_PEF()`  
  Confirms presence of an initial rise to PEF.
* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`  
  Checks for large gaps in the signal.
* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`  
  Evaluates signal acceptability and applies BEV criteria.

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`  
  Calculates FEV1 and FVC using interpolated 1-s volume.
* `calc_flow_parameters()`  
  Computes PEF, FEF25, FEF50, FEF75, and FEF25-75.

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`  
  Returns predicted value for a given parameter using ECCS93 equations.

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`  
  Finalizes signal, shifts TLC to origin, computes FEV1, FVC, PEF, FEFs, and predicted percentages.

---

## Example Workflow

```python
sp = spiro_signal_process(
    time,
    volume,
    flow,
    patientID='P1',
    trialID='T1',
    flag_given_signal_is_FE=False,
    scale2=1  # converts input time units to seconds
)
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

---

## Licensing

Intended for educational and research use. Validate before clinical application.
