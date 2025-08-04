# -*- coding: utf-8 -*-
"""
Classes for batch processing of spirometry data.
"""

import heapq

class spiro_trialsbatch_process:
       # Input to this type is a dictionary called TrialsBatch which is formatted as follows
       # TrialsDict={'TrialNo.1':sp1, 'TrialNo.2':sp2 } where sp1 and and sp2 are objects of type
       # spiro_signal_process. TrialsBatch is a batch of either pre or post trials BUT not  both
       # IMPORTANT: Expects each spirogram object to be finalized
       
    def  __init__(self,TrialsBatch):                     
        self.TrialsBatch=TrialsBatch
    
    def check_between_manoeuvre_criteria(self):
        TrialDict=self.TrialsBatch
        n_trials=len(TrialDict)
        
        if n_trials==1:
            #trialID=list(TrialDict.keys())[0]
            return "Only 1 trial found"
        
        else:
            FEV1_list=[]
            FVC_list=[]
            for trialID in TrialDict:
                #trialID='TrialNo.'+str(i)
                sp=TrialDict[trialID]
                #sp.plotFVL(False)
                FEV1=sp.FEV1
                FVC=sp.FVC
                #sp.plotFVL(False,trialID_i+", FEV1 = "+ str(FEV1)+", FVC = "+str(FVC))
                FEV1_list.append(FEV1)
                FVC_list.append(FVC)
            
            highest_FEV1s=heapq.nlargest(2, FEV1_list)
            highest_FVCs=heapq.nlargest(2, FVC_list)
            
            diff_highest_FEV1s=abs(highest_FEV1s[0]-highest_FEV1s[1])
            diff_highest_FVCs=abs(highest_FVCs[0]-highest_FVCs[1])
            if diff_highest_FEV1s<=0.2 and diff_highest_FVCs<=0.2:
                return True
            else:
                return False

    def select_best_trial(self):
        TrialDict=self.TrialsBatch
        n_trials=len(TrialDict)
        if n_trials==1:
            return list(TrialDict.keys())[0]
        else:
            FVL_sum={}
            for trialID in TrialDict:
                sp=TrialDict[trialID]
                FEV1=sp.FEV1
                FVC=sp.FVC
                FVL_sum[trialID]=FEV1+FVC
            
            best_trialID=max(FVL_sum, key=FVL_sum.get)
            return best_trialID   

class spiro_batch_process:
    # Input is an existing dataframe with patient ids as index, a dictionary BestFVL 
    # that is formatted as {patientID: sp} where patientID and dataframe index are the same 
    def  __init__(self,df_main, BestFVL,pre_post_str):                     
        self.BestFVL=BestFVL
        self.df_main=df_main
        self.pre_post_str=pre_post_str
        #self.add_features=add_features
        
    def update_raw_parameters(self):
        df=self.df_main
        BestFVL=self.BestFVL
        label=self.pre_post_str
        
        # define column names
        FEV1_str=label+"FEV1"+"_raw"
        FVC_str=label+"FVC"+"_raw"
        FEV1_FVC_str=label+"FEV1_FVC"+"_raw"
        PEF_str=label+"PEF"+"_raw"
        FEF25_str=label+"FEF25"+"_raw"
        FEF50_str=label+"FEF50"+"_raw"
        FEF75_str=label+"FEF75"+"_raw"
        FEF25_75_str=label+"FEF25_75"+"_raw"
        
        FEV1_PerPred_str=label+"FEV1_PerPred"+"_raw"
        FVC_PerPred_str=label+"FVC_PerPred"+"_raw"
        FEV1_FVC_PerPred_str=label+"FEV1_FVC_PerPred"+"_raw"
        PEF_PerPred_str=label+"PEF_PerPred"+"_raw"
        FEF25_PerPred_str=label+"FEF25_PerPred"+"_raw"
        FEF50_PerPred_str=label+"FEF50_PerPred"+"_raw"
        FEF75_PerPred_str=label+"FEF75_PerPred"+"_raw"
        FEF25_75_PerPred_str=label+"FEF25_75_PerPred"+"_raw"
        
        
        
        #Initialize columns to null
        df[FVC_str]=""
        df[FEV1_str]=""
        df[FEV1_FVC_str]=""
        df[PEF_str]=""
        df[FEF25_str]=""
        df[FEF50_str]=""
        df[FEF75_str]=""
        df[FEF25_75_str]=""
        
        df[FEV1_PerPred_str]=""
        df[FVC_PerPred_str]=""
        df[FEV1_FVC_PerPred_str]=""
        df[PEF_PerPred_str]=""
        df[FEF25_PerPred_str]=""
        df[FEF50_PerPred_str]=""
        df[FEF75_PerPred_str]=""
        df[FEF25_75_PerPred_str]=""
        
        #
  
        # Update values
        for patID in BestFVL:
            if patID in df.index:
                sp=BestFVL[patID]
                df.loc[patID,FVC_str]=sp.FVC
                df.loc[patID,FEV1_str]=sp.FEV1
                df.loc[patID,FEV1_FVC_str]=sp.Tiff
                df.loc[patID,PEF_str]=sp.PEF
                df.loc[patID,FEF25_str]=sp.FEF25
                df.loc[patID,FEF50_str]=sp.FEF50
                df.loc[patID,FEF75_str]=sp.FEF75
                df.loc[patID,FEF25_75_str]=sp.FEF25_75
                
                df.loc[patID,FVC_PerPred_str]=sp.FVC_PerPred
                df.loc[patID,FEV1_PerPred_str]=sp.FEV1_PerPred
                df.loc[patID,FEV1_FVC_PerPred_str]=sp.Tiff_PerPred
                df.loc[patID,PEF_PerPred_str]=sp.PEF_PerPred
                df.loc[patID,FEF25_PerPred_str]=sp.FEF25_PerPred
                df.loc[patID,FEF50_PerPred_str]=sp.FEF50_PerPred
                df.loc[patID,FEF75_PerPred_str]=sp.FEF75_PerPred
                df.loc[patID,FEF25_75_PerPred_str]=sp.FEF25_75_PerPred
            else:
                print("WARNING: Raw data ID "+patID+" not found in dataset")
            
        
        return df