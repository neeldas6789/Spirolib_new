# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow–volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

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

* `time`                    : Time array of the spirometry manoeuvre (list or 1D array, units configurable)
* `volume`                  : Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`                    : Flow array (list or 1D array, preferably in litres/sec)
* `patientID`               : Unique identifier for the patient
* `trialID`                 : Identifier for the trial
* `flag_given_signal_is_FE` : Boolean flag indicating if the provided signal is forced expiration only
* `scale2`                  : Scaling factor applied to the time vector (e.g., to convert input units to seconds)

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`
  * Ensures expiratory FVL is right skewed and PEF is positive by optionally flipping volume/flow.

* `standerdize_units()`
  * Converts all data arrays to standard units (litres and seconds).

* `manual_trim(begin_time=0, end_time=None)`
  * Trims the signal at specified time bounds and ensures continuity at endpoints.

* `shift_TLC_to_orgin()`
  * Re-centers volume so TLC is at zero (requires FE indices to be set).

* `smooth_FVL_start(time, vol, flow)`
  * Smoothens the initial rising limb of the FVL for improved quality.

---

### Plotting

* `plotFVL(only_FVL=False, show_ID=True, add_text="", only_FE=False, color='black', dpi=100, figsize=None, grid_on=True)`
  * Plots the flow–volume loop or combined time–series (volume/time and flow/time).

---

### Signal Processing Helpers

* `butter_lowpass(cutoff, fs, order)` / `butter_lowpass_filter(data, cutoff, fs, order)`
  * Low-pass filtering via a Butterworth filter.

---

### Index Detection

* `get_Indexes_In_1s(start_index=0)`
  * Returns the index corresponding to 1-second into the signal.

* `get_PEF_index(indx1, indx2)`
  * Identifies the index of Peak Expiratory Flow (PEF) between two bounds.

* `get_FE_start_end(...)`
  * Determines start/end indices of the FE manoeuvre using BEV or threshold–PEF methods.

* `backExtrapolate_FEstart()`
  * Uses back-extrapolation from PEF to find FE start and validate BEV criteria.

* `threshPEF_FEstart(thresh_percent_begin)`
  * Identifies FE start based on a percentage threshold of PEF.

* `trim_FE_end(thresh_percent_end)`
  * Identifies FE end based on a percentage threshold of PEF.

* `get_FI_start(index1=None)`
  * Finds the start index of forced inspiration for combined FI–FE signals.

---

### FE Signal Extraction

* `get_FE_signal(start_type=None, thresh_percent_begin=2, thresh_percent_end=0.25, plot=False)`
  * Extracts the FE segment (time, volume, flow) with optional zero-padding for BEV or threshold start types.

---

### Acceptability Checks

* `check_rise_to_PEF()`
  * Confirms a proper rise to PEF exists.

* `check_largest_time_interval(max_time_interval=1, FE_time_duration=4)`
  * Ensures no large gaps in time sampling.

* `check_acceptability_of_spirogram(min_FE_time=6, thresh_percent_end=0.5)`
  * Validates the spirometry manoeuvre against acceptability criteria, including BEV threshold.

---

### Spirometry Parameter Computation

* `calc_FEV1_FVC()`
  * Interpolates 1-second expired volume (FEV1) and computes final FVC.

* `calc_flow_parameters()`
  * Computes PEF, FEF25, FEF50, FEF75, and FEF25–75 from the FE segment.

---

### Reference Prediction (ECCS93)

* `calc_ECCS93_ref(param)`
  * Returns ECCS93-predicted reference values for FEV1, FVC, PEF, and other parameters.

---

### Finalization

* `finalize_signal(sex=None, age=None, height=None)`
  * After acceptability checks and unit corrections, computes all spirometry metrics and predicted percentages.

---

## Example Workflow

```python
sp = spiro_signal_process(
    time, volume, flow,
    patientID='P1', trialID='T1',
    flag_given_signal_is_FE=False,
    scale2=0.001
)
sp.correct_data_positioning()
sp.standerdize_units()
accepted, msg = sp.check_acceptability_of_spirogram()
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

Intended for educational and research use. For clinical application, ensure proper validation and regulatory compliance.
