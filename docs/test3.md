## Spirolib
A Python library for processing and analyzing spirometry data.

## Features
- Signal processing of spirometry data (spiro_signal_process)
- Advanced feature extraction (spiro_features_extraction)
- Lightweight feature extraction (spiro_features_lite)
- Batch processing of spirometry data (spiro_batch_process & spiro_trialsbatch_process)
- Utility functions for spirometry data processing (utilities)

## Installation
Clone the repository:
```bash
git clone https://github.com/neeldas6789/Spirolib_new.git
```
Install the package:
```bash
cd Spirolib_new
pip install .
```

## Usage
Import the modules from the spirolib package in your Python scripts:
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
spirolib/ - Core spirolib code

docs/ - Documentation and guides