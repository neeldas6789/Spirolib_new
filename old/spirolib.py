# -*- coding: utf-8 -*-
"""
A library to perform various operations on spirometry data

"""

import peakutils
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize, differential_evolution
import heapq
from scipy.signal import butter, lfilter


# Important: consistently followed: index0= start of FI, index1 =start of FE, index2=end of FE

class spiro_signal_process:
    def __init__(self,time,volume,flow,patientID,trialID, flag_given_signal_is_FE):
        '''
        Class initialization
        Requires: 
        1. time: time of spirometry manoeuvre (type: list or 1D array, units: prefarably in s)
        2. volume: volume of manoeuvre (type: list or 1D array, preferably in litres)
        3. flow: air-flow of manoeuvre (type: list or 1D array, preferably in litres/s)
        4. patientID: unique patient ID (type: a string or number)
        5. trialID : trial no of the manoeuvre (type: a string or number, if only one or best trial is available then 'Best')
        6. flag_given_signal_is_FE : whether the given signal is forced expiration only (type: Boolean-True/False, to be determined by user)
        Note: The flow-volume data should be prefarably arranged such that the expiratory flow-volume loop is right skewed and PEF is positive
        '''
        self.time=np.array(time)
        self.volume=np.array(volume)
        self.flow=np.array(flow)
        
        if (len(self.time)!=len(self.volume)):
           raise Exception('Length of time and volume vectors do not match')
        elif (len(self.volume)!=len(self.flow)):
           raise Exception('Length of volume and flow vectors do not match')
        
        self.patientID=str(patientID)
        self.trialID=str(trialID)
        self.flag_given_signal_is_FE=flag_given_signal_is_FE
        self.signal_finalized=False
        self.index1 = None 
        self.index2 = None 

        
    def correct_data_positioning(self,flip_vol=False,flip_flow=False):
        '''
        This function converts positions the data so that expiratory FVL is right skewed and PEF is positive
        Input: 1D np arrays for volume, flow and time with STANDERDIZED UNITS
               flip_vol: True if volume signal be reversed (should be decided after plotting the raw data)
               flip_flow: True if flow signal be reversed (should be decided after plotting the raw data)
        '''
        if flip_vol:
            self.volume=-self.volume
        if flip_flow:
            self.flow=-self.flow
        
    def standerdize_units(self):
        ''' This function converts all units to litres and seconds'''
        self.volume=self.volume/1000
        self.flow=self.flow/1000
        self.time=self.time/1000
        
    def plotFVL(self,only_FVL = False, show_ID = True ,add_text="", only_FE=False, color = 'black', dpi = 100, figsize = None, grid_on = True):
        '''
        This function plots the flow volume loop
        Inputs: 
        1. only_FVL: A boolean indicating whether the forced expirataory flow-volume loop needs to be plotted
        2. show_ID: A boolean indicating patient ID needs to be displayed in the title string
        3. add_text: String to be displayed as title
        4. only_FE: A boolean indicating if only the forced expiratory manoeuvre needs to be displayed
        ......
        '''
        if show_ID:
            if add_text=="":
                title_str=self.patientID+'-'+ self.trialID
            else:
                title_str=self.patientID+'-'+ self.trialID+", "+add_text
        else: 
            if add_text!="":
                title_str =""
            else:
                title_str=self.patientID+'-'+ self.trialID+", "+add_text
            
        volume=self.volume
        flow=self.flow
        time=self.time
        
        if figsize is None:
            if only_FVL:
                figsize = (5,4)
            else:
                figsize = (18,4)
        
        if only_FE==True:
            if hasattr(self, 'index1'):
                index1=self.index1
                index2=self.index2
                volume=self.volume[index1:index2]
                flow=self.flow[index1:index2]
                time=self.time[index1:index2]
            else:
                index1,index2=self.get_FE_start_end()
                volume=self.volume[index1:index2]
                flow=self.flow[index1:index2]
                time=self.time[index1:index2]
         
        if only_FVL:
            plt.figure(figsize=figsize, dpi= dpi, facecolor='w', edgecolor='k')
            plt.title(title_str,fontsize=12,fontweight='bold')
            plt.plot(volume,flow,color=color,linewidth=1.5)
            plt.xlabel('Volume',weight='normal')
            plt.ylabel('Flow',weight='normal')
            if grid_on:
                plt.grid(True,which='both')
        else:
            plt.figure(figsize=figsize, dpi= dpi, facecolor='w', edgecolor='k')
            plt.suptitle(title_str,fontsize=12, fontweight='bold')
            
            plt.subplot(1,3,1)
            plt.plot(volume,flow,color=color)
            plt.xlabel('Volume (L)')
            plt.ylabel('Flow (L/s)')
            if grid_on:
                plt.grid(True,which='both')
            
            
            plt.subplot(1,3,2)
            plt.plot(time,volume,color=color)
            plt.xlabel('Time (s)')
            plt.ylabel('Volume (L)')
            if grid_on:
                plt.grid(True,which='both')
            
            plt.subplot(1,3,3)
            plt.plot(time,flow,color=color)
            plt.xlabel('Time (s)')
            plt.ylabel('Flow (L/s)')
            if grid_on:
                plt.grid(True,which='both')
        
        #plt.close(plt.Figure)
        
    def get_Indexes_In_1s(self, start_index=0):
        time=self.time[start_index:]
        time=time-time[0]
        new_list = list(time-1)
        indexes_1s = next(t[0] for t in enumerate(new_list) if t[1] > 0)
        return indexes_1s - 1
    
    def get_PEF_index(self, indx1,indx2):
        flow=self.flow
        PEF_index=indx1+np.argmax(flow[indx1:indx2+1])
        
        #plt.plot(self.volume[PEF_index:],flow[PEF_index:])
        return PEF_index
    
    def butter_lowpass(self,cutoff, fs, order):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(self,data, cutoff, fs, order):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y
    
    
    def backExtrapolate_FEstart(self):
        # This function  curates the beginning of FE
        # using back extrapolation from steepest peak
        
        if self.flag_given_signal_is_FE:
                index1 = 0
                index2 = len(self.time) - 1
        else:
            index1 = self.temp_index1
            index2 = self.temp_index2
        
        
        # Unpack FE flow volume time
        flow=self.flow[index1:index2+1]
        vol= self.volume[index1:index2+1]
        vol = vol - vol[0]
        time=self.time[index1:index2+1]
        time= time - time[0]
        
        
        PEF_Index= np.argmax(flow)
        t_PEF = time[PEF_Index]
        vol_PEF = vol[PEF_Index]
        m = flow[PEF_Index]
        
        # extrapolated start time 
        t_ep=t_PEF - vol_PEF/m 
        
        
        # to get index corresponding to t_ep 
        temp_index=0
        if t_ep>=0:
            while temp_index<len(time)-1:
                if t_ep>= time[temp_index] and t_ep<time[temp_index+1]:
                    new_index1 = temp_index
                    break
                else:
                    temp_index=temp_index+1
                    
            FVC = abs(vol[-1] - vol[0])
            BEV = vol[new_index1]
            
            thresh_vol= np.maximum(0.05*FVC,0.15)
            
            if BEV <= thresh_vol:
                BEV_criteria = True
            else:
                BEV_criteria = False
        else:
            new_index1=0
            BEV_criteria = True
            
        # return whether BEV criteria is satisfied    
            
        return new_index1 + index1 , BEV_criteria
        
        
    def threshPEF_FEstart(self,thresh_percent_begin):
        #This function  curates the beginning of FE
        # using a threshold percentage of PEF
        if self.flag_given_signal_is_FE:
            index1 = 0
            index2 = len(self.time) - 1
        else:
            index1 = self.temp_index1
            index2 = self.temp_index2
        
        flow=self.flow
        PEF_Index= self.get_PEF_index(index1,index2)
        PEF=flow[PEF_Index]
        flow_excit=flow[index1:PEF_Index+1]
        
        threshold=(thresh_percent_begin/100)*PEF #Any flow below this is zero, thresh_percent of PEF
        
        temp_index1=int(len(flow_excit)-1)
        
        while flow_excit[temp_index1]>threshold and temp_index1>0:#index1:
            temp_index1=temp_index1-1
        
        index1=index1+temp_index1+1
        
        return index1
    
    
    def trim_FE_end(self, thresh_percent_end):
        #This function  curates the ending of FE
        # using a threshold percentage of PEF
        if self.flag_given_signal_is_FE:
            index1 = 0
            index2 = len(self.time) - 1
        else:
            index1 = self.temp_index1
            index2 = self.temp_index2
            
        flow=self.flow
        PEF_Index= self.get_PEF_index(index1,index2)
        PEF=flow[PEF_Index]
        threshold=(thresh_percent_end/100)* PEF

        temp_index2=index2
        while (temp_index2>index1) and (flow[temp_index2]<=threshold):
            temp_index2 = temp_index2 - 1
        
        return temp_index2
    
    def get_FE_start_end(self, start_type=None, thresh_percent_begin = 2, thresh_percent_end =0.5 ,check_BEV_criteria = False):
        #indx1 is start of FE (updated with Backextrapolated start)
        #indx2 is end of FE or point of RV
        #IMPORTANT: Assumes data is positioned and standerdized
        # default start type of FE is BEV
        
        if self.flag_given_signal_is_FE:
            if start_type is None:
                index1=0
            elif start_type=="BEV": 
                index1, BEV_criteria =self.backExtrapolate_FEstart()
                if check_BEV_criteria :
                    if not BEV_criteria:
                        index1 = -1
                else:
                    if not BEV_criteria:
                        print("WARNING: BEV criteria not met")
                
            elif start_type=="thresh_PEF" :
                index1 = self.threshPEF_FEstart(thresh_percent_begin=thresh_percent_begin)
            
            index2=self.trim_FE_end(thresh_percent_end=thresh_percent_end)
            
            return index1, index2
        else:
            volume=self.volume
            indx_1s=self.get_Indexes_In_1s()
            
            indx1=np.argmin(volume) 
            VolVec_aft_TLC=volume[indx1+1:] #Volume vector from TLC to end
            VolVec_bef_TLC=volume[0:indx1+1] #Volume vector from start to TLC 
            
            if len(VolVec_aft_TLC)==0:
                VolVec_aft_TLC=np.append(VolVec_aft_TLC, volume[indx1])# add a virtual point to negate empty arrays
            
            #Add this 0 padding so that peak utils dont get stuck
            VolVec_aft_TLC[-1]=VolVec_aft_TLC[-1]+0.0001 
            
            #plt.plot(self.time[indx1+1:],VolVec_aft_TLC,linewidth=5,label="pre filter")
            
    
            
            #get peaks before and after TLC
            thresh=0.85
            #thresh_dist=0.1*(max(VolVec_aft_TLC)-min(VolVec_aft_TLC))
            
            peaks_aft_TLC = peakutils.indexes(VolVec_aft_TLC, thres=thresh, min_dist=int(5*indx_1s))  
            peaks_bef_TLC = peakutils.indexes(VolVec_bef_TLC, thres=thresh, min_dist=2*indx_1s)
            
            #VolVec_aft_TLC=orig_VolVec_aft_TLC
            if len(peaks_aft_TLC)!=0: 
                height_aft_TLC=np.abs(VolVec_aft_TLC[peaks_aft_TLC[0]]-VolVec_aft_TLC[0]) 
            else:
                height_aft_TLC=np.abs(VolVec_aft_TLC[-1]-VolVec_aft_TLC[0])  
            
            if len(peaks_bef_TLC)!=0:
                height_bef_TLC=np.abs(VolVec_bef_TLC[peaks_bef_TLC[-1]]-VolVec_bef_TLC[-1])
            else:
                height_bef_TLC=np.abs(VolVec_bef_TLC[-1]-VolVec_bef_TLC[0])  
            
            #logic: peak height after TLC should be the maximum otherwise wrong TLC index chosen
            if height_aft_TLC<height_bef_TLC: 
               indx1=np.argmin(volume[0:indx1-2*indx_1s])
               VolVec_aft_TLC=volume[indx1+1:]
            
            indx2=indx1+np.argmax(VolVec_aft_TLC) 
            
            self.temp_index1 = indx1
            self.temp_index2 = indx2
            if (start_type is None) or (start_type=="BEV"): 
                new_index1, BEV_criteria =self.backExtrapolate_FEstart()
                if check_BEV_criteria:
                    if BEV_criteria == False:
                        new_index1 = -1                
            else:
                new_index1 = self.threshPEF_FEstart(thresh_percent_begin=thresh_percent_begin)
            
            
            new_index2=self.trim_FE_end(thresh_percent_end=thresh_percent_end)
            
            return new_index1, new_index2
    

    
    def calc_FEV1_FVC(self):
        FE_Vol=self.volume[self.index1:self.index2+1]
        FE_Vol=FE_Vol-FE_Vol[0]
        FE_time=self.time[self.index1:self.index2+1]
        FE_time=FE_time-FE_time[0]
                
        #plt.plot(FEtime,FE_Vol)    
        t0=FE_time[0]
        index_1s=self.get_Indexes_In_1s(start_index=self.index1)
        FEV1=np.interp(t0+1, [FE_time[index_1s],FE_time[index_1s+1]], [FE_Vol[index_1s],FE_Vol[index_1s+1]])       

        FVC=abs(FE_Vol[-1]-FE_Vol[0])
        return round(FEV1,2), round(FVC,2)
    
    
    def calc_flow_parameters(self):
        # Only possible when index1 and index2 are determined
         if self.flag_given_signal_is_FE:
             FEvol=self.volume
             FEflow=self.flow
             FEtime=self.time
         else:
            FEvol=self.volume[self.index1:self.index2+1]
            FEflow=self.flow[self.index1:self.index2+1]
            FEtime=self.time[self.index1:self.index2+1]
             
         norm_c=FEvol[-1] # or FVC
         FEvol_norm=FEvol/norm_c
         PEFindx=np.argmax(FEflow)
         PEF=FEflow[PEFindx]
         indx=0
                #print(indx)
         while FEvol_norm[indx]<=1:
            if FEvol_norm[indx+1]>=0.25 and FEvol_norm[indx]<0.25:
                FEF25=np.interp(0.25,[FEvol_norm[indx],FEvol_norm[indx+1]],[FEflow[indx],FEflow[indx+1]])
                time25=np.interp(0.25,[FEvol_norm[indx],FEvol_norm[indx+1]],[FEtime[indx],FEtime[indx+1]])
                        
            if FEvol_norm[indx+1]>=0.5 and FEvol_norm[indx]<0.5:
                FEF50=np.interp(0.5,[FEvol_norm[indx],FEvol_norm[indx+1]],[FEflow[indx],FEflow[indx+1]])
                    
            if FEvol_norm[indx+1]>=0.75 and FEvol_norm[indx]<0.75:
                FEF75=np.interp(0.75,[FEvol_norm[indx],FEvol_norm[indx+1]],[FEflow[indx],FEflow[indx+1]])
                time75=np.interp(0.75,[FEvol_norm[indx],FEvol_norm[indx+1]],[FEtime[indx],FEtime[indx+1]])
                break
            indx+=1
            
         FEF_25_75=(0.5*norm_c)/(time75-time25)
         return round(PEF,2), round(FEF25,2), round(FEF50,2), round(FEF75,2), round(FEF_25_75,2)
        
         
     
    def get_FI_start(self, index1=None):
        if index1 is None:
            index1=self.index1
        
        vol_before_FE=self.volume[0:index1]
        #time_befor_FE=self.time[0:index1]
        #plt.plot(time_befor_FE,vol_before_FE)
        
        if len(vol_before_FE)==0:
            return -1
        
        indx_1s=self.get_Indexes_In_1s()
        thresh=0.3
        peaks=peakutils.indexes(vol_before_FE, thres=thresh, min_dist=int(indx_1s))
        #plt.plot(self.time[0:index1],vol_before_FE)
        if len(peaks)!=0:
            index0=peaks[-1]
            return index0
        else:
            return -1
    
    def check_rise_to_PEF(self):
        PEF_index = np.argmax(self.flow)
        if PEF_index == 0:
            return False
        else:
            return True
    
    def check_largest_time_interval(self,max_time_interval = 1, FE_time_duration = 4):
        # check largest time interval within the first 6s
        time_diff = np.ediff1d(self.time)
        index_6s = np.argwhere(self.time>FE_time_duration)
        
        if len(index_6s)>0:
            index_6s=index_6s[0,0]
            time_diff = time_diff[:index_6s]
        
        if len(np.argwhere(time_diff>max_time_interval))>0:
            return False
        else:
            return True
        
    def check_acceptability_of_spirogram(self , min_FE_time = 6, thresh_percent_end =0.5 ):
        ## This function checks the acceptability of spirogram
        ## IMPORTANT:This function runs properly only after correct_data_positioning()
        ## and standerdize_units() is executed
        time=self.time
        
        
        indexes_1s=self.get_Indexes_In_1s(start_index = 0)
        
        if indexes_1s==-1:
            return False, 'Rejected: Manoevre not perfomed'
        
      
        if not self.check_rise_to_PEF():
            return False, 'Rejected: Rise to PEF not found'
        
        index1,index2=self.get_FE_start_end(start_type="BEV",thresh_percent_end =thresh_percent_end, check_BEV_criteria=True)
        if index1 == -1:
            return False, "Rejected: BEV criteia not met"
            
        if not self.flag_given_signal_is_FE:
            index0=self.get_FI_start(index1)
            if index0==-1:
                    return False, 'Rejected: Incorrect foreced inspiration'
        
        
        if index1>index2: ##RV is reached before forced expiration is performed
            return False, 'Rejected:Bad manoevre, could not detect FE'
        
        #artefacts_found=self.check_artefacts_in_FE(index1, index2,indexes_1s)
        
#        if artefacts_found:
#            return False, 'Rejected:Artefacts found during FE'
        
        if (self.flag_given_signal_is_FE==False) and (index1<=indexes_1s): ## point of max inhalation or TLC is at the beginning;bad start
            return False, 'Rejected:Manoevre starts at TLC'
        
        if index2<=indexes_1s: ## RV is just at the beginning ; bad start
            return False, 'Rejected:Manoevre starts with RV'
        

        
        time_FE=time[index2]-time[index1]
        if  time_FE<min_FE_time: # Force exhalation time is very low 
            return False, 'Rejected:Time of forced expiration is less than '+str(min_FE_time)+'s'
        elif time_FE>50:
            return False, 'Rejected:Time of forced expiration is more than 50s!'
        
        # Spirogram is accepted, finalize the indexes
        self.index1=index1 # index1 is saved based on BEV criteria
        self.index2=index2
        return True, 'Accepted'
    
    def shift_TLC_to_orgin(self):
        volume=self.volume
        if self.index1 is not None:
            volume=volume-volume[self.index1]
        else:
            print("Error: FE indexes not yet calculated. Indexes are computed only after acceptability checking")
        self.volume=volume
    
    def smooth_FVL_start(self,time,vol,flow):
        # This function smoothens the beginning of FE FVL
        time=time
        vol=vol
        flow=flow
            #sp.plotFVL(False)
        PEF_Index=np.argmax(flow)
        flow_excit=flow[0:PEF_Index+1]
        vol_excit=vol[0:PEF_Index+1]
        forward_diff=np.diff(flow_excit)
            
        neg_diff_indices=np.argwhere(forward_diff<0)
        
        if neg_diff_indices.size>0:
            index_bad_start=neg_diff_indices[neg_diff_indices.size-1,0]
            good_excite_flow=flow_excit[index_bad_start:]
            good_excite_vol=vol_excit[index_bad_start:]
            
            
            #bad_excite_flow=flow_excit[0:index_bad_start]
            bad_excite_vol=vol_excit[0:index_bad_start]
                
            poly_coeffs=np.polyfit(good_excite_vol, good_excite_flow, 3)
            poly=np.poly1d(poly_coeffs)
                
            smoothed_bad_excite_flow=poly(bad_excite_vol)
            index_neg_interp=np.argwhere(smoothed_bad_excite_flow<0)
            
            if index_neg_interp.size>0:
                index1=index_neg_interp[index_neg_interp.size-1,0]+1
            else:
                index1=0
                
                
            smoothed_flow=np.append(smoothed_bad_excite_flow[index1:index_bad_start],flow[index_bad_start:])
            smoothed_time=time[index1:]
            smoothed_time=smoothed_time-smoothed_time[0]
                
            f_diff_t=np.diff(smoothed_time)
            vol_discrete=f_diff_t*smoothed_flow[1:]
            smoothed_vol=np.cumsum(vol_discrete)
            smoothed_vol=np.append(0,smoothed_vol)
            return smoothed_time,smoothed_vol,smoothed_flow
        else:
            return time,vol,flow
    
    def manual_trim(self, begin_time=0, end_time = None):
        # Function to trim sp signal based on provided begin and end times
        if begin_time==0:
            index1 = 0
        else:
            index1 = np.argwhere(self.time>=begin_time)
            index1 = index1[0,0]
        
        if end_time is None:
            index2 = len(self.time)
        else:
            index2 = np.argwhere(self.time>=end_time)
            index2 = index2[0,0]
        
        if (index1==0) and (index2 < len(self.time)): # Trimming at end
            time = self.time[0:index2]
            time= np.append(time, time[-1] + (time[-1]-time[-2]))
            flow = np.append(self.flow[0: index2],0)
            volume = self.volume[0: index2]
            volume = np.append(volume, volume[-1])
        
        elif (index1>0) and (index2 == len(self.time)): # Trimming at begin
            time = self.time[index1:index2]
            time = np.append(time[0] -(time[1]-time[0]),time)
            time = time - time[0]
            flow = np.append(0,self.flow[index1 : index2])
            volume = np.append(0,self.volume[index1 : index2])
        
        elif (index1>0) and (index2 <len(self.time)): # Trimming at both ends
            time = self.time[index1:index2]
            time = np.append(time, time[-1] + (time[-1]-time[-2]))
            time = np.append(time[0] -(time[1]-time[0]),time)
            time = time - time[0]
            flow = np.append(0,self.flow[index1 : index2])
            flow = np.append(flow, 0)
            volume = np.append(0,self.volume[index1 : index2])
            volume = np.append(volume, volume[-1])
        
        else:
            time = self.time
            volume = self.volume
            flow = self.volume
        
        return time, volume, flow
                 
    def get_FE_signal(self, start_type=None, thresh_percent_begin = 2, thresh_percent_end =0.25, plot=False):
        '''
        This function extracts an the time, volume and flow corresponding to the forced expiratory (FE manoeuvre
        Inputs:
        1. spiro_signal_process object (class function)
        2. start_type: 'BEV' (starting point of  FE is chosen according to BEV criteria, used for calculating FEV1 and FVC)  or
                       'thresh_PEF'(starting point of  FE is chosen based on a percentage threshold of PEF, useful for modeling)
        3. thresh_percent_begin: A percentage threshold of PEF to be define the beginning of FE, ignored when start_type is 'None' or 'BEV'
        4. thresh_percent_end: A percentage threshold of PEF to define the end of FE
        5. plot: Boolean indicating whether the FE signal needs to be plotted
        # Output
        1D arrays of time, volume and flow corresponding to the FE manoeuvre. If t0 indicates beginning of forced 
        expiration, t1 is the time for PEF and tn indicates the end, then the signals are organized as
        t0 = 0 s, volume(t0) = 0 and volume(tn)=FVC, flow(t0)=0, flow(t1)=PEF and flow(tn)->0 (may not be 0)
        '''
    #Function to extract FE signal 
    # Does not depend on self.index1 and self.index2
        if self.flag_given_signal_is_FE:
            if start_type is None:
                index1=0
                index2=len(self.time) - 1
            elif start_type == "BEV":
                index1, index2 = self.get_FE_start_end(start_type = "BEV", thresh_percent_end = thresh_percent_end)
            elif start_type == "thresh_PEF":
                index1, index2 = self.get_FE_start_end(start_type='thresh_PEF', thresh_percent_begin= thresh_percent_begin, thresh_percent_end = thresh_percent_end)
        else:
            if (start_type is None) or (start_type=="BEV"): # default index1 is BEV start
                index1, index2 = self.get_FE_start_end(start_type = "BEV", thresh_percent_end = thresh_percent_end)
            
            elif start_type == "thresh_PEF"  : # start of FE is decided based on threshold value of PEF
                index1, index2 = self.get_FE_start_end(start_type='thresh_PEF',thresh_percent_begin= thresh_percent_begin, thresh_percent_end = thresh_percent_end)   
               
        # Slice the FE signal
        FE_time=self.time[index1:index2+1]
        FE_time=FE_time-FE_time[0]
        FE_vol= self.volume[index1:index2+1]
        FE_vol=FE_vol-FE_vol[0]
        FE_flow=self.flow[index1:index2+1]
                
        # appned 0 Flow at begining and end of FE
        if start_type == "BEV" or start_type == "thresh_PEF":
            FE_flow = np.append(0,FE_flow)
            FE_flow = np.append(FE_flow, 0)
            FE_time = np.append(FE_time[0] - (FE_time[1]-FE_time[0]),FE_time)
            FE_time = np.append(FE_time, FE_time[-1]  + (FE_time[-1] - FE_time[-2]))
            FE_time = FE_time - FE_time[0]
            FE_vol = np.append(0,FE_vol)
            FE_vol = np.append(FE_vol, FE_vol[-1])
            
        if plot:
            plt.figure(figsize=(16,4), dpi= 100, facecolor='w', edgecolor='k')
            plt.suptitle(self.patientID,fontsize=12, fontweight='bold')
                
            plt.subplot(1,3,1)
            plt.plot(FE_vol,FE_flow,color='black')
            plt.grid(True,which='both')
            plt.xlabel('Volume')
            plt.ylabel('Flow')
                
            plt.subplot(1,3,2)
            plt.plot(FE_time,FE_vol,color='black')
            plt.grid(True,which='both')
            plt.xlabel('Time')
            plt.ylabel('Volume')
                
            plt.subplot(1,3,3)
            plt.plot(FE_time,FE_flow,color='black')
            plt.grid(True,which='both')
            plt.xlabel('Time')
            plt.ylabel('Flow')

        return FE_time,FE_vol,FE_flow

    
    def calc_ECCS93_ref(self,param):
       sex=self.Sex #1-male  or 0-female
       age=self.Age # years
       height=self.Height # cms
        
       #calculate reference values
       if sex==1: #Male
            if param=="FVC":
                FVC_Pred=5.76*height/100-0.026*age-4.34
                return FVC_Pred
            elif param=="FEV1":
                FEV1_Pred=4.3*height/100-0.029*age-2.49
                return FEV1_Pred
            elif param=="Tiff":
                Tiff_pred=-0.18*age+87.21
                return Tiff_pred
            elif param=="PEF":
                PEF_Pred=6.14*height/100-0.043*age+0.15
                return PEF_Pred
            elif param=="FEF75":
                FEF75_Pred=0.0261*height-0.026*age-1.34
                return FEF75_Pred
            elif param=="FEF50":
                FEF50_Pred=0.0379*height-0.031*age-0.35
                return FEF50_Pred
            elif param=="FEF25":
                FEF25_Pred=5.46*height/100-0.029*age-0.47
                return FEF25_Pred
            elif param=="FEF25_75":
                FEF_25_75_Pred=1.94*height/100-0.043*age+2.7
                return FEF_25_75_Pred
            elif param=="MIF50":
                MIF50_Pred=(height-100)*0.8/30
                return MIF50_Pred
            elif param=="IC":
                IC_Pred=6.1*height/100 - 0.028*age -4.65
                return IC_Pred
           
       else: #Female
            if param=="FVC":    
                FVC_Pred=4.43*height/100-0.026*age-2.89
                return FVC_Pred
            elif param=="FEV1":
                FEV1_Pred=3.95*height/100-0.025*age-2.6
                return FEV1_Pred
            elif param=="Tiff":
                Tiff_pred=-0.19*age+89.1
                return Tiff_pred
            elif param=="PEF":
                PEF_Pred=5.5*height/100-0.03*age-1.11
                return PEF_Pred
            elif param=="FEF75":
                FEF75_Pred=0.0105*height-0.025*age+1.11
                return FEF75_Pred
            elif param=="FEF50": 
                FEF50_Pred=2.45*height/100-0.025*age+1.16
                return FEF50_Pred
            elif param=="FEF25":
                FEF25_Pred=3.22*height/100-0.025*age+1.6
                return FEF25_Pred
            elif param=="FEF25_75":
                FEF_25_75_Pred=1.25*height/100-0.034*age+2.92
                return FEF_25_75_Pred
            elif param=="MIF50":
                MIF50_Pred=(height-100)*0.8/30
                return MIF50_Pred
            elif param=="IC":
                IC_Pred=4.66*height/100 - 0.024*age -3.28
                return IC_Pred
    
     
    def finalize_signal(self,sex=None,age=None,height=None):
        '''
        This function is invoked ONLY AFTER acceptability of a spirogram 
        is registered (acceptability can be check manually or by the function check_acceptability_of_spirogram)
        Make sure signal is correctly positioned (flow-volume data should be prefarably arranged such that the 
        expiratory FVL is right skewed and PEF is positive), data standerdized and spirogram acceptability is checked. 
        The function calcualtes the usual spirometry parameters and stores in the spiro_signal_process object. It further
        reference values of spirometry parameters using ECCS93 if sex (1:male or 0:female), age (years) and
        height (cm) are provided
        '''
        if not hasattr(self, 'index1'):  
                # Ideally, indexes 1 and 2 are saved after acceptability of spirogram is checked
                # This handles any exceptional cases
                self.index1, self.index2=self.get_FE_start_end(start_type="BEV")
                
        if self.flag_given_signal_is_FE:            
            self.index0=None
        else:
            self.index0=self.get_FI_start()
            

        if not hasattr(self, 'FEV1'):  
            self.shift_TLC_to_orgin()      
            FEV1, FVC=self.calc_FEV1_FVC()
            PEF, FEF25, FEF50, FEF75, FEF25_75=self.calc_flow_parameters()
            self.FEV1=FEV1
            self.FVC=FVC
            self.Tiff=100*FEV1/FVC
            self.PEF=PEF
            self.FEF25=FEF25
            self.FEF50=FEF50
            self.FEF75=FEF75
            self.FEF25_75=FEF25_75
        
        if (sex is not None) and (age is not None) and (height is not None):
            self.Sex=sex
            self.Age=age
            self.Height=height
            
            # Update reference values
            self.FEV1_PerPred=round(100*self.FEV1/self.calc_ECCS93_ref("FEV1"),2)
            self.FVC_PerPred=round(100*self.FVC/self.calc_ECCS93_ref("FVC"),2)
            self.Tiff_PerPred=round(100*self.Tiff/self.calc_ECCS93_ref("Tiff"),2)
            self.PEF_PerPred=round(100*self.PEF/self.calc_ECCS93_ref("PEF"),2)
            self.FEF25_PerPred=round(100*self.FEF25/self.calc_ECCS93_ref("FEF25"),2)
            self.FEF50_PerPred=round(100*self.FEF50/self.calc_ECCS93_ref("FEF50"),2)
            self.FEF75_PerPred=round(100*self.FEF75/self.calc_ECCS93_ref("FEF75"),2)
            self.FEF25_75_PerPred=round(100*self.FEF25_75/self.calc_ECCS93_ref("FEF25_75"),2)
            
        self.signal_finalized=True
            
        

        
##*******************************************************************
  
#%% This class is responsible for batch processing of spirometry data of individual patients
# It should be used to check within between manoeuvre criteria and for selecting best curve
         
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

#%% This class if for updating an existing dataframe with spirometry parameters
# calculated from raw data. 
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

     
#%% 
class spiro_features_extraction:
    '''
    This class implements different mathematical models for extracting features from spirometry
    signal. Following mathematical parameter calculations are supported
    1. AreaFE % predicted (https://www.dovepress.com/area-under-the-forced-expiratory-flow-volume-loop-in-spirometry-indica-peer-reviewed-fulltext-article-COPD)
    2. Angle of collapse (https://respiratory-research.biomedcentral.com/articles/10.1186/1465-9921-14-131)
    3. Deflating balloon (coming soon!)
    Note: FE - Forced expiratory
    '''
    class areaFE:
        '''
        Class for calculating AreaFE % predicted
        Requires:
        1. FE volume 
        2. FE flow
        3. Sex
        4. Age
        5. Height
        Note: This class expects correctly positioned and shifted FE signal 
            (in the FVL TLC should be at 0 and RV>0, flow>0,FVL is right skewed)
             and units standerdized (vol in litres, flow in litres/s and time in s)
        '''     
        def __init__(self,FE_volume, FE_flow, sex, age, height):
            self.volume=FE_volume
            self.flow=FE_flow
            self.sex = sex
            self.age = age
            self.height = height
        
        
        def calc_AreaPred(self, corr=1.0003):
        # function to calculate predicted ared
            sex=self.sex
            age = self.age
            height = self.height
            
            if (sex is None) or (age is None) or (height is None):
                print('Clinical charecterstics not provided')
                Area_Pred=None
            else:
                if sex==1:
                    FVC_Pred=5.76*height/100-0.026*age-4.34
                    PEF_Pred=6.14*height/100-0.043*age+0.15
                    FEF75_Pred=0.0261*height-0.026*age-1.34
                    FEF50_Pred=0.0379*height-0.031*age-0.35
                    FEF25_Pred=5.46*height/100-0.029*age-0.47
                else:
                    FVC_Pred=4.43*height/100-0.026*age-2.89
                    PEF_Pred=5.5*height/100-0.03*age-1.11
                    FEF75_Pred=0.0105*height-0.025*age+1.11
                    FEF50_Pred=2.45*height/100-0.025*age+1.16
                    FEF25_Pred=3.22*height/100-0.025*age+1.6
        
              
                v_PEFpred=0.25*FVC_Pred - 0.25*FVC_Pred*(PEF_Pred-FEF25_Pred)/(FEF25_Pred-FEF50_Pred)
                
                x_arr=np.array([0, v_PEFpred, 0.25*FVC_Pred, 0.5*FVC_Pred, 0.75*FVC_Pred, FVC_Pred])
                y_arr=np.array([0, PEF_Pred, FEF25_Pred, FEF50_Pred, FEF75_Pred, 0])
                Area_Pred =np.trapz(y_arr,x_arr) * corr
            
            return Area_Pred
        
        def calc_areaFE(self):
            areaFE=np.trapz(self.flow,self.volume)
            return areaFE
        
    
    class angle_of_collapse:
        '''
        Class for calculating angle of collapse
        Requires:
        1. FE volume 
        2. FE flow
        Note: This class expects correctly positioned and shifted FE signal 
            (in the FVL TLC should be at 0 and RV>0, flow>0,FVL is right skewed)
             and units standerdized (vol in litres, flow in litres/s and time in s)
        '''     
    
        def __init__(self,FE_volume, FE_flow):
            # Only FE signal after PEF is required
            PEF_index = np.argmax(FE_flow)
            self.volume=FE_volume[PEF_index:]
            self.flow=FE_flow[PEF_index:]
            #self.time=FE_time[PEF_index:]
          
            
        def generate_linemodel(self,x,y, index):
            # PEF and end points of FE
            x0=self.volume[0]
            y0=self.flow[0] 
            xn=self.volume[-1]
            yn=self.flow[-1]
            n = len(self.volume)
            # gen model by interpolating
#            vol_left=np.linspace(x0,x,index)
#            vol_right=np.linspace(x,xn,n-index) 
            
            vol_left = self.volume[0:index+1]
            vol_right = self.volume[index+1:]
                
            flow_left= np.interp( vol_left  ,np.array([x0, x]), np.array([y0, y]))
            flow_right= np.interp(vol_right,np.array([x, xn]), np.array([y, yn]))
            line_model_flow= np.append(flow_left,flow_right) 
            line_model_vol= np.append(vol_left,vol_right)
            
            return line_model_vol, line_model_flow
            
        def min_line_model_error(self, plotProcess = False):       
            # gen model by interpolating
            Jmin=1e10
            x_hat=None
            y_hat=None
            ind_min=None
            n=len(self.volume)
            # loop over all points
            ## NOTE: Efficient implementation is required
            if plotProcess:
                plt.figure(figsize=(5,4), dpi= 100, facecolor='w', edgecolor='k')
                plt.title('Angle of collapse fitting process')
            
            fvc = self.volume[-1] 
            
            for i in range(1,n-1):
                
                x=self.volume[i]
                y=self.flow[i]
                _, line_model_flow = self.generate_linemodel(x,y,i)
                J=(np.sum((line_model_flow-self.flow)**2))/n
                
                if plotProcess:
                    if (i%20==0):
                        line_model_vol, line_model_flow=self.generate_linemodel(x, y, i)
                        plt.plot(line_model_vol,line_model_flow)
                    
                
                if J<=Jmin:
                    Jmin=J
                    x_hat=x
                    y_hat=y
                    ind_min=i
            if plotProcess:
                plt.plot(self.volume,self.flow, color = 'black')
            return x_hat, y_hat, Jmin, ind_min
        
        def get_angle(self,x_p,y_p):
            x0=self.volume[0]
            y0=self.flow[0] 
            xn=self.volume[-1]
            yn=self.flow[-1]
            z1= complex(x0-x_p , y0 - y_p)
            z2=complex(x_p - xn, y_p - yn)
            line_model_angle= 180-(np.angle(z2,deg=True)- np.angle(z1,deg=True))
            return line_model_angle
        
        def calc_AC(self, plotModel = False, plotProcess = False):
            volume=self.volume
            flow=self.flow
            x_hat, y_hat, Jmin, ind_min =self.min_line_model_error(plotProcess)
            AC = self.get_angle(x_hat, y_hat)
            
            if plotModel:
                line_model_vol, line_model_flow=self.generate_linemodel(x_hat, y_hat, ind_min)
                #Plot
                ut=utilities()
                title_str="Angle of collapse = "+ str(round(AC,2))+", Jmin = " + str(round(Jmin,2))           
                plotdict1={'Model':[line_model_vol,line_model_flow],
                            'Original': [volume,flow],
                            'AxisLabels': ['Volume','Flow']}
                ut.plot_Model([plotdict1], title_str)
            
            return AC, Jmin
    
    class deflating_baloon:
        '''
        Class for calculating deflating balloon parameters
        Requires:
        1. FE time 
        2. FE volume
        3. FE flow
        Note: This class expects correctly positioned and shifted FE signal 
            (in the FVL TLC should be at 0 and RV>0, flow>0,FVL is right skewed)
             and units standerdized (vol in litres, flow in litres/s and time in s)
        '''     
        def __init__(self,FE_time, FE_volume, FE_flow):
            self.FE_time=FE_time
            self.FE_volume=FE_volume
            self.FE_flow=FE_flow
            
        def orient_and_snip_signal(self):
            # This function orients the signal so that hypothesis and the signal are of the same sign and range
            # Volume signal oriented so that RV is at 0 and TLC is at max positive
            # Flox signal is oriented from positive to negative
            # Do not temper the original signals
            
            #excite_index=self.excitation_index
            
            FE_vol=self.FE_volume
            FE_flow=self.FE_flow
            
            # oriented signals
            FE_vol_o=np.abs(FE_vol-FE_vol[-1])
            #FE_vol_os=FE_vol_o[excite_index:]
            
            FE_flow_o=-FE_flow
            #FE_flow_os=FE_flow_o[excite_index:]
            
            self.FE_vol_o=FE_vol_o #oriented volume signal
            #self.FE_vol_os=FE_vol_os 
            self.FE_flow_o=FE_flow_o #oriented flow signal
            #self.FE_flow_os=FE_flow_os

        def reorient_model(self):
            #This function reverts to the original volume signal so that RV is at max and TLC is at 0
            model_volume=self.model_volume
            model_flow=self.model_flow
            if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                model_volume=np.abs(model_volume-model_volume[0])
            else:
                del_v = self.FVC - self.FE_vol_o[self.excitation_index]
                model_volume=np.abs(model_volume-model_volume[self.excitation_index]) + del_v
            model_flow=-model_flow
            self.model_volume=model_volume
            self.model_flow=model_flow
        
        def get_excitation_phase(self,T1,params):
            # This function calculates the excitation phase between time[0] or t0 and time[excitation_index] or t1
            # Input are params and vector T1 between 0 and t1
            FVC=self.FVC
            if self.excitation_type=="Linear": # Discarded module
             # Assumes flow increases linearly from 0 to PEF between time[0] or t0 and time[excitation_index] or t1
             # respectively d
                 k_flow_slope=self.k_flow_slope
                 h1=FVC-(k_flow_slope/2)*np.square(T1)
                 h1_dash=-k_flow_slope*T1
            
            elif self.excitation_type=="Exponential pressure": # discarded module
            # Assumes pleural pressure is applied exponentially between time[0] or t0 and time[excitation_index] or t1
            
                alpha=params[2]
                a0 = params[3]
                
                h1 = a0 * (FVC/a0 - (np.exp(alpha*T1)/alpha**2) + (T1**2/2) + (T1/alpha) + (1/alpha**2))
                h1_dash = a0 * (T1 - np.exp(alpha*T1)/alpha + 1 /alpha )
            
            elif self.excitation_type=="Non linear":
            # Assumes flow increases non-linearly from 0 to PEF between time[0] or t0 and time[excitation_index] or t1
                 PEF=self.PEF
                 alpha=params[2]
                 beta=1+1/(alpha*PEF)
                 t1=T1[-1]
                 C=-(t1/beta)*np.log(abs(t1/beta))-alpha*beta*FVC
                 h1=(-1/(alpha*beta))*(T1+(t1/beta)*np.log(abs(T1-t1/beta))+C)
                 h1_dash=T1/(alpha*(t1-beta*T1))
            
            else:
            # flow motion between t0 and t1 is not modeled, 
            #assumes initial conditions of vol(t1) = FVC - del_v and flow(t1)
                #h1 = np.zeros(len(T1))
                h1 = self.FE_vol_o[0: self.excitation_index+1]
                h1_dash = self.FE_flow_o[0: self.excitation_index+1]
                #h1_dash[-1]  = -self.PEF
                
            return h1, h1_dash
        
        def calc_FEV1_FVC(self):
#            if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
#                ind = 0
#            else:
#                ind = self.excitation_index
            
            FE_Vol=self.model_volume
            FEtime=self.FE_time
                
            #plt.plot(FEtime,FE_Vol)    
            t0=FEtime[0]
            
            index_1s=0
            while FEtime[index_1s]<t0+1:
                index_1s=index_1s+1
            FEV1=np.interp(t0+1, [FEtime[index_1s],FEtime[index_1s+1]], [FE_Vol[index_1s],FE_Vol[index_1s+1]])       
    
                
            FVC=abs(FE_Vol[-1])
            return abs(round(FEV1,2)), round(FVC,2)
        
        def calc_hypothesis(self,params):
            # Unpack input parameters
            FE_time=self.FE_time
            
            # Get excitation index
            excitation_index=self.excitation_index
            n_vec=len(FE_time) # length of vector
            T1=FE_time[0:excitation_index+1] # time during which  flow increases 
            T2=FE_time[excitation_index:n_vec] # time during which ballon deflates 
            

            # Motion between time[0] and t1
            h1, h1_dash=self.get_excitation_phase(T1,params)
    
            
            x_t1=h1[-1] # volume at t1
            xdot_t1=h1_dash[-1] # flow at t1
            h1=h1[:-1].copy() # Removing one the last element from this array as this will double count in the next array
            h1_dash=h1_dash[:-1].copy()
            
            ## Motion between t1 and time[tn]
            
            # Unpack parameters
            wn=params[0]
            zeta=params[1]
            
            # Calculate dynamic components
            s1=(-zeta+np.sqrt(zeta**2-1))*wn # Pole 2
            s2=(-zeta-np.sqrt(zeta**2-1))*wn # Pole 1
            s3=(zeta+np.sqrt(zeta**2-1))*wn
            s4=(zeta-np.sqrt(zeta**2-1))*wn
            s5=2*wn*np.sqrt(zeta**2-1)
            
            C1=(x_t1*s3+xdot_t1)/s5
            C2=(-x_t1*s4-xdot_t1)/s5
            t1=FE_time[excitation_index]
            
            h2=(C1*np.exp(s1*(T2-t1))+C2*np.exp(s2*(T2-t1)))
            h2_dash=(s1*C1*np.exp(s1*(T2-t1))+s2*C2*np.exp(s2*(T2-t1)))
            
            h=np.append(h1,h2)
            h_dash=np.append(h1_dash,h2_dash)
            
            return h,h_dash
        
        def Cost_Function(self,param):
            ## Compute hypothesis
            h, h_dash=self.calc_hypothesis(param)
            
            ## compute cost

            # Unpack oriented original signal
            FE_vol_o=self.FE_vol_o
            FE_flow_o=self.FE_flow_o

            
            # Caculate J
            if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                J=np.sum((h - FE_vol_o)**2)+np.sum((h_dash - FE_flow_o)**2)
            else:
                ind = self.excitation_index
                J=np.sum((h[ind:] - FE_vol_o[ind:] )**2)+np.sum((h_dash[ind:]  - FE_flow_o[ind:])**2)
            return J
        
        def Cost_func_exp_pressure(self, params): # Discarded
            alpha=params[0]
            a0 = params[1]
            FE_time=self.FE_time
            excitation_index=self.excitation_index
            FVC = self.FVC
            T1=FE_time[0:excitation_index+1]
            h1 = a0 * (FVC/a0 - (np.exp(alpha*T1)/alpha**2) + (T1**2/2) + (T1/alpha) + (1/alpha**2))
            h1_dash = a0 * (T1 - np.exp(alpha*T1)/alpha + 1 /alpha )
            FE_vol_o=self.FE_vol_o
            FE_flow_o=self.FE_flow_o
            
            J=np.sum((h1 - FE_vol_o[0:excitation_index+1])**2)+np.sum((h1_dash - FE_flow_o[0:excitation_index+1])**2)
            return J
        
        def run_simulation(self,sim_param = 'zeta',sim_type="",num_sims=4, percentage_step=10, plot_FVL_only = True):
            # Read optimal parameters
            wn = self.wn
            zeta = self.zeta
            if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                alpha = self.alpha
            
            if sim_type == "Exponential pressure":
                a0 = self.a0
            ind = self.excitation_index
            # Init plots
            title_str = "Flow-volume loop simulation of " + sim_param
            if plot_FVL_only:
                plt.figure(figsize=(7,6), dpi= 100, facecolor='w', edgecolor='k')
                plt.title(title_str,fontsize=12,fontweight='bold')
            else:
                plt.figure(figsize=(6.5,12), dpi= 100, facecolor='w', edgecolor='k')
                plt.suptitle(title_str,fontsize=12,fontweight='bold')
            
            markerstyles= [".","*","-","x","2"]
            
            for step in np.arange(-np.floor(num_sims/2), np.floor(num_sims/2)+1):
                # Update simulation parameter
                if sim_param=="alpha":  
                    alpha = self.alpha + step * (percentage_step/100) * self.alpha
                elif sim_param=="zeta":
                    zeta = self.zeta + step * (percentage_step/100) * self.zeta
                elif sim_param=="omega":
                    wn = self.wn + step * (percentage_step/100) * self.wn
                    
                # Prepare parameter list
                if sim_type == "Exponential pressure":
                    param_list = [wn,zeta,alpha, a0]
                elif sim_type =="Non linear":
                    param_list = [wn,zeta,alpha]
                
                else:
                    param_list = [wn,zeta]
                    
                # calculate model flow and volume
                self.model_volume,self.model_flow = self.calc_hypothesis(param_list)
                self.reorient_model()
#                model_volume = self.model_volume
#                model_flow = self.model_flow
                FEV1, FVC = self.calc_FEV1_FVC()
                
                # plots
                if sim_param=='zeta':
                    sim_param_code = '\u03B6'
                elif sim_param=='omega':
                    sim_param_code = '\u03C9'
                    
                if step>0:
                    label =sim_param_code+" + " + str(step * (percentage_step)) + " %" +", FEV1  = "+str(FEV1)+" L, FVC = " + str(FVC)+" L"
                
                elif step<0:
                    label =sim_param_code+" - " + str(abs(step) * percentage_step) + " %" +", FEV1  = "+str(FEV1)+" L, FVC = " + str(FVC)+" L"
                
                elif step == 0:
                    label =sim_param_code+" baseline = "  + str(round(zeta,2)) +", FEV1  = "+str(FEV1)+" L, FVC = " + str(FVC)+" L"

                    
                #label =sim_param_code+" " + str(step * (percentage_step)) + " %" +", FEV1  = "+str(FEV1)+" L, FVC = " + str(FVC)+" L"
                if plot_FVL_only:
                    if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                        plt.plot(self.model_volume,self.model_flow,markerstyles[int(step+2)],linewidth=2,label=label)
                    else:
                        plt.plot(self.model_volume[ind:],self.model_flow[ind:],markerstyles[int(step+2)],linewidth=1.5,label=label)
                    plt.xlabel('Volume (L)',fontsize=11,weight='normal')
                    plt.ylabel('Flow (L/s)',fontsize=11,weight='normal')
                    plt.grid(True,which='both')
                    plt.legend()
                else:
                    plt.subplot(3,1,1)
                    if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                        plt.plot(self.model_volume,self.model_flow,markerstyles[int(step+2)],linewidth=2,label=label)
                    else:
                        plt.plot(self.model_volume[ind:],self.model_flow[ind:],markerstyles[int(step+2)],linewidth=2,label=label)
                    plt.xlabel('Volume (L)',fontsize=12,weight='normal')
                    plt.ylabel('Flow (L/s)',fontsize=12,weight='normal')
                    plt.grid(True,which='both')
                    plt.legend()
                    
                    plt.subplot(3,1,2)
                    if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                        plt.plot(self.FE_time, self.model_volume,markerstyles[int(step+2)],linewidth=2,label=label)
                    else:
                        plt.plot(self.FE_time[ind:], self.model_volume[ind:],markerstyles[int(step+2)],linewidth=2,label=label)
                    plt.xlabel('Time (s)',fontsize=12,weight='normal')
                    plt.ylabel('Volume (L)',fontsize=12,weight='normal')
                    plt.grid(True,which='both')
                    plt.legend()
                    
                    plt.subplot(3,1,3)
                    if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                        plt.plot(self.FE_time, self.model_flow,markerstyles[int(step+2)],linewidth=2,label=label)
                    else:
                        plt.plot(self.FE_time[ind:], self.model_flow[ind:],markerstyles[int(step+2)],linewidth=2,label=label)
                    plt.xlabel('Time (s)',fontsize=12,weight='normal')
                    plt.ylabel('Flow (L/s)',fontsize=12,weight='normal')
                    plt.grid(True,which='both')
                    plt.legend()
                    
            if plot_FVL_only:        
                plt.plot(self.FE_volume[0:ind],self.FE_flow[0:ind],linewidth=1)
        
        def run_model(self, excitation_type,plot_model=False, add_title_text="",plot_FVL_only=False):
            # Read signal
            FE_vol=self.FE_volume
            FE_flow=self.FE_flow
            
            ## Compute inputs
            # excite index
            excitation_index=np.argmax(FE_flow) # the PEF index
            self.excitation_index=excitation_index
            
            # FVC
            FVC=FE_vol[-1]-FE_vol[0]
            self.FVC=FVC
            
            # orient original signal and snip after excitation index for optimization
            self.orient_and_snip_signal()
             
            ## Optimize cost function
            self.excitation_type=excitation_type
            
            if excitation_type=="Linear": # Discarded module
                # flow slope
                t1=self.FE_time[excitation_index]
                k_flow_slope=FE_flow[excitation_index]/t1
                self.k_flow_slope=k_flow_slope
                param_final=differential_evolution(self.Cost_Function,bounds=[(0,10),(1,10)])
                
                # Collect final parameters
                wn=param_final.x[0]
                zeta=param_final.x[1]
                self.wn=wn
                self.zeta=zeta
                # calculate model flow and volume
                h,h_dash=self.calc_hypothesis([wn,zeta])
            
            elif excitation_type=="Exponential pressure": # Discarded module
                itn=1
                Jmin=1E10
                while itn<=3: # Run optimization three times and chose opt params with min J , done improve robustness of parameters
                    PEF_params= differential_evolution(self.Cost_func_exp_pressure,bounds=[(1,50),(1,50)],strategy='best1bin')
                    alpha_init = PEF_params.x[0]
                    a0_init = PEF_params.x[1]
                    
                    rad = 0.50
                    param_final=differential_evolution(self.Cost_Function,bounds=[(0,10),(1,10),(alpha_init-rad*alpha_init,alpha_init+rad*alpha_init),(a0_init-rad*a0_init, a0_init+rad*a0_init)],strategy='best1bin')
                    #param_final=differential_evolution(self.Cost_Function,bounds=[(0,10),(1,10),(0.01,100),(0.01,500)],strategy='best1bin')
                    # Collect final parameters
                    wn=param_final.x[0]
                    zeta=param_final.x[1]
                    alpha=param_final.x[2]
                    a0 = param_final.x[3]
                    
                    J = self.Cost_Function([wn,zeta,alpha, a0])
                    if J<Jmin:
                        Jmin = J
                        self.wn=wn
                        self.zeta=zeta
                        self.alpha=alpha
                        self.a0= a0
                        
                        # calculate model flow and volume
                        h,h_dash=self.calc_hypothesis([self.wn,self.zeta,self.alpha,self.a0])
                    
                    itn+=1
                    
            elif excitation_type=="Non linear": # Non linear start
                PEF=np.max(FE_flow)
                self.PEF=PEF
                param_final=differential_evolution(self.Cost_Function,bounds=[(0,2.5),(1,5),(0,-PEF)],strategy='best1bin')
                # Collect final parameters
                wn=param_final.x[0]
                zeta=param_final.x[1]
                alpha=param_final.x[2]
                
                self.wn=wn
                self.zeta=zeta
                self.alpha=alpha
                
                # calculate model flow and volume
                h,h_dash=self.calc_hypothesis([wn,zeta,alpha])

            else:  # default, with initial conditions vol(t1)= FVC-del_v and flow(t1) = PEF
                PEF=np.max(FE_flow)
                self.PEF=PEF
                param_final=differential_evolution(self.Cost_Function,bounds=[(0,3),(1,6)],strategy='best1bin')
                # Collect final parameters
                wn=param_final.x[0]
                zeta=param_final.x[1]
                self.wn=wn
                self.zeta=zeta

                
                # calculate model flow and volume
                h,h_dash=self.calc_hypothesis([wn,zeta])
            
            self.model_volume=h
            self.model_flow=h_dash
            
            # Reorient model signal with RV at 0 and TLC at max so that it is compatible
            # with the original signal
            self.reorient_model()
            
            # Calculate mean squared error
            from sklearn.metrics import mean_squared_error,r2_score
            if excitation_type in ["Linear", "Exponentifrom sklearn.metrics import mean_squared_error,r2_scoreal pressure", "Non linear"]:
                self.mse_volume=mean_squared_error(self.FE_volume,self.model_volume)
                self.mse_flow=mean_squared_error(self.FE_flow,self.model_flow)
                self.R2_volume=r2_score(self.FE_volume,self.model_volume)
                self.R2_flow=r2_score(self.FE_flow,self.model_flow)
            else:
                ind = self.excitation_index
                self.mse_volume=mean_squared_error(self.FE_volume[ind:],self.model_volume[ind:])
                self.mse_flow=mean_squared_error(self.FE_flow[ind:],self.model_flow[ind:])
                self.R2_volume=r2_score(self.FE_volume[ind:],self.model_volume[ind:])
                self.R2_flow=r2_score(self.FE_flow[ind:],self.model_flow[ind:])
            
            if plot_model:
                self.plot_model(plot_FVL_only,add_title_text)
            
             
        def plot_model(self,only_FVL,add_title_text):
            # Unpack signal
            FE_time=self.FE_time
            FE_vol=self.FE_volume
            FE_flow=self.FE_flow
            ind = self.excitation_index
            
            # Read model flow and volume
            model_vol=self.model_volume
            model_flow=self.model_flow
            
            # Read model params 
            zeta=round(self.zeta,2)
            wn=round(self.wn,2)
            
            # Read fit metrics 
            R2vol=round(self.R2_volume,2)
            R2flow=round(self.R2_flow,2)
            
            
            if self.excitation_type=="Non linear":
                alpha= round(abs(self.alpha),2)
                title_str=add_title_text+' : '+ "alpha ="+str(alpha) +", zeta ="+str(zeta) +", wn ="+ str(wn)
            
            elif self.excitation_type=="Exponential pressure":
                a0=round(self.a0,2)
                title_str=add_title_text+': '+ ", alpha ="+str(alpha) +", zeta ="+str(zeta) +", wn ="+ str(wn) +", R2vol ="+ str(R2vol)+", R2flow ="+ str(R2flow)
            else:
                title_str=add_title_text+': ' +"zeta ="+str(zeta) +", wn ="+ str(wn)+", R2vol ="+ str(R2vol)+", R2flow ="+ str(R2flow)
            #title_str=plot_title_text+' : '+ "zeta ="+str(zeta)+", wn="+ str(wn)
            
            if only_FVL:
                title_str=add_title_text+': '+ "alpha ="+str(alpha) +", zeta ="+str(zeta) +", wn ="+ str(wn)
                plt.figure(figsize=(7,6), dpi= 100, facecolor='w', edgecolor='k')
                plt.title(title_str,fontsize=12,fontweight='bold')
                plt.plot(FE_vol,FE_flow,color='black',linewidth=1.5,label='Original')
                
                plt.plot(model_vol,model_flow,'--',color='black',linewidth=1.5,label='Model')
                plt.xlabel('Volume (L)',fontsize=12,weight='normal')
                plt.ylabel('Flow (L/s)',fontsize=12,weight='normal')
                plt.grid(True,which='both')
                plt.legend()
            else:
                #16,4 horizontal
                #plt.figure(figsize=(6,16), dpi= 100, facecolor='w', edgecolor='k')
                plt.figure(figsize=(16,4), dpi= 100, facecolor='w', edgecolor='k')
                plt.suptitle(title_str,fontsize=12, fontweight='bold')
                
                plt.subplot(1,3,1)
                plt.plot(FE_vol,FE_flow,color='black',label='Original')
                if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                    plt.plot(model_vol,model_flow,'--',color='black',label='Model')
                else:
                    plt.plot(model_vol[ind:] ,model_flow[ind:] ,'--',color='black',label='Model')
                plt.grid(True,which='both')
                plt.xlabel('Volume (L)')
                plt.ylabel('Flow (L/s)')
                plt.legend()
                #plt.text(0,0,text)
                
                plt.subplot(1,3,2)
                plt.plot(FE_time,FE_vol,color='black',label='Original')
                if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                    plt.plot(FE_time,model_vol,'--',color='black',label='Model')
                else:
                    plt.plot(FE_time[ind:],model_vol[ind:],'--',color='black',label='Model')
                plt.grid(True,which='both')
                plt.xlabel('Time (s)')
                plt.ylabel('Volume (L)')
                plt.legend()
                
                plt.subplot(1,3,3)
                plt.plot(FE_time,FE_flow,color='black',label='Original')
                if self.excitation_type in ["Linear","Exponential pressure", "Non linear"]:
                    plt.plot(FE_time,model_flow,'--',color='black',label='Model')
                else:
                    plt.plot(FE_time[ind:],model_flow[ind:],'--',color='black',label='Model')
                plt.grid(True,which='both')
                plt.xlabel('Time (s)')
                plt.ylabel('Flow (L/s)')
                plt.legend()


#%% This is a class to calclulate features based on traditional spirometry parameters
# when only flow = np.array([PEF, FEF25, FEF50, FEF75, 0]) and 
# np.array(volume= [0, 0.25 FVC, 0.5 FVC, 0.75 FVC, FVC])
# ASSUMPTION: PEF vol is 0
                
class spiro_features_lite:
    def __init__(self, volume=None, flow=None):
        self.volume= volume
        self.flow = flow
    
    # Upsample volume and flow at uniform time points
    def upsample(self,timestep=0.1):
        ut=utilities()
        # Obtain time points correspoinding to FEFs points
        self.time=ut.get_time_from_FVL(self.flow,self.volume)
        # Upsample with required time step
        self.time_us, self.volume_us, self.flow_us=ut.sample_FVL_data(self.time,self.volume, self.flow,timestep)
    
    # Calculates area under FE loop and ration of areaFE to area of triangle
    def calc_areaFE(self):
        areaFE=np.trapz(self.flow,self.volume)
        return areaFE
    
    
    # Function to calculate Marko's features
    def calc_Marko_features(self,PY,FEV1,FEV1_PerPred,FVC,FVC_PerPred,
                            PEF, PEF_PerPred, FEF25, FEF25_PerPred,
                            FEF50, FEF50_PerPred, FEF75, FEF75_PerPred,
                            Raw, Raw_PerPred, sGaw, sGaw_PerPred,VC,
                            TLCO, TLCO_PerPred, KCO, KCO_PerPred):
        Marko_Params = {}
        
        Marko_Params['PEF_by_FVC'] = PEF/FVC
        Marko_Params['PEF_x_FVC'] = PEF*FVC
        if PY>0 and PY<5:
            Marko_Params['Smoking'] =  'Mild'
        else:
            if PY>5:
               Marko_Params['Smoking'] = "Yes"
            else:
                Marko_Params['Smoking']= "No"
            
        Marko_Params['delta_PEF_FEF25'] = (PEF - FEF25)
        Marko_Params['delta_PEF_FEF25_PerPred'] = PEF_PerPred - FEF25_PerPred
        Marko_Params['delta_FEF25_FEF50'] = (FEF25 - FEF50)
        Marko_Params['delta_FEF25_FEF50_PerPred']  = FEF25_PerPred - FEF50_PerPred
        Marko_Params['delta_FEF50_FEF75'] = (FEF50 - FEF75)
        Marko_Params['delta_FEF50_FEF75_PerPred'] = FEF50_PerPred - FEF75_PerPred
        
        Marko_Params['log_FEF75_PerPred'] = np.log(FEF75_PerPred)
        
        Marko_Params['log_Raw_PerPred'] = np.log(Raw_PerPred)
        Marko_Params['log_sGaw_PerPred'] = np.log(sGaw_PerPred)
        Marko_Params['delta_VC'] = FVC-VC
        
        
        Marko_Params['TLCO_by_KCO'] = TLCO/KCO
        Marko_Params['delta_KCO_TLCO'] = KCO_PerPred - TLCO_PerPred
        Marko_Params['log_TLCO_PerPred'] = np.log(TLCO_PerPred)
        
        return Marko_Params
        
    
    def calc_areaFE_Pred(self, sex, age, height):
        if sex==1:
            FVC_Pred=5.76*height/100-0.026*age-4.34
            PEF_Pred=6.14*height/100-0.043*age+0.15
            FEF75_Pred=0.0261*height-0.026*age-1.34
            FEF50_Pred=0.0379*height-0.031*age-0.35
            FEF25_Pred=5.46*height/100-0.029*age-0.47
        else:
            FVC_Pred=4.43*height/100-0.026*age-2.89
            PEF_Pred=5.5*height/100-0.03*age-1.11
            FEF75_Pred=0.0105*height-0.025*age+1.11
            FEF50_Pred=2.45*height/100-0.025*age+1.16
            FEF25_Pred=3.22*height/100-0.025*age+1.6
        
              
        v_PEFpred=0.25*FVC_Pred - 0.25*FVC_Pred*(PEF_Pred-FEF25_Pred)/(FEF25_Pred-FEF50_Pred)
        x_arr=np.array([0, v_PEFpred, 0.25*FVC_Pred, 0.5*FVC_Pred, 0.75*FVC_Pred, FVC_Pred])
        y_arr=np.array([0, PEF_Pred, FEF25_Pred, FEF50_Pred, FEF75_Pred, 0])
        
        Area_Pred =np.trapz(y_arr,x_arr)
        return Area_Pred        
    
    # Calculates FEF spline coefficients
    def calc_FEFspline_coeffs(self, order=3, plotModel=False):
        volume=self.volume[1:]
        flow=self.flow[1:]
        poly_coeffs=np.polyfit(volume, flow, order)
        poly=np.poly1d(poly_coeffs)
        if plotModel:
            model_flow=poly(volume)
            title_str="Spline order = "+ str(order)
            ut=utilities()
            plotdict1={'Model':[volume,model_flow],
                       'Original': [volume,flow],
                       'AxisLabels': ['Volume','Flow']}
            ut.plot_Model([plotdict1], title_str)
            
        return  poly_coeffs
    
    
    # Compute angle of collapse and angle_PEF
    def calc_angle_of_collapse(self, plotModel=False):
        index_PEF = np.argmax(self.flow_us)
        volume=self.volume_us[index_PEF:]
        flow=self.flow_us[index_PEF:]
        x0=volume[0]
        y0=flow[0] 
        xn=volume[-1]
        yn=flow[-1]
        n=len(volume)
        
        # Get angle between the two lines of the line model
        def get_angle(x_p,y_p):
            z1= complex(x0-x_p , y0 - y_p)
            z2=complex(x_p - xn, y_p - yn)
            line_model_angle= 180-(np.angle(z2,deg=True)- np.angle(z1,deg=True))
            return line_model_angle
        
        # generate the line model
        def generate_linemodel(x,y, index):
            # gen model by interpolating
            vol_left=np.linspace(x0,x,index)
            vol_right=np.linspace(x,xn,n-index) 
                
            flow_left= np.interp( vol_left  ,np.array([x0, x]), np.array([y0, y]))
            flow_right= np.interp(vol_right,np.array([x, xn]), np.array([y, yn]))
            line_model_flow= np.append(flow_left,flow_right) 
            line_model_vol= np.append(vol_left,vol_right)
            
            return line_model_vol, line_model_flow
        
        # Find the optimal error
        def min_line_model_error():       
            # gen model by interpolating
            Jmin=1e10
            x_hat=None
            y_hat=None
            ind_min=None
            J_list = []
            # loop over all points
            ## NOTE: Efficient implementation is required
            for i in range(1,n-1):
                x=volume[i]
                y=flow[i]
                
                _, line_model_flow = generate_linemodel(x,y,i)
                J=(np.sum((line_model_flow-flow)**2))/n
                J_list.append(J)
                if J<=Jmin:
                    Jmin=J
                    x_hat=x
                    y_hat=y
                    ind_min=i
                    
            return x_hat, y_hat, Jmin, ind_min
        
        x_hat, y_hat, Jmin, ind_min =min_line_model_error()
        AC = get_angle(x_hat, y_hat)
        angle_PEF = 180-get_angle(volume[0], flow[0])
        if plotModel:
            line_model_vol, line_model_flow=generate_linemodel(x_hat, y_hat, ind_min)
            #Plot
            ut=utilities()
            title_str="Angle of collapse = "+ str(round(AC,2))+", Jmin = " + str(round(Jmin,2))           
            plotdict1={'Model':[line_model_vol,line_model_flow],
                        'Original': [volume,flow],
                        'AxisLabels': ['Volume','Flow']}
            ut.plot_Model([plotdict1], title_str)
        
        return AC, angle_PEF
    
    
    # function to calculate deflating balloon zeta and wn from traditional PEF and FEF params
    def calc_def_balloon_lite(self, plotModel=False):
         index_PEF = np.argmax(self.flow_us)
         volume= self.volume_us[index_PEF:]
         volume = volume- volume[0]
         volume = np.abs(volume-volume[-1])
         flow=self.flow_us[index_PEF:]
         time=self.time_us[index_PEF:]
         
         
         volume=np.abs(volume-volume[-1])
         flow=-flow
         
         def calc_hypothesis(params):
            # Initial conditions
            x_t1=volume[0]
            xdot_t1=flow[0]
             
            # Unpack parameters
            wn=params[0]
            zeta=params[1]
            
            # Solve initial conditions
            s1=(-zeta+np.sqrt(zeta**2-1))*wn
            s2=(-zeta-np.sqrt(zeta**2-1))*wn
            s3 = 2*wn*np.sqrt(zeta**2-1)
#            s3=(zeta+np.sqrt(zeta**2-1))*wn
#            s4=(zeta-np.sqrt(zeta**2-1))*wn
#            s5=2*wn*np.sqrt(zeta**2-1)
#            
#            C1=(x_t1*s3+xdot_t1)/s5
#            C2=(-x_t1*s4-xdot_t1)/s5
            C1 = (xdot_t1 - s2 *x_t1 )/s3
            C2 = (- xdot_t1 + s1 * x_t1 )/s3
            t1=time[0]
            
            h=(C1*np.exp(s1*(time-t1))+C2*np.exp(s2*(time-t1)))
            h_dash=(s1*C1*np.exp(s1*(time-t1))+s2*C2*np.exp(s2*(time-t1)))
            
            return h,h_dash
         
         def Cost_Function(param):
             ## Compute hypothesis
             h, h_dash=calc_hypothesis(param)
             
             # Caculate J
             J=np.sum((h - volume)**2)+np.sum((h_dash - flow)**2)
             return J
           
         param_final=differential_evolution(Cost_Function,bounds=[(0,10),(1,10)],strategy='best1bin')
         
         w=param_final.x[0]
         zeta=param_final.x[1]

         if plotModel:
             h,h_dash=calc_hypothesis([w, zeta])
             
             # reorient signals
             model_volume=np.abs(h-h[0])
             model_flow=-h_dash
             
             # retrieve original signals
             volume_orig=np.abs(volume-volume[0])
             flow_orig=-flow
             
             # Plots
             ut=utilities()
             plotdict1={'Model':[model_volume,model_flow],
                        'Original': [volume_orig,flow_orig],
                        'AxisLabels': ['Volume','Flow']}
             
             title_str="zeta = "+str(round(zeta,2)) +", w = "+ str(round(w,2))
             ut.plot_Model([plotdict1], title_str)
         return w, zeta
                

#%% utilities that allow various operations
class utilities:           
    def __init__(self):
        None
    # derive flow  from volume
    def get_flow_from_vol(self,vol,time):
        dt=np.diff(time) 
        dvol=np.diff(vol)
        flow=dvol/dt
        flow=np.append(0,flow)
        return flow

    # derive volume  from flow
    def get_vol_from_flow(self,flow,time):
        dt=np.diff(time)
        dvol=dt*flow[1:]
        vol=np.append(0,np.cumsum(dvol))
        return vol 
    
    # derive time from flow-volume loop
    def get_time_from_FVL(self,flow, volume):
        n=len(volume)
        del_vol=np.array(volume[1:n])-np.array(volume[0:n-1])
        del_time=del_vol/(0.5*(flow[1:n]+flow[0:n-1])) # use average flow to find del time
        time=np.cumsum(del_time)
        time=np.append(0,time)
        return time
    
    # Modify  flow, vol with constant time sampling
    def sample_FVL_data(self,time, vol=None, flow=None,timestep=0.1):
         # Perfomrs uniform sampling with linear interpolation
         t0=time[0]
         tn=time[-1]
         time_comp=np.arange(t0,tn,timestep)
         #time_comp=np.append(time_comp, tn)
         
         if vol is not None:
             vol_comp=np.interp(time_comp,time,vol)
         if flow is not None:
             flow_comp=np.interp(time_comp,time,flow)
         return time_comp, vol_comp, flow_comp
    
    def add_noise_to_FVLdata(self,sp,mode):
        time = sp.time
        flow = sp.flow
        
        
        index1, index2 = sp.get_FE_start_end(start_type="thresh_PEF")
        index1s = sp.get_Indexes_In_1s(start_index = index1)
        
        PEF_index = sp.get_PEF_index(index1, index2)
        PEF = flow[PEF_index]
        
        
        if mode ==1 :
           max_flow_noise = np.random.uniform(0.05,0.20)*PEF
           n_begin_dist =  np.random.randint(1, (PEF_index-index1)+0.5*index1s)
           n_locs = np.random.randint(0.5*index1s, 5*index1s)
           n_locs = np.minimum( n_locs , len(time) - (n_begin_dist+index1))
           #flow[index1 + n_begin_dist:index1 + n_begin_dist+n_locs] = np.random.normal(0,1,n_locs)* max_flow_noise
           flow[index1 + n_begin_dist:index1 + n_begin_dist+n_locs] = flow[index1 + n_begin_dist:index1 + n_begin_dist+n_locs]+np.random.normal(0,1,n_locs)* max_flow_noise
        
        else:
          max_flow_noise = np.random.uniform(0.05,0.25)*PEF
          begin_indx =  np.random.randint(0, index1)
          n_locs = np.random.randint(2*index1s, len(time)-begin_indx)
          flow[begin_indx:begin_indx+n_locs]=np.random.normal(0,1,n_locs)* max_flow_noise
          
        
        vol_noise = self.get_vol_from_flow(flow,time)
        return vol_noise, flow
        
        
    
    def convert2grayscale(self, x,y, mode='FVL',size=32, fig_dpi = 150, monitor_dpi = 145, x_unit_spacing =10, y_unit_spacing=10 , axis_flag ='on',plot_original=False,display_GS=False):
        from skimage import color
        from scipy.misc import imresize 
        
        f, ax = plt.subplots(frameon=False)
        y_range = abs(np.max(y) - np.min(y))  +  2
        x_range = abs(np.max(x) - np.min(y))  + 2
        disp_inches_height = (monitor_dpi/fig_dpi)*y_range * y_unit_spacing * 0.039
        disp_inches_width = (monitor_dpi/fig_dpi)*x_range * x_unit_spacing * 0.039
        f.set_size_inches(disp_inches_width ,disp_inches_height)
        f.set_dpi(fig_dpi)
        ax.axis(axis_flag)
        ax.plot(x,y, color='black')
        
        if mode =='FVL': # for flow-volume loop
            # x : volume, y : flow
            # x_unit-spacing will be adjusted according to aspect ratio
            ax.set_aspect(0.5)
        elif mode == 'VT': # for vol-time renderin
            pass
            # x : time, y : volume
            
        ax.set_xlim([np.min(x)-0.5, np.max(x)+0.5])
        ax.set_ylim([np.min(y)-0.5, np.max(y)+0.5])
         
        f.canvas.draw()
            
        # grab the pixel buffer and dump it into a numpy array
        X_img_orig = np.array(f.canvas.renderer._renderer)
        if plot_original==False:
             f.clear()
         
        X_gray = color.rgb2gray(X_img_orig)
        X_gray_resized = imresize(X_gray, (size,size),  interp='bicubic')
         
        if display_GS:
            fig2 = plt.figure()
            ax2 = fig2.add_subplot(111, frameon=False)
            ax2.imshow(X_gray_resized,'gray')
            ax2.axis('off')
            plt.show()
     
        return X_gray_resized

    def plot_Model(self,PLotdictslist, title_str):
        
        total_plots=len(PLotdictslist)
        
        if total_plots==1:
            
            # Unpack input
            plotdict=PLotdictslist[0]
            Model_x=plotdict['Model'][0]
            Model_y=plotdict['Model'][1]
            Orig_x=plotdict['Original'][0]
            Orig_y=plotdict['Original'][1]
            xlabel = plotdict['AxisLabels'][0]
            ylabel = plotdict['AxisLabels'][1]
            
            # plot
            plt.figure(figsize=(5,4), dpi= 100, facecolor='w', edgecolor='k')
            plt.title(title_str,fontsize=12,fontweight='bold')
            plt.plot(Orig_x,Orig_y,color='black',label='Original')
            plt.plot(Model_x,Model_y,'--',color='black',label='Model')
            plt.grid(True,which='both')
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.legend()
        else:
            plt.figure(figsize=(16,4), dpi= 100, facecolor='w', edgecolor='k')
            plt.suptitle(title_str,fontsize=12, fontweight='bold')
            
            for i in range(1,total_plots+1):
                plotdict=PLotdictslist[0]
                Model_x=plotdict['Model'][0]
                Model_y=plotdict['Model'][1]
                Orig_x=plotdict['Original'][0]
                Orig_y=plotdict['Original'][1]
                xlabel = plotdict['AxisLabels'][0]
                ylabel = plotdict['AxisLabels'][1]
                
                plt.subplot(1,total_plots,i)
                plt.plot(Orig_x,Orig_y,color='black',label='Original')
                plt.plot(Model_x,Model_y,'--',color='black',label='Model')
                plt.grid(True,which='both')
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.legend()
    
    

         

         
         
         
         
         
         
         
         
         
         
         
         
         
         
