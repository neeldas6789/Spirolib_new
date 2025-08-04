# -*- coding: utf-8 -*-
"""
This script processes spirometry data into spirolib.spiro_signal_process format
Requires data to be already extracted from raw files
"""

#%% Import libraries
import os
import sys
import pickle

# Ensure the project root is on the import path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')
))

# Import the spirolib library
import spirolib

#%% Load unprocessed data
FVLData_unpro = pickle.load(open("FVLdata_unprocessed.p", "rb"))
# The unprocessed data is assumed as best flow-volume data per patientID,
# stored as dict mapping patientID to [Time, Volume, Flow].

#%% Loop through unprocessed data
FVLData_processed = {}
cnt_progress = 0
for patID in FVLData_unpro:
    data = FVLData_unpro[patID]
    Time, Volume, Flow = data
    
    # Create a spiro signal process object
    sp = spirolib.spiro_signal_process(
        Time, Volume, Flow, patID, "Best", True
    )
    
    # Check signal acceptability
    flag_accept, reason = sp.check_acceptability_of_spirogram()
    
    if flag_accept:
        # Example clinical inputs
        sex = 1
        age = 60
        height = 175
        
        sp.finalize_signal(sex, float(age), float(height))
        FVLData_processed[patID] = sp

    cnt_progress += 1
    print("Progress (%) =", round(100 * cnt_progress / len(FVLData_unpro)))

#%% Save processed data
pickle.dump(FVLData_processed, open("FVLdata_processed.p", "wb"))