# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale1)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array, preferably in seconds)
* `volume`: Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`: Flow array (list or 1D array, preferably in litres/sec)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean flag indicating if the signal is forced expiration only
* `scale1`: Scaling factor to multiply the input `time` array (e.g., to convert units)

---

## Core Methods

### Data Preprocessing

* `correct_data_positioning(flip_vol=False, flip_flow=False)`

  * Ensures signal orientation is standard (expiratory FVL right skewed and PEF positive)

* `standerdize_units()`

  * Converts all input data units to litres and seconds

* `manual_trim(begin_time=0, end_time=None)`

  * Trims the signal between the given time bounds

---

## Example Workflow

```python
# Instantiate with scale factor = 1 (no time scaling)
sp = spiro_signal_process(time, volume, flow, patientID='P1', trialID='T1', flag_given_signal_is_FE=False, scale1=1)
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

This module is intended for educational and research purposes. If used clinically or commercially, ensure proper validation and compliance with medical device regulations.
