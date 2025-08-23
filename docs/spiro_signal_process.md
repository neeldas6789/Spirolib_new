# spiro_signal_process

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale)
```

### Parameters

1. `time`                         – Time of spirometry manoeuvre (list or 1D array, any unit before scaling)
2. `volume`                       – Volume of manoeuvre (list or 1D array, preferably in litres)
3. `flow`                         – Air-flow of manoeuvre (list or 1D array, preferably in litres/s)
4. `patientID`                    – Unique patient ID (string or number)
5. `trialID`                      – Trial number or identifier (string or number; e.g., 'Best')
6. `flag_given_signal_is_FE`      – Boolean indicating if provided signal is forced expiration only
7. `scale`                        – Numeric factor multiplied with `time` to standardize units (e.g., 0.001 to convert ms→s)

#### Notes
- The constructor internally applies `self.time = np.array(time) * scale`.
- The flow-volume data should be arranged so that the expiratory FVL is right-skewed and PEF is positive.

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`  
  Ensures correct orientation (expiratory FVL right skewed; PEF positive)

* `standerdize_units()`  
  Converts all units to litres (volume/flow) and seconds (time)

* `manual_trim(begin_time=0, end_time=None)`  
  Trims the signal between provided time bounds (adds 0-padding at start/end)

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`  
  Plots the flow-volume loop or time-series representations of volume and flow

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)`  /  `butter_lowpass_filter(data, cutoff, fs, order)`  
  Implements Butterworth low-pass filtering

* `smooth_FVL_start(time, vol, flow)`  
  Smooths initial part of FE loop for improved shape

### Index Detection

* `get_Indexes_In_1s(start_index=0)`  
  Returns index corresponding to 1 s from a given start

* `get_PEF_index(indx1, indx2)`  
  Identifies index of Peak Expiratory Flow (PEF)

* `get_FE_start_end(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.5, check_BEV_criteria=False)`  
  Determines start/end indices of forced expiration

* `get_FI_start(index1=None)`  
  Finds start index of forced inspiration (for combined signals)

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`  
  Returns FE segment (time, volume, flow) with optional plotting and zero-padding for BEV or thresholded start/end

### Trimming & Thresholding

* `backExtrapolate_FEstart()`  
  Performs back-extrapolation to detect FE start and checks BEV criteria

* `threshPEF_FEstart(thresh_percent_begin)`  
  Uses PEF threshold to detect FE start

* `trim_FE_end(thresh_percent_end)`  
  Uses PEF threshold to detect FE end

### Acceptability Checks

* `check_rise_to_PEF()`  
  Verifies that flow rises to a valid PEF

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`  
  Ensures no large gaps in the recorded signal

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`  
  Evaluates overall spirogram acceptability (including BEV criteria)

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`  
  Calculates FEV1 (interpolated at 1 s) and FVC

* `calc_flow_parameters()`  
  Computes PEF, FEF25, FEF50, FEF75, and FEF25-75

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`  
  Returns predicted reference value for a given parameter (e.g., 'FVC', 'PEF')

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`  
  Must be called after acceptability checks; calculates and stores all parameters and % predicted values

---

## Internal Attributes (Post-finalization)

* `index1`, `index2` – Start/end indices of FE segment
* `FEV1`, `FVC`, `Tiff` (FEV1/FVC), `PEF`, `FEF25`, `FEF50`, `FEF75`, `FEF25_75`
* `% predicted` values: `FEV1_PerPred`, `FVC_PerPred`, etc.
* `signal_finalized` – Boolean flag indicating completion

---

## Example Workflow

```python
sp = spiro_signal_process(time, volume, flow, patientID='P1', trialID='T1', flag_given_signal_is_FE=False, scale=1)
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

Intended for educational and research use. Validate clinically before diagnostic applications.
