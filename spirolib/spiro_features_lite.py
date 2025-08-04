# -*- coding: utf-8 -*-
"""
Class to calculate features based on traditional spirometry parameters.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
from .utilities import utilities

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