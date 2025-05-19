import json
from scipy.signal import find_peaks
# from vm_plotter import plot_stim_volts_pair
from neuron import h
import numpy as np
import matplotlib.pyplot as plt
# from scalebary import add_scalebar
my_dpi = 96
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
#plt.rcParams['font.sans-serif'] = "Arial"
#plt.rcParams['font.family'] = "sans-serif"
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
tick_major = 6
tick_minor = 4
plt.rcParams["xtick.major.size"] = tick_major
plt.rcParams["xtick.minor.size"] = tick_minor
plt.rcParams["ytick.major.size"] = tick_major
plt.rcParams["ytick.minor.size"] = tick_minor
font_small =9
font_medium = 13
font_large = 14
plt.rc('font', size=font_small)          # controls default text sizes
plt.rc('axes', titlesize=font_medium)    # fontsize of the axes title
plt.rc('axes', labelsize=font_medium)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=font_small)    # fontsize of the tick labels
plt.rc('ytick', labelsize=font_small)    # fontsize of the tick labels
plt.rc('legend', fontsize=font_small)    # legend fontsize
plt.rc('figure', titlesize=font_large)   # fontsize of the figure title
"""
ntimestep = 10000
dt = 0.02
def_times = np.array([dt for i in range(ntimestep)])
def_times = np.cumsum(def_times)
"""
def cm_to_in(cm):
    return cm/2.54




def get_fi_curve(mdl,s_amp,e_amp,nruns,wt_data=None,wt2_data=None, ax1=None,fig = None,dt = 0.01,fn = './Plots/ficurve.pdf'):
    all_volts = []
    npeaks = []
    x_axis = np.linspace(s_amp,e_amp,nruns)
    stim_length = int(600/dt)
    stim_length2 = int(1000/dt)
    for curr_amp in x_axis:
        mdl.init_stim(amp = curr_amp,dt = dt)
        curr_volts,_,_,_ = mdl.run_model()
        #curr_peaks,_ = find_peaks(curr_volts[:stim_length],height = -20)
        curr_peaks,_ = find_peaks(curr_volts[:stim_length2],height = -30) #modified for na16 TTX experiments
        all_volts.append(curr_volts)
        npeaks.append(len(curr_peaks))
    print(npeaks) #spikes at each stim current for FI curve
    if ax1 is None:
        fig,ax1 = plt.subplots(1,1)
        ax1.plot(x_axis,npeaks,marker = 'o',markersize=1,linestyle = '-',color = 'red')
    ax1.set_title('FI Curve')
    ax1.set_xlabel('Stim [nA]')
    ax1.set_ylabel('nAPs for 500ms epoch')
    if wt_data is None:
        fig.show()
        fig.savefig(fn)
        return npeaks
    else:
        ax1.plot(x_axis,wt_data,marker = 'o',markersize=1,linestyle = '-',color = 'black') #mutant will be red
        if wt2_data is not None:
          ax1.plot(x_axis,wt2_data,marker = 'o',markersize=1, linestyle='-', color = 'blue') #plots additional FI curve that you must supply array
        #ax1.plot(x_axis,wt_data,'black')
    fig.show()
    fig.savefig(fn)
    return(npeaks)
def plot_dvdt_from_volts(volts,dt,axs=None,clr = 'black',skip_first = False): #red #99023c #blue #6cc9ff #007dbc
    if skip_first:
        curr_peaks,_ = find_peaks(volts,height = -20)
        volts = volts[curr_peaks[0]+int(3/dt):]
    if axs is None:
        fig,axs = plt.subplots(1,1)
    dvdt = np.gradient(volts)/dt 
    
    # print(volts)
    # print(dt)
    # print(dvdt)
    # print(type(volts))
    # print(len(volts))
    # print(type(dt))
    # print(type(dvdt))
    # print(len(dvdt))
    #dvdt = np.gradient(volts)/dt
    
    axs.plot(volts, dvdt, color = clr, linewidth=0.5)
    #axs.plot(volts[1:20000], dvdt[1:20000], color = clr)#plot first peak only

    return axs

#plot first AP only
def plot_dvdt_from_volts_firstpeak(volts,dt,axs=None,clr = 'black',skip_first = False): #red #99023c #blue #6cc9ff #007dbc
    if skip_first:
        curr_peaks,_ = find_peaks(volts,height = -20)
        volts = volts[curr_peaks[0]+int(3/dt):]
    if axs is None:
        fig,axs = plt.subplots(1,1)
    dvdt = np.gradient(volts)/dt 
    
    # print(volts)
    # print(dt)
    # print(dvdt)
    # print(type(volts))
    # print(len(volts))
    # print(type(dt))
    # print(type(dvdt))
    # print(len(dvdt))
    #dvdt = np.gradient(volts)/dt
    
    #axs.plot(volts, dvdt, color = clr)
    axs.plot(volts[1:12500], dvdt[1:12500], color = clr)#plot first peak only [1:20000] was original

    return axs

def plot_dvdt_from_volts_wtvmut(volts,wt_Vm,dt,axs=None,het_Vm=None,clr = 'red',skip_first = False): #red #99023c #blue #6cc9ff #007dbc
    if skip_first:
        curr_peaks,_ = find_peaks(volts,height = -20)
        volts = volts[curr_peaks[0]+int(3/dt):]
    if axs is None:
        fig,axs = plt.subplots(1,1)
    dvdtwt = np.gradient(wt_Vm)/dt
    dvdt = np.gradient(volts)/dt
    if het_Vm is not None:
        dvdthet = np.gradient(het_Vm)/dt
     
    
    # print(volts)
    # print(dt)
    # print(dvdt)
    # print(type(volts))
    # print(len(volts))
    # print(type(dt))
    # print(type(dvdt))
    # print(len(dvdt))
    #dvdt = np.gradient(volts)/dt
    
    #axs.plot(volts, dvdt, color = clr)
    
    axs.plot(volts, dvdt, color = clr,linewidth=0.5)#plot first peak only [1:20000] was original
    axs.plot(wt_Vm,dvdtwt,color='black', alpha=0.8,linewidth=0.5)
    if het_Vm is not None:
        axs.plot(het_Vm,dvdthet,color='cadetblue', alpha=0.8,linewidth=0.5)
    return axs

def plot_dg_dt(g,volts,dt,axs=None,clr = 'black'):
    if axs is None:
        fig,axs = plt.subplots(1,1)
    dgdt = np.gradient(g)/dt
    axs.plot(volts, dgdt, color = clr)

def plot_extra_volts(t,extra_vms,axs = None,clr = 'black'):
    if axs is None:
        fig,axs = plt.subplots(3,figsize=(cm_to_in(8),cm_to_in(23)))
    axs[0].plot(t,extra_vms['ais'], label='ais', color=clr,linewidth=1)
    axs[0].locator_params(axis='x', nbins=5)
    axs[0].locator_params(axis='y', nbins=8)
    axs[0].set_title('AIS')
    axs[1].plot(t,extra_vms['nexus'], label='nexus', color=clr,linewidth=1)
    axs[1].locator_params(axis='x', nbins=5)
    axs[1].locator_params(axis='y', nbins=8)
    axs[1].set_title('Nexus')
    axs[2].plot(t,extra_vms['dist_dend'], label='dist_dend', color=clr,linewidth=1)
    axs[2].locator_params(axis='x', nbins=5)
    axs[2].locator_params(axis='y', nbins=8)
    axs[2].set_title('dist_dend')





def update_mech_from_dict(mdl,dict_fn,mechs,input_dict = False, param_name='a1_0'):
    if input_dict:
        param_dict = dict_fn
    else:
        with open(dict_fn) as f:
            data = f.read()
        param_dict = json.loads(data)
    print(f'updating {mechs} with {param_dict}')
    isUpdated = False
    for curr_sec in mdl.sl:
        # print(f'current section {curr_sec}') ###120523 TF
        if curr_sec.name() == 'cADpyr232_L5_TTPC1_0fb1ca4724[0].axon[0]': ##TF040224 if not axon[0], continues to for loop below
            print('THIS IS AXON 0 AH!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(f'Current Mech {curr_mech} and current section {curr_sec}')
            print('THIS IS AXON 0 AH!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            ##TF052324/##
            # Update all parameters except gbar for the axon section. AIS gbar will get updated when update_mod_param called (dependent on nav12/16)
            for curr_mech in mechs:
                print(f'Current Mech {curr_mech} and current section {curr_sec}') ###120523 TF
                if h.ismembrane(curr_mech, sec=curr_sec):
                    curr_name = h.secname(sec=curr_sec)
                    for seg in curr_sec:
                        for p_name in param_dict.keys():
                            hoc_cmd = f'{curr_name}.{p_name}_{curr_mech}({seg.x}) = {param_dict[p_name]}'
                            print(f'hoc command {hoc_cmd}')
                            h(hoc_cmd)
            continue
            ##/TF05224##
            
        # Update all other sections other than axon[0]
        for curr_mech in mechs:
            print(f'Current Mech {curr_mech} and current section {curr_sec}') ###120523 TF
            if h.ismembrane(curr_mech, sec=curr_sec):
                isUpdated = True
                curr_name = h.secname(sec=curr_sec)
                #sec = h.Section()

                #######Original
                # for p_name in param_dict.keys():
                #     hoc_cmd = f'{curr_name}.{p_name}_{curr_mech} = {param_dict[p_name]}'
                #     h(hoc_cmd)

                #in case we need to go per sec:
                  #  for seg in curr_sec:
                  #      hoc_cmd = f'{curr_name}.gbar_{channel}({seg.x}) *= {wt_mul}'
                  #      print(hoc_cmd)

                ##TF040124 altering to update axon[0] to get ais correct and not apply blanket gbar to all segs
                # Overwrite gbar for other sections
                for p_name in param_dict.keys():
                    if curr_sec != 'cADpyr232_L5_TTPC1_0fb1ca4724[0].axon[0]':
                        hoc_cmd = f'{curr_name}.{p_name}_{curr_mech} = {param_dict[p_name]}'
                        h(hoc_cmd)#############################
                    
                    ## Multiply gbar for the specific axon segment
                    # else:
                    #     for seg in curr_sec:
                    #         print('this is the one **************************************************************************************************************************************************************')
                    #         hoc_cmd1 = f'{curr_name}.{p_name}_{curr_mech} = {param_dict[p_name]}'
                    #         h(hoc_cmd1)
                    #         print(f'hoc command 1 {hoc_cmd1}')
                    #         hoc_cmd = f'{curr_name}.gbar_{curr_mech}({seg.x}) *= {param_dict[p_name]}'
                    #         print(f'hoc command {hoc_cmd}')
                    #         h(hoc_cmd)
                    #         print('this is the one **************************************************************************************************************************************************************')
    if(not isUpdated):
        print("Havent Updated in any section")
    else: print("Updated !!!!")
    return param_dict

##TF030624 Update mech from dict function specifically for HH mod files
def update_mech_from_dict_HH(mdl,dict_fn,mechs,input_dict = False, param_name='a1_0'):
    if input_dict:
        param_dict = dict_fn
    else:
        with open(dict_fn) as f:
            data = f.read()
        param_dict = json.loads(data)
    print(f'updating {mechs} with {param_dict}')
    
    for curr_sec in mdl.sl:
        print(f'current section {curr_sec}') ###120523 TF
        for curr_mech in mechs:
            print(f'Current Mech {curr_mech}') ###120523 TF
            if h.ismembrane(curr_mech, sec=curr_sec):
                curr_name = h.secname(sec=curr_sec)
                #print(f'Current Name {curr_name}')###120523 TF
                #sec = h.Section()
                #print(sec)
                #print(eval(f'h.psection(sec=sec)'))
                #print(h.Section())

                for p_name in param_dict.keys():
                    # print(f' p name {p_name}') ###120523 TF
                    hoc_cmd = f'{curr_name}.{p_name} = {param_dict[p_name]}'
                    # print(f'hoc command {hoc_cmd}') ###120523 TF
                    h(hoc_cmd)
              
                #in case we need to go per sec:
                  #  for seg in curr_sec:
                  #      hoc_cmd = f'{curr_name}.gbar_{channel}({seg.x}) *= {wt_mul}'
                  #      print(hoc_cmd)
    
    return param_dict

def update_mod_param(mdl,mechs,mltplr,gbar_name = 'gbar', print_flg =False):
    for curr_sec in mdl.sl:
        curr_name = h.secname(sec=curr_sec)
        for curr_mech in mechs:
            if h.ismembrane(curr_mech, sec=curr_sec):
                for seg in curr_sec:
                    hoc_cmd = f'{curr_name}.{gbar_name}_{curr_mech}({seg.x}) *= {mltplr}'
                    print(hoc_cmd)
                    # print(f'this is the par value')
                    par_value = h(f'{curr_name}.{gbar_name}_{curr_mech}({seg.x})')
                    h(hoc_cmd)
                    assigned_value = h(f'{curr_name}.{gbar_name}_{curr_mech}({seg.x})')
                    # print(f'this is the assigned value')
                    #h(f'{curr_name}.{gbar_name}_{curr_mech}({seg.x})')
                   
                    # print(f'par_value before{par_value} and after {assigned_value}')
                    if print_flg:
                       print(f'{curr_name}_{curr_mech}_{seg}_par_value before {par_value} and after {assigned_value}')
                       print(f'**********##### There is now {mltplr} of {curr_mech}\n\n')


def multiply_param(mdl,mechs,p_name,multiplier):
    for curr_sec in mdl.sl:
        for curr_mech in mechs:
            if h.ismembrane(curr_mech, sec=curr_sec):
                curr_name = h.secname(sec=curr_sec)
                hoc_cmd = f'{curr_name}.{p_name}_{curr_mech} *= {multiplier}'
                #print(hoc_cmd)
                h(hoc_cmd)
def offset_param(mdl,mechs,p_name,offset):
    for curr_sec in mdl.sl:
        for curr_mech in mechs:
            if h.ismembrane(curr_mech, sec=curr_sec):
                curr_name = h.secname(sec=curr_sec)
                hoc_cmd = f'{curr_name}.{p_name}_{curr_mech} += {offset}'
                print(hoc_cmd)
                h(hoc_cmd)
def update_param_value(mdl,mechs,p_name,value):
    for curr_sec in mdl.sl:
        for curr_mech in mechs:
            if h.ismembrane(curr_mech, sec=curr_sec):
                curr_name = h.secname(sec=curr_sec)
                hoc_cmd = f'{curr_name}.{p_name}_{curr_mech} = {value}'
                print(hoc_cmd)
                h(hoc_cmd)










#### Emily's code
def update_channel(mdl, channel_name, channel, dict_fn, wt_mul, mut_mul):
    """
    channel_name: str e.g 'na16mut'
    channel: str e.g. 'na16'
    """
    with open(dict_fn) as f:
        data = f.read()
    param_dict = json.loads(data)
    for curr_sec in mdl.sl:
        if h.ismembrane(channel_name, sec=curr_sec):
            curr_name = h.secname(sec=curr_sec)
            for seg in curr_sec:
                hoc_cmd = f'{curr_name}.gbar_{channel_name}({seg.x}) *= {mut_mul}'
                #print(hoc_cmd)
                h(hoc_cmd)
            for p_name in param_dict.keys():
                hoc_cmd = f'{curr_name}.{p_name} = {param_dict[p_name]}'
                #print(hoc_cmd)
                h(hoc_cmd)
        if h.ismembrane(channel, sec=curr_sec):
            curr_name = h.secname(sec=curr_sec)
            for seg in curr_sec:
                hoc_cmd = f'{curr_name}.gbar_{channel}({seg.x}) *= {wt_mul}'
                #print(hoc_cmd)
                h(hoc_cmd)


def update_K(mdl, channel_name, gbar_name, mut_mul):
    k_name = f'{gbar_name}_{channel_name}'
    prev = []
    for curr_sec in mdl.sl:
        if h.ismembrane(channel_name, sec=curr_sec):
            curr_name = h.secname(sec=curr_sec)
            for seg in curr_sec:
                hoc_cmd = f'{curr_name}.{k_name}({seg.x}) *= {mut_mul}'
                print(hoc_cmd)
                h(f'a = {curr_name}.{k_name}({seg.x})')  # get old value
                prev_var = h.a
                prev.append(f'{curr_name}.{k_name}({seg.x}) = {prev_var}')  # store old value in hoc_cmd
                h(hoc_cmd)
    return prev


def reverse_update_K(mdl, channel_name, gbar_name, prev):
    k_name = f'{gbar_name}_{channel_name}'
    index = 0
    for curr_sec in mdl.sl:
        if h.ismembrane(channel_name, sec=curr_sec):
            curr_name = h.secname(sec=curr_sec)
            for seg in curr_sec:
                hoc_cmd = prev[index]
                h(hoc_cmd)
                index += 1

def plot_stim(mdl, amp,fn,clr='blue'):
    mdl.init_stim(amp=amp)
    Vm, I, t, stim = mdl.run_model()
    plot_stim_volts_pair(Vm, f'Step Stim {amp}pA', file_path_to_save=f'./Plots/V1/{fn}_{amp}pA',times=t,color_str=clr)
    return I

def plot_FIs(fis, extra_cond = False):
    data = fis
    # save multiple figures in one pdf file
    filename= f'Plots/FI_plots.pdf'
    fig = plt.figure()
    x_axis, npeaks, name = data[0]
    plt.plot(x_axis, npeaks, label=name, color='black')
    # plot mut
    x_axis, npeaks, name = data[1]
    plt.plot(x_axis, npeaks, label=name, color='red')
    if extra_cond:
        # plot wtTTX
        x_axis, npeaks, name = data[2]
        plt.plot(x_axis, npeaks, label=name, color='black', linestyle='dashed')
        # plot mutTTX
        x_axis, npeaks, name = data[3]
        plt.plot(x_axis, npeaks, label=name, color='red', linestyle='dashed')

    plt.legend()
    plt.xlabel('Stim [nA]')
    plt.ylabel('nAPs for 600ms epoch')
    plt.title(f'FI Curve')
    fig.savefig(filename)


def plot_all_FIs(fis, extra_cond = False):
    for i in range(len(fis)):
        data = fis[i]
        # save multiple figures in one pdf file
        filename= f'Plots/FI_plots{i}.pdf'
        fig = plt.figure()
        x_axis, npeaks, name = data[0]
        plt.plot(x_axis, npeaks, label=name, color='black')
        # plot mut
        x_axis, npeaks, name = data[1]
        plt.plot(x_axis, npeaks, label=name, color='red')
        if extra_cond:
            # plot wtTTX
            x_axis, npeaks, name = data[2]
            plt.plot(x_axis, npeaks, label=name, color='black', linestyle='dashed')
            # plot mutTTX
            x_axis, npeaks, name = data[3]
            plt.plot(x_axis, npeaks, label=name, color='red', linestyle='dashed')

        plt.legend()
        plt.xlabel('Stim [nA]')
        plt.ylabel('nAPs for 500ms epoch')
        plt.title(f'FI Curve: for range {i}')
        fig.savefig(filename)
def scan12_16():
    for i12 in np.arange(0.5,1.5,0.1):
        for i16 in np.arange(0.5,1.5,0.1):
            sim = Na1612Model(nav12=i12, nav16=i16)
            sim.make_wt()
            fig_volts,axs = plt.subplots(2,figsize=(cm_to_in(8),cm_to_in(15)))
            sim.plot_stim(axs = axs[0],stim_amp = 0.7,dt=0.005)
            NH.plot_dvdt_from_volts(sim.volt_soma,sim.dt,axs[1])
            fn = f'./Plots/na1216_trials/vs_dvdt12_{i12}_16_{i16}.pdf'
            fig_volts.savefig(fn)

def get_spike_times(volts,times):
    inds,peaks = find_peaks(volts,height = -20)
    ans = [times[x] for x in inds]
    return ans