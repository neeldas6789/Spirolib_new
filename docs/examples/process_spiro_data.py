# -*- coding: utf-8 -*-
"""
This script to processes spirometry data into spirolib.spiro_signal_process format
Requires data to be alread extracted from raw files
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
FVLData_unpro=pickle.load(open("FVLdata_unprocessed.p","rb"))
# In this example, the unprocessed data is the best flow-volume trial data for
# each patient ID. The the data is stored as a dictionary that maps a string called patient ID (also EMD) to
# a list defined as [Time, Volume, Flow]. This data is assuled to have been already extracted


#%% Loop through unprocessed data
FVLData_processed={}
cnt_progress=0
for patID in FVLData_unpro:
    # Read unprocessed data
    data=FVLData_unpro[patID]
    Time=data[0]
    Volume=data[1]
    Flow=data[2]
    
    # Create a spiro signal process object
    # NOTE: added scale_factor argument to match new signature
    # Specify scale to convert time units (e.g., 0.001 for ms to s)
    sp=spirolib.spiro_signal_process(Time,Volume,Flow,patID,"Best",True,1)
    
    #sp.plotFVL(False) # if you want to plot
    
    # if only a single trial is available, the following function is not required.
    # Alternatively, the used can define other functions or performa manual checks
    # to ensure the quality of the spirometry manoeuvers
    # The function can now also reject signals if BEV criteria are not met.
    flag_accept,reason=sp.check_acceptability_of_spirogram() 
    
    # If the quality of the manoeuvre is acceptable, then finalize the signal
    # by also calculating the reference values. The sex, age and height need to be
    # read as input from an external dataset. Here, we use some random values
    if flag_accept:
#        sex=df.loc[patID,'sex'] 
#        age=df.loc[patID,'age']
#        height=df.loc[patID,'length']
        sex = 1
        age = 60
        height = 175
        
        sp.finalize_signal(sex,float(age),float(height))
        FVLData_processed[patID]=sp

    cnt_progress+=1  

    print("Progress (%) = ", round(100*cnt_progress/len(FVLData_unpro)))

#%% Save processed data
pickle.dump(FVLData_processed,open("FVLdata_processed.p","wb"))