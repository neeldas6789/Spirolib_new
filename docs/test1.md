# Spirolib

A Python library for processing and analyzing spirometry data.

## Features

- Spiro signal processing utilities
- Feature extraction from spirograms (full and lite versions)
- Batch processing of spirometry trials
- Utility functions: flow/volume conversions, sampling, noise addition, plotting, and grayscale rendering

## Installation

Install via pip:

```bash
pip install spirolib
```

Or clone the repository:

```bash
git clone https://github.com/neeldas6789/Spirolib_new.git
```

## Usage

Import the modules in your Python scripts:

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

spirolib/ – Core library modules:
```
__init__.py
foo.py
spiro_signal_process.py
spiro_features_extraction.py
spiro_features_lite.py
spiro_batch_process.py
utilities.py
```

docs/ – Documentation and guides