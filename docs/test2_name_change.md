# Spirolib
A Python library for processing and analyzing spirometry data.

## Features
* Batch processing of spirometry trials (`spiro_trialsbatch_process`, `spiro_batch_process`)
* Signal processing utilities (`utilities`, low‐pass filtering, noise augmentation)
* Spirometry signal handling and parameter computation (`spiro_signal_process`)
* Feature extraction from FE loops (`spiro_features_extraction`, `spiro_features_lite`)

## Installation
Clone the repository and import the `spirolib` package into your Python project.

```bash
git clone https://github.com/neeldas6789/Spirolib_new.git
cd Spirolib_new
# then in Python:
# from spirolib import spiro_signal_process, utilities, ...
```

## Usage
Import modules from the `spirolib` namespace in your scripts:
```python
from spirolib import (
    spiro_signal_process,
    spiro_features_extraction,
    spiro_features_lite,
    spiro_trialsbatch_process,
    spiro_batch_process,
    utilities
)
```

## Project Structure
```
spirolib/  # Core library modules
docs/      # User guides and API reference
```