# -*- coding: utf-8 -*-
"""
Utility functions for spirometry data processing.
"""

import numpy as np
import matplotlib.pyplot as plt

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