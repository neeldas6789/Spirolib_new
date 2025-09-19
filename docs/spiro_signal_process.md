# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
# Now includes scale1 parameter to scale time into seconds
sp = spiro_signal_process(time, volume, flow, patientID, trialID, flag_given_signal_is_FE, scale1)
```

### Parameters

* `time`: Time array of the spirometry manoeuvre (list or 1D array, preferably in seconds)
* `volume`: Volume array of the manoeuvre (list or 1D array, preferably in litres)
* `flow`: Flow array (list or 1D array, preferably in litres/sec)
* `patientID`: Unique identifier for the patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Boolean flag indicating if the signal is forced expiration only
* `scale1`: Scale factor applied to `time` input to convert units into seconds (e.g., use 1 if time is already in seconds)

---

## Core Methods

... (rest unchanged)