# -*- coding: utf-8 -*-
"""
This script demonstrates how to calculate parameters of the following models:
1. AreaFE % pred
2. Angle of collapse
3. Deflating balloon parameters
"""

#%% Import Libraries
import os
cur_dir = os.getcwd()
# Ensure current directory is on path
import sys
# If spirolib is installed, no need for custom path
# sys.path.insert(0, 'C:/Users/u0113548/Google Drive/PhD/Projects/Spiro dev')
import spirolib

#%% Load the spirometry data for all patients. This data must be a dictionary
# mapping patientID to spiro_signal_process objects.
import pickle
Best_FVL = pickle.load(open("FVLdata_processed.p", "rb"))

#%% Loop over the dictionary to calculate the balloon parameters for each patientID
cnt_curves = 0
for EMD, sp in Best_FVL.items():
    # Clinical parameters (example values)
    sex = 1      # male
    age = 60     # years
    height = 175 # cm
    race = None  # race identifier or None if unknown

    # Extract FE signal using threshold start
    FE_time, FE_vol, FE_flow = sp.get_FE_signal(start_type='thresh_PEF', thresh_percent_begin=1)

    #%% AreaFE % predicted
    aFE = spirolib.spiro_features_extraction.areaFE(FE_vol, FE_flow, sex, age, height, race)
    Area_Pred = aFE.calc_AreaPred()
    AreaFE = aFE.calc_areaFE()
    AreaFE_PerPred = 100 * (AreaFE / Area_Pred)

    #%% Angle of collapse
    ac = spirolib.spiro_features_extraction.angle_of_collapse(FE_vol, FE_flow)
    AC, cost = ac.calc_AC(plotModel=True, plotProcess=True)

    #%% Deflating balloon model
    db = spirolib.spiro_features_extraction.deflating_baloon(FE_time, FE_vol, FE_flow)
    db.run_model(excitation_type="", plot_model=True, add_title_text=EMD)

    # To simulate sensitivity (default behavior uses PEF initial conditions)
    # db.run_simulation(sim_param='zeta', num_sims=4, percentage_step=10, plot_FVL_only=True)

    # Extract final model parameters
    wn = db.wn
    zeta = db.zeta
    R2_vol, R2_flow = db.R2_volume, db.R2_flow
    mse_vol, mse_flow = db.mse_volume, db.mse_flow

    # Update external database with results...

    cnt_curves += 1
    print("Progress (%) =", round(100 * cnt_curves / len(Best_FVL)))
