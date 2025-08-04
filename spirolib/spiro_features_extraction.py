# -*- coding: utf-8 -*-
"""
Class for extracting features from spirometry signals using mathematical models.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
from .utilities import utilities

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
        
        
        def calc_AreaPred(self):
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
                Area_Pred =np.trapz(y_arr,x_arr)
            
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
