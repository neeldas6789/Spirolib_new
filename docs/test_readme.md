# Spirolib

A Python library for processing and analyzing spirometry data.

## Features

- Batch processing of spirometry trials (`spiro_trialsbatch_process`, `spiro_batch_process`)
- Spirometry signal processing utilities (`spiro_signal_process`)
- Traditional feature extraction (`spiro_features_lite`)
- Advanced feature extraction and modeling (`spiro_features_extraction`)
- Data visualization and modeling support via `utilities`

## Installation

Clone the repository:
```bash
git clone https://github.com/neeldas6789/Spirolib_new.git
cd Spirolib_new
```

Install required packages:
```bash
pip install numpy scipy matplotlib peakutils scikit-learn scikit-image
```

## Usage

Import and use modules in your Python scripts:
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
Spirolib_new/
├── spirolib/
│   ├── __init__.py
│   ├── spiro_signal_process.py
│   ├── spiro_features_extraction.py
│   ├── spiro_features_lite.py
│   ├── spiro_batch_process.py
│   └── utilities.py
└── docs/
    ├── spiro_signal_process.md
    ├── spiro_features_extraction.md
    └── test_readme.md
```
