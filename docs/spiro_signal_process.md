# Documentation: `spiro_signal_process`

The `spiro_signal_process` class provides tools to analyze spirometry data, particularly for handling flow-volume loops (FVLs), forced expiratory manoeuvres (FE), and computing standard spirometry parameters such as FEV1, FVC, and PEF.

## Class Initialization

```python
sp = spiro_signal_process(
    time,                        # list or 1D array: time of manoeuvre
    volume,                      # list or 1D array: volume (preferably in litres)
    flow,                        # list or 1D array: flow (preferably in litres/s)
    patientID,                   # unique patient ID
    trialID,                     # trial identifier (number or 'Best')
    flag_given_signal_is_FE,     # Boolean: True if input is forced expiration only
    scale1                       # numeric scale factor to adjust time units
)
```

### Parameters

* `time`: Time vector of spirometry manoeuvre
* `volume`: Volume vector of manoeuvre
* `flow`: Flow vector of manoeuvre
* `patientID`: Unique identifier for patient
* `trialID`: Identifier for the trial
* `flag_given_signal_is_FE`: Whether the provided signal is FE only
* `scale1`: Scaling factor applied to `time` (e.g., 1 for seconds, 1000 for milliseconds)
