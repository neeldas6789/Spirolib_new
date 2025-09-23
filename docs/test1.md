## Spirolib
A Python library for processing and analyzing spirometry data.

## Features
- Batch processing of spirometry data (spiro_trialsbatch_process, spiro_batch_process)
- Signal processing utilities (spiro_signal_process)
- Feature extraction from spiro signals (spiro_features_extraction)
- Lightweight feature extraction (spiro_features_lite)
- Additional utilities: flow/volume conversion, sampling, noise addition, grayscale conversion, plotting (utilities)

## Installation
Clone the repository and install:

```bash
git clone https://github.com/neeldas6789/Spirolib_new.git
cd Spirolib_new
pip install -e .
```

## Usage
Import modules directly from the package:

```python
from spirolib import spiro_signal_process, spiro_features_extraction, spiro_features_lite, spiro_batch_process, utilities
```

Or import the package and explore its components:

```python
import spirolib
help(spirolib)
```

## Project Structure
spirolib/ - Main refactored spirolib code  
  __init__.py  
  foo.py  
  spiro_signal_process.py  
  spiro_features_extraction.py  
  spiro_features_lite.py  
  spiro_batch_process.py  
  utilities.py  

docs/ - Documentation and guides  
old/ - Legacy monolithic module