## Spirolib
A Python library for processing and analyzing spirometry data.

## Features
- Batch processing of spirometry data (spiro_trialsbatch_process, spiro_batch_process)
- Full feature extraction (spiro_features_extraction)
- Lite feature extraction (spiro_features_lite)
- Signal processing and filtering routines (spiro_signal_process)
- Utility functions for volume‐flow conversions and plotting (utilities)

## Installation
You can install Spirolib from PyPI:

```bash
pip install spirolib
```

Or clone the repository and install locally:

```bash
git clone https://github.com/neeldas6789/Spirolib_new.git
cd Spirolib_new
pip install .
```

## Usage
Import the modules you need from the spirolib package:

```python
from spirolib import (
    spiro_signal_process,
    spiro_features_extraction,
    spiro_features_lite,
    spiro_trialsbatch_process,
    spiro_batch_process,
    utilities
)

# Process raw volume-time data
sp = spiro_signal_process(volume_array, time_array)

# Extract detailed spirometry features
features = spiro_features_extraction(sp)

# Or use the lightweight extractor
lite_features = spiro_features_lite(sp)

# Batch process multiple trials
batch = spiro_trialsbatch_process({'trial1': sp, 'trial2': sp2})
best = batch.select_best_trial()

# Populate a DataFrame with raw parameters
df = spiro_batch_process(df_main, {'patient1': sp}, 'pre_').update_raw_parameters()

# Utility conversions and plotting
util = utilities()
flow = util.get_flow_from_vol(volume_array, time_array, scale=1)
```