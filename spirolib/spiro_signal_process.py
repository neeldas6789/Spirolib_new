# -*- coding: utf-8 -*-
"""
A class to perform various operations on spirometry data signals.
"""

import peakutils
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter


# Important: consistently followed: index0= start of FI, index1 =start of FE, index2=end of FE

class spiro_signal_process:
    def __init__(self,time,volume,flow,patientID,trialID, flag_given_signal_is_FE, scale3):
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
        scale= scale3
        self.time=np.array(time)*scale
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
