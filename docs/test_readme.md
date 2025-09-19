# Spirolib

A Python library for processing and analyzing spirometry data.

## Features

- Batch processing of spirometry data (`spiro_batch_process`, `spiro_trialsbatch_process`)
- Feature extraction from spirometry signals (`spiro_features_extraction`, `spiro_features_lite`)
- Signal processing utilities (`spiro_signal_process`, `utilities`)

## Installation

Clone the repository and add it to your Python path, or install via pip:

```bash
git clone https://github.com/neeldas6789/Spirolib_new.git
cd Spirolib_new
pip install .
```

## Usage

Import the modules from the `spirolib` package in your Python scripts:

```python
from spirolib.spiro_signal_process import spiro_signal_process
from spirolib.spiro_features_extraction import spiro_features_extraction
from spirolib.sp
iro_features_lite import spiro_features_lite
```

## Project Structure

- `spirolib/` – Main library source code
- `docs/` – Documentation and guides

