## Spirolib
A Python library for processing and analyzing spirometry data.

## Features
- Batch processing of spirometry data (`spiro_batch_process`, `spiro_trialsbatch_process`)
- Advanced signal processing routines (`spiro_signal_process`)
- Comprehensive feature extraction (`spiro_features_extraction`)
- Lightweight feature extraction (`spiro_features_lite`)
- Utility functions for data transformation and visualization (`utilities`)

## Installation
Clone the repository and install in editable mode::

    git clone https://github.com/neeldas6789/Spirolib_new.git
    cd Spirolib_new
    pip install -e .

## Usage
Import the modules you need from the `spirolib` package::

    from spirolib import spiro_signal_process, spiro_features_extraction, utilities
    # initialize and call functions as shown in examples

## Project Structure
spirolib/    - Core package modules
  ├── spiro_signal_process.py
  ├── spiro_features_extraction.py
  ├── spiro_features_lite.py
  ├── spiro_batch_process.py
  ├── utilities.py

docs/        - Documentation and guides