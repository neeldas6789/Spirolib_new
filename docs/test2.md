## Spirolib
A Python library for processing and analyzing spirometry data.

## Features
- Signal processing: spiro_signal_process (flow/volume filtering, smoothing, etc.)
- Feature extraction: spiro_features_extraction (detailed) and spiro_features_lite (lightweight)
- Batch processing: spiro_trialsbatch_process and spiro_batch_process for multi-trial and multi-patient workflows
- Utilities: volume↔flow conversion, uniform sampling, noise addition, grayscale rendering (utilities)

## Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/neeldas6789/Spirolib_new.git
cd Spirolib_new
pip install -r requirements.txt    # if available
pip install .
```

## Usage
```python
from spirolib import (
    spiro_signal_process,
    spiro_features_extraction,
    spiro_features_lite,
    spiro_trialsbatch_process,
    spiro_batch_process,
    utilities,
)

# 1. Signal processing
sp = spiro_signal_process(raw_data_array)
# 2. Feature extraction
features_full = spiro_features_extraction(sp)
features_lite = spiro_features_lite(sp)

# 3. Single‐trial batch processing
batch = {'Trial1': sp, 'Trial2': sp}
tb = spiro_trialsbatch_process(batch)
best_trial_id = tb.select_best_trial()
valid = tb.check_between_manoeuvre_criteria()

# 4. Multi‐patient batch processing
df = ...  # pandas DataFrame indexed by patient IDs
best_fvls = {'patient1': sp, 'patient2': sp}
bp = spiro_batch_process(df, best_fvls, 'pre')
df_updated = bp.update_raw_parameters()

# 5. Utilities example
util = utilities()
flow = util.get_flow_from_vol(volume, time, scale)
vol  = util.get_vol_from_flow(flow, time, scale)
t_resampled, vol_resampled, flow_resampled = util.sample_FVL_data(time, vol=volume, flow=flow)
noise_vol, noise_flow = util.add_noise_to_FVLdata(sp, mode=1)
gray_img = util.convert2grayscale(x, y, mode='FVL', size=32)
```