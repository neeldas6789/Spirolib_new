# -*- coding: utf-8 -*-
"""
This script processes spirometry data into spirolib.spiro_signal_process format
Requires data to be already extracted from raw files
"""
#
#%% Import libraries
import os
cur_dir = os.getcwd()
os.chdir(cur_dir)
import pickle
import sys
sys.path.insert(0, 'C:/Users/u0113548/Google Drive/PhD/Projects/Spiro dev')
import spirolib


#%% Load unprocessed data
FVLData_unpro = pickle.load(open("FVLdata_unprocessed.p", "rb"))
# In this example, the unprocessed data is the best flow-volume trial data for
# each patient ID. The data is stored as a dictionary mapping a patient ID (EMD)
# to a list defined as [Time, Volume, Flow].



#%% Loop through unprocessed data
FVLData_processed = {}
cnt_progress = 0
for patID in FVLData_unpro:
    # Read unprocessed data
    data = FVLData_unpro[patID]
    Time = data[0]
    Volume = data[1]
    Flow = data[2]
    
    # Create a spiro_signal_process object (include scale factor as last argument)
    sp = spirolib.spiro_signal_process(Time, Volume, Flow, patID, "Best", True, 1)
    
    # Correct positioning and standardize units before acceptability check
    sp.correct_data_positioning()
    sp.standerdize_units()
    
    # Check acceptability of the manoeuvre
    flag_accept, reason = sp.check_acceptability_of_spirogram()
    
    # If acceptable, finalize the signal and calculate reference values
    if flag_accept:
        # For example, read these from an external dataset:
        # sex = df.loc[patID,'sex']
        # age = df.loc[patID,'age']
        # height = df.loc[patID,'length']
        sex = 1
        age = 60
        height = 175
        
        sp.finalize_signal(sex, float(age), float(height))
        FVLData_processed[patID] = sp

    cnt_progress += 1
    print("Progress (%) =", round(100 * cnt_progress / len(FVLData_unpro)))

#%% Save processed data
pickle.dump(FVLData_processed, open("FVLdata_processed.p", "wb"))