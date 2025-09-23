# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale1)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array)
* `volume`: Volume array of the manoeuvre (list or 1D array)
* `flow`: Flow array of the manoeuvre (list or 1D array)
* `patientID`: Unique identifier for the patient (string or number)
* `trialID`: Identifier for the trial (string or number)
* `flag_given_signal_is_FE`: Boolean flag indicating if the signal is forced expiration only
* `scale1`: Numeric scaling factor applied to `time` (e.g., 1 for seconds, 1000 to convert ms to s)

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

... (rest unchanged)