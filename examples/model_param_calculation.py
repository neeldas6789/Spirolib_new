# -*- coding: utf-8 -*-
"""
This script demonstrates how to calculate parameters of the following models:
1. AreaFE % pred
2. Angle of collapse
3. Deflating balloon parameters
"""

#%% Import Libraries
import os
cur_dir=os.getcwd()
os.chdir(cur_dir)
import pickle

# Import the spirolib library
import sys
sys.path.insert(0,'C:/Users/u0113548/Google Drive/PhD/Projects/Spiro dev')
import spirolib 

#%% Load the spirometry data for all patients. This data must be a dictioary
# mapping patientID to spiro_signal_process objects. 
Best_FVL=pickle.load(open("FVLdata_processed.p","rb"))
#Best_FVL=pickle.load(open("spiro_10_raw.p","rb"))

#%% Loop over the dictionary to calculate the balloon parameters for each patientID
cnt_curves=0
for EMD in Best_FVL:
         # Read the spiro object
         sp=Best_FVL[EMD]
         
         # Read clinical parameters from an external dataset. Here, we assume some random values
         sex = 1 # male
         age = 60 # years
         height = 175 # cm
         race = None # race parameter (e.g., 'Caucasian')
         
         # Extract an FE signal, use a threshold
         FE_time,FE_vol,FE_flow=sp.get_FE_signal(start_type = 'thresh_PEF',  thresh_percent_begin= 1)
         
         #%% AreaFE % predicted
         aFE = spirolib.spiro_features_extraction.areaFE(FE_vol, FE_flow, sex, age, height, race)
         Area_Pred = aFE.calc_AreaPred() # Removed corr parameter
         AreaFE = aFE.calc_areaFE()
         AreaFE_PerPred = 100 *(AreaFE/Area_Pred)
         
         #%% Angle of collapse
         ac = spirolib.spiro_features_extraction.angle_of_collapse(FE_vol, FE_flow)
         AC = ac.calc_AC( plotModel = True, plotProcess = True)
         # Note:Set plot_model and  plotProcess to False, to speed up calculations
         
         #%% Deflating balloon model
         # Note: The 'excitation_type' parameter for run_model is now primarily for internal tracking;
         # only the 'Default' behavior (initial conditions from PEF) is actively modeled.
         db = spirolib.spiro_features_extraction.deflating_baloon(FE_time,FE_vol,FE_flow)
         db.run_model(excitation_type = "", plot_model = True,add_title_text = EMD) 
         # Note:Set plot_model = False to speed up calculations
         
         # To simulate how the FVL varies on changing a parameter of the model (for research purposes)
         # The sim_type parameter for run_simulation is now primarily for internal tracking;
         # only the 'Default' behavior (initial conditions from PEF) is actively modeled.
         #db.run_simulation(sim_param = 'zeta',sim_type="",num_sims=4, percentage_step=10, plot_FVL_only = True)
         
         # Extract model parameters
         wn =  db.wn #coeffient of combined elastic recoil and pleural pressure
         zeta = db.zeta #dimensionless coefficient indicating small airaway resistance
         
         # Get model fit performance 
         R2_vol = db.R2_volume
         R2_flow= db.R2_flow
         mse_vol = db.mse_volume
         mse_flow= db.mse_flow
         
          
        # Update the database
        # Some_update_function(dataset, AreaFE_perpred,wn, zeta ***)
         
         #%% Progress bar
         cnt_curves+=1 
         print("Progress (%) = ", round(100*cnt_curves/len(Best_FVL)))
         
         #break