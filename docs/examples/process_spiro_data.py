# -*- coding: utf-8 -*-
"""
This script processes spirometry data into spirolib.spiro_signal_process format
Requires data to be already extracted from raw files
"""
#
#%% Import libraries
import os
cur_dir=os.getcwd()
os.chdir(cur_dir)
import pickle
import sys
sys.path.insert(0,'C:/Users/u0113548/Google Drive/PhD/Projects/Spiro dev')
import spirolib 


#%% Load unprocessed data
FVLData_unpro = pickle.load(open("FVLdata_unprocessed.p","rb"))
# In this example, the unprocessed data is the best flow-volume trial data for
# each patient ID. The data is stored as a dictionary that maps a string called patient ID (also EMD)
# to a list defined as [Time, Volume, Flow]. This data is assumed to have been already extracted


#%% Loop through unprocessed data
FVLData_processed = {}
cnt_progress = 0
for patID in FVLData_unpro:
    # Read unprocessed data
    data = FVLData_unpro[patID]
    Time, Volume, Flow = data[0], data[1], data[2]
    
    # Create a spiro signal process object
    sp = spirolib.spiro_signal_process(Time, Volume, Flow, patID, "Best", True)
    
    # If the signal needs orientation and unit conversion
    sp.correct_data_positioning()
    sp.standerdize_units()
    
    # If only a single trial is available, the following function is not required.
    # Alternatively, the user can define custom checks to ensure manoeuvre quality.
    # The function can now also reject signals if BEV criteria are not met.
    flag_accept, reason = sp.check_acceptability_of_spirogram()
    
    # If the quality of the manoeuvre is acceptable, finalize the signal
    # by calculating reference values. Sex, age, and height must be provided.
    if flag_accept:
        # sex = df.loc[patID,'sex']
        # age = df.loc[patID,'age']
        # height = df.loc[patID,'length']
        sex = 1
        age = 60
        height = 175
        
        sp.finalize_signal(sex, float(age), float(height))
        FVLData_processed[patID] = sp

    cnt_progress += 1  
    print("Progress (%) =", round(100*cnt_progress/len(FVLData_unpro)))

#%% Save processed data
pickle.dump(FVLData_processed, open("FVLdata_processed.p","wb"))