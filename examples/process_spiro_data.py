# -*- coding: utf-8 -*-
"""
This script processes spirometry data into spirolib.spiro_signal_process format.
Requires data to be already extracted from raw files.
"""

#%% Import libraries
import os
cur_dir = os.getcwd()
# Ensure current directory is on path
import sys
# sys.path.insert(0, 'C:/Users/u0113548/Google Drive/PhD/Projects/Spiro dev')
import pickle
import spirolib

#%% Load unprocessed data
FVLData_unpro = pickle.load(open("FVLdata_unprocessed.p", "rb"))

#%% Loop through unprocessed data
FVLData_processed = {}
cnt_progress = 0
for patID, data in FVLData_unpro.items():
    Time, Volume, Flow = data

    # Create a spiro signal process object
    # scale1 parameter applies to time units (e.g., 1 for seconds)
    sp = spirolib.spiro_signal_process(Time, Volume, Flow, patID, "Best", True, scale1=1)

    # Optional: visualize raw FVL
    # sp.plotFVL(False)

    # Check spirogram acceptability (includes BEV criteria)
    flag_accept, reason = sp.check_acceptability_of_spirogram()
    if flag_accept:
        # Clinical metadata (example values)
        sex = 1
        age = 60
        height = 175
        sp.finalize_signal(sex, float(age), float(height))
        FVLData_processed[patID] = sp

    cnt_progress += 1
    print("Progress (%) =", round(100 * cnt_progress / len(FVLData_unpro)))

#%% Save processed data
pickle.dump(FVLData_processed, open("FVLdata_processed.p", "wb"))
