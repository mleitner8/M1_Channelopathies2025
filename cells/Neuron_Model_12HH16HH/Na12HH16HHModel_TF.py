from NeuronModelClass import NeuronModel
from NrnHelper import *
import matplotlib.pyplot as plt
import sys
from pathlib import Path
import numpy as np
from currentscape.currentscape import plot_currentscape
import pandas as pd
import os
import datetime
import csv


class Na12Model_TF:

    def __init__(self, na12name='na12annaTFHH2',
                 mut_name='na12annaTFHH2',
                 na12mechs=['na12', 'na12mut'],
                 na16name='na16HH_TF2',
                 na16mut_name='na16HH_TF2',
                 na16mechs=['na16', 'na16'],
                 params_folder='../cells/Neuron_Model_12HH16HH/params/',
                 ## na16name='na16_orig2',na16mechs = ['na16','na16mut'], na16mut_name='na16'

                 ais_nav12_fac=5.184,
                 nav12=1.17975,
                 soma_na12=2.9952,
                 dend_nav12=1.9305,

                 ais_nav16_fac=2.187,
                 nav16=2.574,
                 soma_na16=0.8,
                 dend_nav16=3.3,

                 somaK=2.2,
                 KP=0.00590625,
                 K=0.4,
                 KT=0.00075,
                 ais_ca=21.5,
                 ais_Kca=0.5,
                 node_na=1,
                 dend_K=0.025,
                 plots_folder='./Plots/', pfx='testprefix',
                 update=True, fac=None, na12_scale=None):

        # K = 1 ##TF020624
        # node_na = 0.5 #(0.5 good value, default following newAIS) #1#100#90#80#70#60#50#40#30#20 #10

        self.l5mdl = NeuronModel(nav12=nav12, nav16=nav16, axon_K=K, axon_Kp=KP, axon_Kt=KT, soma_K=somaK,
                                 ais_ca=ais_ca, ais_KCa=ais_Kca, soma_nav16=soma_na16, soma_nav12=soma_na12,
                                 node_na=node_na,
                                 ais_nav16_fac=ais_nav16_fac, ais_nav12_fac=ais_nav12_fac,
                                 # TF 012524 added ais_nav16 to change in reference to ais_nav12
                                 ##TF030624 Args below added to add update_mech_from_dict functionality to NeuronModel class.
                                 dend_nav12=dend_nav12,
                                 dend_nav16=dend_nav16,
                                 dend_K=dend_K,
                                 update=update,  ##Change to false if you don't want to update mechs
                                 na12name=na12name,
                                 na12mut_name=mut_name,
                                 na12mechs=na12mechs,
                                 na16name=na16name,
                                 na16mut_name=na16mut_name,
                                 na16mechs=na16mechs,
                                 params_folder=params_folder,
                                 fac=fac,
                                 na12_scale=na12_scale,
                                 )

        self.plot_folder = plots_folder
        self.plot_folder = f'{plots_folder}'
        Path(self.plot_folder).mkdir(parents=True, exist_ok=True)
        self.pfx = pfx

    # need to alter currents and current names to work for na12hmm
    def make_currentscape_plot(self, amp, time1, time2, pfx=None, stim_start=100, sweep_len=800, sim_config={
        'section': 'soma',
        'segment': 0.5,
        'section_num': 0,
        # 'section': 'axon',
        # 'segment': 0,
        # 'section_num':0,

        # 'currents'  : ['na12.ina_ina','na12mut.ina_ina','na16.ina_ina','na16mut.ina_ina','ica_Ca_HVA','ica_Ca_LVAst','ihcn_Ih','ik_SK_E2','ik_SKv3_1'],
        # 'currents'  : ['na12.ina','na12mut.ina','na16.ina','na16mut.ina','ica_Ca_HVA','ica_Ca_LVAst','ihcn_Ih','ik_SK_E2','ik_SKv3_1'],
        # 'currents'  : ['na16mut.ina_ina','ica_Ca_HVA','ica_Ca_LVAst','ihcn_Ih','ik_SK_E2','ik_SKv3_1'], #'na12.ina_ina','na12mut.ina_ina','na16.ina_ina' test_plot_TF2
        # 'currents'  : ['na16.ina_ina','na16mut.ina_ina','ica_Ca_HVA','ica_Ca_LVAst','ihcn_Ih','ik_SK_E2','ik_SKv3_1'], #test_plot_TF3 + others, needs Na12 currents
        # 'currents'  : ['na12.ina_ina','na16.ina_ina','na16mut.ina_ina','ica_Ca_HVA','ica_Ca_LVAst','ihcn_Ih','ik_SK_E2','ik_SKv3_1','i_pas'], #'na12mut.ina_ina'
        # 'currents'  : ['na12.ina_ina','na16.ina_ina','na16mut.ina_ina','ik_SKv3_1','i_pas'], #'na12mut.ina_ina'
        # 'currents'  :['ina','ica','ik'],
        # 'currents'  : ['ica_Ca_HVA','ica_Ca_LVAst','ik_SKv3_1','ik_SK_E2','na16.ina_ina','na16mut.ina_ina','na12.ina_ina','na12mut.ina_ina','i_pas'], #Currents for axon (no Ih)

        # 'currents'  : ['ica_Ca_HVA','ica_Ca_LVAst','ik_SKv3_1','ik_SK_E2','na16.ina_ina','na16mut.ina_ina','na12.ina_ina','na12mut.ina_ina','i_pas','ihcn_Ih'], #Normal currents for Na12 soma
        'currents': ['ica_Ca_HVA', 'ica_Ca_LVAst', 'ik_SKv3_1', 'ik_SK_E2', 'na16.ina_ina', 'na16mut.ina_ina',
                     'na12.ina_ina', 'na12mut.ina_ina', 'i_pas', 'ihcn_Ih'],  # Normal currents for Na12 soma

        'ionic_concentrations': ["cai", "ki", "nai"],
        'current_names': ['Ca_HVA', 'Ca_LVAst', 'SKv3_1', 'SK_E2', 'Na16 WT', 'Na16 WT', 'Na12', 'Na12 MUT', 'pas',
                          'Ih']  # Na16 WT current names (double na16 WT)

    }):
        # sim_obj = NeuronModel()   #TO DO : send in different parameters???

        # current_names = ['na12','na16','na16 mut','Ca_HVA','Ca_LVAst','Ih','SK_E2','SKv3_1','pas']
        # current_names = ['Ih','Ca_HVA','Ca_LVAst','SKv3_1','SK_E2','Na16 WT','Na16 WT','Na12','Na12 MUT','pas'] #Na16 WT current names (double na16 WT)
        # current_names = ['Ca_HVA','Ca_LVAst','SKv3_1','SK_E2','Na16 WT','Na16 WT','Na12','Na12 MUT','pas'] #Na16 WT current names (double na16 WT)

        current_names = sim_config['current_names']

        # current_names = ['Ih','Ca_HVA','Ca_LVAst','SKv3_1','SK_E2','Na16 WT','Na16 MUT','Na12','pas']
        # current_names = sim_config['outward'] + sim_config['inward']
        # amp = 0.5
        # sweep_len = 800
        self.l5mdl.init_stim(stim_start=stim_start, amp=amp,
                             sweep_len=sweep_len)  # modify stim_start to look at different time points?
        # Vm, I, t, stim,ionic = sim_obj.run_sim_model(dt=0.01,sim_config=sim_config)
        Vm, I, t, stim, ionic = self.l5mdl.run_sim_model(dt=0.1, sim_config=sim_config)  # change time steps here

        # Vm, I, t, stim, ionic = self.l5mdl.run_sim_model(start_Vm=-70, dt=0.01,sim_config=sim_config) #change time steps here

        #####*** Below for plotting user-specified time steps
        # sweep_len = 75
        dt = 0.1
        # time1 = 51 #start time in ms. Must be between 0 < x < sweep_len 54het 51ms->60msWT
        # time2 = 60 #end time in ms. Must be between 0 < x < sweep_len 63het
        step1 = int((time1 / dt))
        step2 = int((time2 / dt))
        Vmsteplist = Vm[step1:step2]  # assign new list for range selected between two steps
        # maxvm = max(Vm[step1:step2]) #gets max voltage
        # indexmax = Vmsteplist.argmax() #gets index (time point in Vmsteplist) where max voltage is
        #####***

        # print(I)
        # print([x for x in I.keys()])
        # print([x for x in ionic.keys()])
        # current_names = sim_config['currents']
        plot_config = {
            "output": {
                "savefig": True,
                # "dir": "./Plots/12HMM16HH_TF/SynthMuts_120523/Currentscape/",
                "dir": f"{self.plot_folder}",
                # "fname": "Na12_mut22_1nA_800ms", ########################################################_________________Change file name here
                "fname": f"{pfx}amp{amp}_t1-{time1}t2-{time2}_swp{sweep_len}_start{stim_start}",
                "extension": "pdf",
                # "extension": "jpg",
                "dpi": 600,
                "transparent": False},

            "show": {  # "total_contribution":True,
                # "all_currents":True,
                "currentscape": True},

            "colormap": {"name": "colorbrewer.qualitative.Paired_12"},
            # "colormap": {"name":"cartocolors.qualitative.Prism_10"},
            # "colormap": {"name":"cmocean.diverging.Balance_10"},

            "xaxis": {"xticks": [25, 50, 75],
                      "gridline_width": 0.2, },

            "current": {"names": current_names,
                        "reorder": False,
                        # "autoscale_ticks_and_ylim":False,
                        # "ticks":[0.00001, 0.001, 0.1], #3 xaxis lines???
                        # "ylim":[0.00001,0.01] #yaxis lims[min,max]
                        },

            "ions": {"names": ["ca", "k", "na"],
                     "reorder": False},

            "voltage": {"ylim": [-90, 50]},
            "legendtextsize": 5,
            "adjust": {
                "left": 0.15,
                "right": 0.8,
                "top": 1.0,
                "bottom": 0.0
            }
        }

        # print(plot_config['current'])
        # print('step at max value for vm')
        # # print(Vmsteplist)
        # print(f"the max voltage value is {maxvm}")
        # print(f"The index at which the max voltage happens is {indexmax}")

        # fig = plot_currentscape(Vm, [I[x] for x in I.keys()], plot_config,[ionic[x] for x in ionic.keys()]) #Default version that plots full sweep_len (full simulation)
        fig = plot_currentscape(
            Vm[step1:step2],
            [I[x][step1:step2] for x in I.keys()],
            plot_config,
            [ionic[x][step1:step2] for x in ionic.keys()]
        )  # Use this version to add time steps
        try:
            plt.close(fig)
        except Exception:
            pass
        # fig = plot_currentscape(Vm[step1:step2], [I[x][step1:step2] for x in I.keys()], plot_config) #112723 removing ionic currents at bottom

    def make_currentscape_plot_dual_stim(self,
                                         sweep_len,
                                         dt,
                                         soma_amp, soma_dur, soma_start,
                                         dend_amp, dend_dur, dend_start,
                                         dend_section_type, dend_section_index, dend_section_seg,
                                         dend_shape='epsp', tau1=1.0, tau2=6.0,
                                         time1=None, time2=None,
                                         pfx=None,
                                         sim_config=None):
        """Currentscape for dual-stim protocols (e.g., Larkum panels b–e).

        This configures the *same* soma + dend stimulation used by plot_dual_stim
        (including EPSP-shaped dend current injection), then runs run_sim_model so
        currents can be recorded at the requested sim_config segment.
        """
        if sim_config is None:
            raise ValueError('sim_config must be provided for currentscape dual-stim')
        if time1 is None:
            time1 = 0
        if time2 is None:
            time2 = sweep_len

        current_names = sim_config.get('current_names', sim_config.get('currents', []))

        # Configure soma and dend stimuli (do not run the model yet).
        self.l5mdl.init_stim(sweep_len=sweep_len, stim_start=soma_start, stim_dur=soma_dur, amp=soma_amp, dt=dt)

        if dend_shape == 'epsp':
            self.l5mdl.init_dend_epsp_stim(sweep_len=sweep_len, amp=dend_amp, stim_start=dend_start, dt=dt,
                                           tau1=tau1, tau2=tau2,
                                           section_type=dend_section_type, section_index=dend_section_index,
                                           section_seg=dend_section_seg)
        else:
            self.l5mdl.init_stim_dend_youpicksection(sweep_len=sweep_len, amp=dend_amp, stim_dur=dend_dur,
                                                     stim_start=dend_start, dt=dt,
                                                     section_type=dend_section_type, section_index=dend_section_index,
                                                     section_seg=dend_section_seg)

        # Run simulation while recording currents specified in sim_config.
        Vm, I, t, stim, ionic = self.l5mdl.run_sim_model(dt=dt, sim_config=sim_config)

        step1 = int(time1 / dt)
        step2 = int(time2 / dt)
        step1 = max(0, min(step1, len(Vm)))
        step2 = max(step1 + 1, min(step2, len(Vm)))

        plot_config = {
            "output": {
                "savefig": True,
                "dir": f"{self.plot_folder}",
                "fname": f"{pfx}_dualstim_t1-{time1}t2-{time2}_swp{sweep_len}_soma{str(soma_amp).replace('.', 'p')}@{soma_start}_dend{str(dend_amp).replace('.', 'p')}@{dend_start}",
                "extension": "pdf",
                "dpi": 600,
                "transparent": False
            },
            "show": {
                "currentscape": True
            },
            "colormap": {"name": "colorbrewer.qualitative.Paired_12"},
            "xaxis": {"xticks": [25, 50, 75], "gridline_width": 0.2},
            "current": {
                "names": current_names,
                "reorder": False,
            },
            "ions": {"names": ["ca", "k", "na"], "reorder": False},
            "voltage": {"ylim": [-90, 50]},
            "legendtextsize": 5,
            "adjust": {
                "left": 0.15,
                "right": 0.8,
                "top": 1.0,
                "bottom": 0.0
            }
        }

        fig = plot_currentscape(
            Vm[step1:step2],
            [I[x][step1:step2] for x in I.keys()],
            plot_config,
            [ionic[x][step1:step2] for x in ionic.keys()]
        )
        try:
            plt.close(fig)
        except Exception:
            pass

        ###### Writing all raw data to csv
        # with open("./Plots/12HH16HMM_TF/111423/Currentscape/Na16_WT_1na_75ms_rawdata.csv",'w',newline ='') as csvfile:
        #     writer = csv.writer(csvfile, delimiter = ',')
        #     #writer.writerow(current_names)
        #     writer.writerow(I.keys())

        #     writer.writerows(I[x] for x in I) # This and line below for writing data from entire sweep_len
        #     writer.writerow(Vm)

        # writer.writerows(I[x][step1:step2] for x in I) ####This and below line are used when time steps are used
        # writer.writerow(Vm[step1:step2])

    # __________added this function to get overexp and ttx to work
    def make_mut(self, mut_mech, p_fn_na12_mech):
        print(f'updating mut {mut_mech} with {p_fn_na12_mech}')
        self.na12_pmech = update_mech_from_dict(self.l5mdl, p_fn_na12_mech, self.mut_mech)

    # ______________________________________________________________#

    def update_gfactor(self, gbar_factor=1):
        update_mod_param(self.l5mdl, self.mut_mech, gbar_factor, gbar_name='gbar')

    def plot_stim(self, stim_amp=0.5, dt=0.02, clr='black', plot_fn='step', axs=None, rec_extra=False, stim_dur=500):
        self.dt = dt
        if not axs:
            fig, axs = plt.subplots(1, figsize=(cm_to_in(8), cm_to_in(7.8)))
        self.l5mdl.init_stim(stim_dur=stim_dur, amp=stim_amp)
        if rec_extra:
            Vm, I, t, stim, extra_vms = self.l5mdl.run_model(dt=dt, rec_extra=rec_extra)
            self.extra_vms = extra_vms
        else:
            Vm, I, t, stim, _ = self.l5mdl.run_model(dt=dt)

        self.volt_soma = Vm
        self.I = I
        self.t = t
        self.stim = stim

        ap_t = (t / dt) * 1000  ##Get timesteps

        axs.plot(t, Vm, label='Vm', color=clr, linewidth=0.5)  ##TF031424 changed linewidth
        axs.locator_params(axis='x', nbins=5)
        axs.locator_params(axis='y', nbins=8)
        # plt.show()
        # add_scalebar(axs)
        file_path_to_save = f'{self.plot_folder}{plot_fn}.pdf'
        # plt.savefig(file_path_to_save, format='pdf') ##TF031424 removed to avoid duplicates since plotting dvdt_from_volts as well.
        return ap_t, Vm

    def plot_dual_stim(self, soma_amp=0.3, soma_dur=100, soma_start=30,
                       dend_amp=0.5, dend_dur=100, dend_start=35,
                       dend_section_type='dend', dend_section_index=0, dend_section_seg=0.5,
                       dend2_section_type=None, dend2_section_index=None, dend2_section_seg=0.5,
                       dt=0.02, clr='black', plot_fn='dual_step', axs=None, rec_extra=False, sweep_len=500,
                       dend_shape='epsp', tau1=1.0, tau2=6.0,
                       volt_ylim=None):  # Default taus similar to typical, increase tau2 if "cutting off"
        """
        Plots the response to dual stimulation (somatic + dendritic).
        """
        self.dt = dt

        # If no axs provided, create 2 subplots (Voltage top, Current bottom)
        if not axs:
            fig, axs = plt.subplots(2, 1, figsize=(cm_to_in(8), cm_to_in(12)), sharex=True)
            ax_volt = axs[0]
            ax_stim = axs[1]
        else:
            # Assume user passed valid axes if provided (single or list?)
            # Check if it is iterable (list, tuple, ndarray)
            if isinstance(axs, (list, tuple)) or hasattr(axs, 'flat'):
                # It's a collection of axes
                if hasattr(axs, 'flat'):
                    # Numpy array
                    flat = axs.flat
                    ax_volt = flat[0]
                    ax_stim = flat[1] if len(flat) > 1 else None
                else:
                    # List/Tuple
                    ax_volt = axs[0]
                    ax_stim = axs[1] if len(axs) > 1 else None
            else:
                # Single axis
                ax_volt = axs
                ax_stim = None  # Fallback

        # Run the dual stimulation model
        if rec_extra:
            Vm, I, t, stim, extra_vms, dend_Vm, dend2_Vm, dend_stim_trace = self.l5mdl.init_dual_stim_and_run(
                sweep_len=sweep_len, dt=dt,
                soma_amp=soma_amp, soma_dur=soma_dur, soma_start=soma_start,
                dend_amp=dend_amp, dend_dur=dend_dur, dend_start=dend_start,
                dend_section_type=dend_section_type, dend_section_index=dend_section_index,
                dend_section_seg=dend_section_seg,
                dend2_section_type=dend2_section_type, dend2_section_index=dend2_section_index,
                dend2_section_seg=dend2_section_seg,
                rec_extra=rec_extra, dend_shape=dend_shape, tau1=tau1, tau2=tau2
            )
            self.extra_vms = extra_vms
        else:
            Vm, I, t, stim, dend_Vm, dend2_Vm, dend_stim_trace = self.l5mdl.init_dual_stim_and_run(
                sweep_len=sweep_len, dt=dt,
                soma_amp=soma_amp, soma_dur=soma_dur, soma_start=soma_start,
                dend_amp=dend_amp, dend_dur=dend_dur, dend_start=dend_start,
                dend_section_type=dend_section_type, dend_section_index=dend_section_index,
                dend_section_seg=dend_section_seg,
                dend2_section_type=dend2_section_type, dend2_section_index=dend2_section_index,
                dend2_section_seg=dend2_section_seg,
                rec_extra=rec_extra, dend_shape=dend_shape, tau1=tau1, tau2=tau2
            )

        self.volt_soma = Vm
        self.I = I
        self.t = t
        self.stim = stim

        ap_t = (t / dt) * 1000  # Get timesteps

        # Plot Voltages
        ax_volt.plot(t, Vm, label='Soma', color=clr, linewidth=0.5)
        ax_volt.plot(t, dend_Vm, label='Dend (Red)', color='red', linewidth=0.5)  # , linestyle='--')
        if dend2_Vm is not None:
            ax_volt.plot(t, dend2_Vm, label='Dend2 (Blue)', color='blue', linewidth=0.5)

        ax_volt.set_ylabel('Voltage (mV)')
        ax_volt.locator_params(axis='y', nbins=8)
        if volt_ylim is not None:
            ax_volt.set_ylim(volt_ylim)
        ax_volt.legend(fontsize=6)

        # Plot Currents (Stims)
        if ax_stim:
            ax_stim.plot(t, stim, label='Soma Stim', color='black', linewidth=1.0)
            ax_stim.plot(t, dend_stim_trace, label='Dend Stim', color='red', linewidth=1.0)
            ax_stim.set_ylabel('Current (nA)', fontsize=7)  # Reduced fontsize
            ax_stim.set_xlabel('Time (ms)', fontsize=8)
            ax_stim.tick_params(axis='both', which='major', labelsize=7)
            ax_stim.legend(fontsize=5)
            # Enforce consistent Y-axis for Larkum plots (approx -0.1 to 2.5 nA covers the range)
            ax_stim.set_ylim(-0.1, 2.0)
            ax_stim.locator_params(axis='y', nbins=3)

        file_path_to_save = f'{self.plot_folder}/{plot_fn}.pdf'
        # IMPORTANT: save the figure associated with the provided axes.
        # Using pyplot's global savefig can accidentally save the most-recently-created
        # figure (e.g., a currentscape) instead of the Larkum voltage figure.
        fig_to_save = ax_volt.figure
        fig_to_save.tight_layout()
        fig_to_save.savefig(file_path_to_save, format='pdf')
        return ap_t, Vm, dend_Vm, dend2_Vm

    # Plot both WT and mut on same stim plot
    def plot_wtvmut_stim(self, wt_Vm, wt_t,
                         stim_amp=0.5, dt=0.005, clr='red',
                         plot_fn='step', axs=None, rec_extra=False, stim_dur=500, het_Vm=None, het_t=None, sim_config={
                # 'section' : 'axon',
                # 'section_num' : 0,
                # 'segment' : 0,
                # 'currents'  :['ina','ica','ik'],
                # 'ionic_concentrations' :["cai", "ki", "nai"]
            }):
        self.dt = dt
        if not axs:
            fig, axs = plt.subplots(1, figsize=(cm_to_in(8), cm_to_in(7.8)))
        self.l5mdl.init_stim(stim_dur=stim_dur, amp=stim_amp)
        if rec_extra:
            Vm, I, t, stim, extra_vms = self.l5mdl.run_sim_model(dt=dt, rec_extra=rec_extra,
                                                                 sim_config=sim_config)  # changed run_model to run_sim_model to capture other segments
            self.extra_vms = extra_vms
        else:
            Vm, I, t, stim, ionic = self.l5mdl.run_sim_model(dt=dt,
                                                             sim_config=sim_config)  # changed run_model to run_sim_model to capture other segments

        self.volt_soma = Vm
        self.I = I
        self.t = t
        self.stim = stim

        vlength = len(Vm)
        tlength = len(t)

        print(f'tlength is {tlength}')
        print(f'vlength is {vlength}')

        axs.plot(wt_t[0:tlength], wt_Vm[0:vlength], label='WT', color='black', linewidth=0.5, alpha=0.8)
        if het_Vm is not None and het_t is not None:
            axs.plot(het_t[0:tlength], het_Vm[0:vlength], label='Heterozygous', color='cadetblue', linewidth=0.5,
                     alpha=0.8)
            axs.plot(t, Vm, label='Homozygous', color=clr, linewidth=0.5)
        else:
            axs.plot(t, Vm, label='Mutant', color=clr, linewidth=0.5)

        axs.locator_params(axis='x', nbins=5)
        axs.locator_params(axis='y', nbins=8)
        axs.set_title('Stimulation Plot', fontsize=8)
        axs.set_xlabel('Time (s)', fontsize=8)
        axs.set_ylabel('Membrane Voltage', fontsize=8)
        axs.legend(loc='best', fontsize=6, markerscale=2)

        # plt.show()
        # add_scalebar(axs)
        # file_path_to_save=f'{self.plot_folder}{plot_fn}.pdf' ##Commented 121323 prior to batch run TF
        # plt.savefig(file_path_to_save, format='pdf')

        return

    # Function for getting raw data from WT to superimpose under mut plots
    def get_stim_raw_data(self, stim_amp=0.5, dt=0.005, rec_extra=False, stim_dur=1600, sim_config={
        # changing to get different firing at different points along neuron TF 011624
        # 'section' : 'axon',
        # 'section_num' : 0,
        # 'segment' : 0,
        # 'currents'  :['ina','ica','ik'],
        # 'ionic_concentrations' :["cai", "ki", "nai"]
    }):

        ap_initiation = []
        ap_threshold = 10

        self.dt = dt
        self.l5mdl.init_stim(stim_dur=stim_dur, amp=stim_amp)
        if rec_extra:
            Vm, I, t, stim, extra_vms = self.l5mdl.run_sim_model(dt=dt, rec_extra=rec_extra,
                                                                 sim_config=sim_config)  # changed run_model to run_sim_model to capture other segments
            self.extra_vms = extra_vms
        else:
            Vm, I, t, stim, ionic = self.l5mdl.run_sim_model(dt=dt,
                                                             sim_config=sim_config)  # changed run_model to run_sim_model to capture other segments
            # Check each data point in Vm and append (Vm, t) to ap_initiation if above threshold

        # For finding first AP threshold
        # for i, v in enumerate(Vm):
        #     if v >= ap_threshold:
        #         ap_initiation.append((t[i],v))

        # print(f"The action potential initiation voltage and time are: {ap_initiation[0]}")
        return Vm, I, t, stim  # , ap_initiation

    def get_stim_raw_data_segments(self, stim_amp=0.5, dt=0.005, rec_extra=False, stim_dur=1600, sim_config=None):
        """
        Records voltage at multiple sections/segments specified in sim_config.
        sim_config should have keys 'section', 'section_num', and 'segment', each as a list.
        Returns: Vm_array (time x segment), I, t, stim

        Example call:
            sim_config = {
            'section': ['axon', 'axon', 'soma'],
            'section_num': [0, 1, 0],
            'segment': [0.1, 0.5, 0.9]
            }
            Vm_array, I, t, stim = simwt.get_stim_raw_data_segments(stim_amp=0.5, dt=0.005, stim_dur=500, sim_config=sim_config)
        """
        if sim_config is None:
            raise ValueError(
                "sim_config must be provided and contain lists for 'section', 'section_num', and 'segment'.")

        sections = sim_config.get('section', [])
        section_nums = sim_config.get('section_num', [])
        segments = sim_config.get('segment', [])
        if not (isinstance(sections, list) and isinstance(section_nums, list) and isinstance(segments, list)):
            raise ValueError("'section', 'section_num', and 'segment' in sim_config must be lists.")

        self.dt = dt
        self.l5mdl.init_stim(stim_dur=stim_dur, amp=stim_amp)

        t_vec = h.Vector()
        t_vec.record(h._ref_t)

        seg_refs = []
        for sec_name, sec_num, seg_x in zip(sections, section_nums, segments):
            try:
                sec = getattr(self.l5mdl.h.cell, sec_name)[sec_num]
            except Exception as e:
                print(f"Could not access section {sec_name}[{sec_num}]: {e}")
                continue
            seg = sec(seg_x)
            seg_refs.append(seg)

        volt_vecs = [h.Vector().record(seg._ref_v) for seg in seg_refs]

        h.finitialize(-65)
        h.continuerun(stim_dur)

        t = np.array(t_vec)
        Vm_array = np.array([np.array(v) for v in volt_vecs]).T  # shape: time x segment

        # For compatibility, run the original sim for I, stim
        Vm, I, t_orig, stim = self.get_stim_raw_data(stim_amp=stim_amp, dt=dt, rec_extra=rec_extra, stim_dur=stim_dur,
                                                     sim_config=sim_config)

        return Vm_array, I, t, stim

    def plot_stim_firstpeak(self, stim_amp=0.5, dt=0.02, clr='black', plot_fn='step', axs=None, rec_extra=False,
                            stim_start=30, stim_dur=500):
        self.dt = dt
        if not axs:
            fig, axs = plt.subplots(1, figsize=(cm_to_in(8), cm_to_in(7.8)))
        self.l5mdl.init_stim(stim_dur=stim_dur, amp=stim_amp, stim_start=stim_start)
        if rec_extra:
            Vm, I, t, stim, extra_vms = self.l5mdl.run_model(dt=dt, rec_extra=rec_extra)
            self.extra_vms = extra_vms
        else:
            Vm, I, t, stim = self.l5mdl.run_model(dt=dt)

        self.volt_soma = Vm
        self.I = I
        self.t = t
        self.stim = stim

        axs.plot(t[1:12500], Vm[1:12500], label='Vm', color=clr, linewidth=1)
        axs.locator_params(axis='x', nbins=5)
        axs.locator_params(axis='y', nbins=8)
        # plt.show()
        # add_scalebar(axs)
        file_path_to_save = f'{self.plot_folder}{plot_fn}.pdf'
        plt.savefig(file_path_to_save, format='pdf')
        return axs

    def plot_currents(self, stim_amp=0.5, dt=0.01, clr='black', plot_fn='step', axs=None, stim_dur=500):
        if not axs:
            fig, axs = plt.subplots(4, figsize=(cm_to_in(8), cm_to_in(30)))
        self.l5mdl.init_stim(stim_dur=stim_dur, amp=stim_amp, sweep_len=200)
        Vm, I, t, stim = self.l5mdl.run_model(dt=dt)
        axs[0].plot(t, Vm, label='Vm', color=clr, linewidth=1)
        axs[0].locator_params(axis='x', nbins=5)
        axs[0].locator_params(axis='y', nbins=8)

        axs[1].plot(t, I['Na'], label='Na', color='red')
        axs[2].plot(t, I['K'], label='K', color='black')
        axs[3].plot(t, I['Ca'], label='Ca', color='green')
        # add_scalebar(axs)
        file_path_to_save = f'{self.plot_folder}Ktrials2_{plot_fn}.pdf'
        plt.savefig(file_path_to_save + '.pdf', format='pdf', dpi=my_dpi)
        return axs

    def get_axonal_ks(self, start_Vm=-72, dt=0.1, rec_extra=False):
        h.dt = dt
        self.dt = dt
        h.finitialize(start_Vm)
        timesteps = int(h.tstop / h.dt)

        Vm = np.zeros(timesteps)
        I = {}
        I['Na'] = np.zeros(timesteps)
        I['K'] = np.zeros(timesteps)
        I['K31'] = np.zeros(timesteps)
        I['KT'] = np.zeros(timesteps)
        I['KCa'] = np.zeros(timesteps)
        I['KP'] = np.zeros(timesteps)
        stim = np.zeros(timesteps)
        t = np.zeros(timesteps)

        for i in range(timesteps):
            Vm[i] = h.cell.soma[0].v
            I['Na'][i] = self.l5mdl.ais(0.5).ina
            I['K'][i] = self.l5mdl.ais(0.5).ik
            I['K31'][i] = self.l5mdl.ais.gSKv3_1_SKv3_1
            I['KP'][i] = self.l5mdl.ais.gK_Pst_K_Pst
            I['KT'][i] = self.l5mdl.ais.gK_Tst_K_Tst
            I['KCa'][i] = self.l5mdl.ais.gSK_E2_SK_E2
            t[i] = i * h.dt / 1000
            stim[i] = h.st.amp
            h.fadvance()
        return Vm, I, t, stim

    def plot_axonal_ks(self, stim_amp=0.5, dt=0.01, clr='black', plot_fn='step_axon_ks', axs=None, stim_dur=500):
        if not axs:
            fig, axs = plt.subplots(7, 2, figsize=(cm_to_in(16), cm_to_in(70)))
        self.l5mdl.init_stim(stim_dur=stim_dur, amp=stim_amp, sweep_len=500)
        Vm, I, t, stim = self.get_axonal_ks(dt=dt)
        axs[0][0].plot(t, Vm, label='Vm', color=clr, linewidth=1)
        plot_dvdt_from_volts(Vm, self.dt, axs[0][1])
        axs[0][0].locator_params(axis='x', nbins=5)
        axs[0][0].locator_params(axis='y', nbins=8)

        axs[1][0].plot(t, I['Na'], label='Na', color='red')
        axs[1][0].legend()
        plot_dg_dt(I['Na'], Vm, self.dt, axs[1][1])
        axs[2][0].plot(t, I['K'], label='K', color='black')
        plot_dg_dt(I['K'], Vm, self.dt, axs[2][1])
        axs[2][0].legend()
        axs[3][0].plot(t, I['K31'], label='K31', color='green')
        plot_dg_dt(I['K31'], Vm, self.dt, axs[3][1])
        axs[3][0].legend()
        axs[4][0].plot(t, I['KP'], label='KP', color='orange')
        plot_dg_dt(I['KP'], Vm, self.dt, axs[4][1])
        axs[4][0].legend()
        axs[5][0].plot(t, I['KT'], label='KT', color='yellow')
        plot_dg_dt(I['KT'], Vm, self.dt, axs[5][1])
        axs[5][0].legend()
        axs[6][0].plot(t, I['KCa'], label='KCa', color='grey')
        plot_dg_dt(I['KCa'], Vm, self.dt, axs[6][1])
        axs[6][0].legend()

        # add_scalebar(axs)
        # file_path_to_save=plot_fn
        file_path_to_save = plot_fn
        plt.savefig(file_path_to_save, format='pdf', dpi=my_dpi)
        return axs

    def plot_fi_curve(self, start, end, nruns, wt_data=None, ax1=None, fig=None,
                      fn='ficurve'):  # start=0,end=0.6,nruns=14
        fis = get_fi_curve(self.l5mdl, start, end, nruns, dt=0.1, wt_data=wt_data, ax1=ax1, fig=fig,
                           fn=f'{self.plot_folder}{fn}.pdf')
        return fis

    def plot_volts_dvdt(self, stim_amp=0.5):
        fig_volts, axs_volts = plt.subplots(1, figsize=(cm_to_in(8), cm_to_in(7.8)))
        fig_dvdt, axs_dvdt = plt.subplots(1, figsize=(cm_to_in(8), cm_to_in(7.8)))
        self.plot_stim(axs=axs_volts, dt=0.02)
        plot_dvdt_from_volts(self.volt_soma, self.dt, axs_dvdt)
        file_path_to_save = f'{self.plot_folder}WT_volts_dvdt_{stim_amp}.pdf'
        fig_dvdt.savefig(file_path_to_save, format='pdf', dpi=my_dpi)
        file_path_to_save = f'{self.plot_folder}WT_volts_{stim_amp}.pdf'
        fig_volts.savefig(file_path_to_save, format='pdf', dpi=my_dpi)

    def get_ap_init_site(self):
        self.plot_stim(stim_amp=0.5, rec_extra=True)
        soma_spikes = get_spike_times(self.volt_soma, self.t)
        axon_spikes = get_spike_times(self.extra_vms['axon'], self.t)
        ais_spikes = get_spike_times(self.extra_vms['ais'], self.t)
        for i in range(len(soma_spikes)):
            print(f'spike #{i} soma - {soma_spikes[i]}, ais - {ais_spikes[i]}, axon - {axon_spikes[i]}')

    def get_spontaneous(self):
        fi_value = self.plot_fi_curve(start=0, end=0.1, nruns=1)
        # First spike time in (s), init_stim starts stimulation at 0.2s (200ms)
        if fi_value[0] == 0:
            return "NoSponAct"
        else:
            return "SponAct"

    ##_______________________Added to enable run of TTX and overexpression functions
    def plot_model_FI_Vs_dvdt(self, vs_amp, wt_Vm, wt_t, sim_config, fnpre='', wt_fi=None, wt2_data=None, start=0,
                              end=2, nruns=21, dt=0.005):  # wt2_data=None,

        wt_fi = [0, 0, 2, 6, 8, 10, 11, 12, 13, 14, 15, 15, 16, 17, 17, 18, 19, 19, 20, 20,
                 21]  ##TF072624 Roy's HH tuning best FI

        for curr_amp in vs_amp:  # vs_amp is list
            # fig_volts,axs = plt.subplots(2,figsize=(cm_to_in(3),cm_to_in(3.5)))
            # fig_volts,axs = plt.subplots(2,figsize=(cm_to_in(9),cm_to_in(10.5)))
            # axs[0] = self.plot_stim(axs = axs[0],stim_amp = curr_amp,dt=0.01)
            # #axs[0] = self.plot_stim(axs = axs[0],stim_amp = curr_amp,dt=0.05)
            # axs[1] = plot_dvdt_from_volts(self.volt_soma,self.dt,axs[1])
            # add_scalebar(axs[0])
            # add_scalebar(axs[1])
            # fn = f'{self.plot_folder}/{fnpre}dvdt_vs_{curr_amp}.pdf'
            # fig_volts.savefig(fn)
            # csv_volts = f'{self.plot_folder}/{fnpre}vs_{curr_amp}.csv'

            ###
            # self.plot_volts_dvdt(stim_amp = curr_amp)
            figures = []

            # figures.append(plt.figure())
            # fig_volts,axs = plt.subplots(2,figsize=(cm_to_in(8),cm_to_in(15)))
            # self.plot_stim(axs = axs[0],stim_amp = curr_amp,dt=0.005)
            # plot_dvdt_from_volts(self.volt_soma,self.dt,axs[1])
            # fn2 = f'{self.plot_folder}/{fnpre}{curr_amp}.pdf'
            # fig_volts.savefig(fn2)

            # fig_volts2,axs = plt.subplots(2,figsize=(cm_to_in(8),cm_to_in(15)))
            # self.plot_stim_firstpeak(axs = axs[0],stim_amp = curr_amp,dt=0.005)
            # plot_dvdt_from_volts_firstpeak(self.volt_soma,self.dt,axs[1])
            # fn3 = f'{self.plot_folder}/{fnpre}{curr_amp}_single.pdf'
            # fig_volts2.savefig(fn3)

            # Attempting wt and het on same plot
            fig_volts3, axs = plt.subplots(2, figsize=(cm_to_in(30), cm_to_in(15)))
            self.plot_wtvmut_stim(wt_Vm=wt_Vm, wt_t=wt_t, axs=axs[0], stim_amp=curr_amp, dt=dt, sim_config=sim_config)
            print(wt_Vm)
            print(len(wt_Vm))
            print(wt_t)
            print(len(wt_t))
            print(self.volt_soma)
            print(len(self.volt_soma))
            plot_dvdt_from_volts_wtvmut(self.volt_soma, wt_Vm, dt, axs[1])
            fn4 = f'{self.plot_folder}/{fnpre}{curr_amp}_wtvmut.pdf'
            fig_volts3.savefig(fn4)

            # plt.show()
            ###

            # with open(csv_volts, 'w', newline='') as file:
            #     writer = csv.writer(file)
            #     writer.writerow(['Voltage'])  # Write header row
            #     writer.writerows(zip(self.volt_soma))

        ###################
        self.plot_fi_curve_2line(start, end, nruns, wt_data=wt_fi, wt2_data=wt2_data,
                                 fn=fnpre + '_fi')  # add back wt2_data if want more lines
        ###################

        # fi_ans = self.plot_fi_curve_2line(start,end,nruns,wt_data = wt_fi,fn = fnpre + '_fi')
        # with open(f'{self.plot_folder}/{fnpre}.csv', 'w+', newline='') as myfile:
        #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        #     wr.writerow(fi_ans)
        # return fi_ans

    ##_________________________________________________________________________________________________
    def plot_fi_curve_2line(self, start, end, nruns, epochlabel='', wt_data=None, wt2_data=None, ax1=None, fig=None,
                            fn='ficurve'):  # start=0,end=0.6,nruns=14 (change wt_data from None to add WT line), add in wt2_data for another line
        fis = get_fi_curve(self.l5mdl, start, end, nruns, dt=0.1, wt_data=wt_data, wt2_data=wt2_data, ax1=ax1, fig=fig,
                           fn=f'{self.plot_folder}/{fn}.pdf', epochlabel=epochlabel)  # add in wt2_data for another line
        print(fis)
        with open(f'{self.plot_folder}/{fn}-FI-list.txt', 'w') as file:
            file.write(','.join(str(fi) for fi in fis))
        file.close()
        # fi_df = pd.DataFrame(fis)
        # fi_df.to_csv(f'{self.plot_folder}/{fn}-FI_raw.csv')
        return fis

    def wtvsmut_stim_dvdt(self, vs_amp, wt_Vm, wt_t, sim_config, het_Vm=None, het_t=None, fnpre='', dt=0.005,
                          stim_dur=500, clr='red'):  ##TF111524 added stim_dur
        for curr_amp in vs_amp:
            figures = []

            # Attempting wt and het on same plot
            fig_volts3, axs = plt.subplots(2, figsize=(cm_to_in(15), cm_to_in(22.5)),
                                           gridspec_kw={'height_ratios': [1, 2]})
            self.plot_wtvmut_stim(wt_Vm=wt_Vm, wt_t=wt_t, axs=axs[0], stim_amp=curr_amp, dt=dt, sim_config=sim_config,
                                  het_Vm=het_Vm, het_t=het_t, stim_dur=stim_dur, clr=clr)
            # Set fixed axes for the dvdt plot
            axs[0].set_ylim(-80, 60)

            print(wt_Vm)
            print(len(wt_Vm))
            print(wt_t)
            print(len(wt_t))
            print(self.volt_soma)
            print(len(self.volt_soma))
            plot_dvdt_from_volts_wtvmut(self.volt_soma, wt_Vm, dt, axs[1], het_Vm=het_Vm, clr=clr)

            # Set fixed axes for the dvdt plot
            axs[1].set_ylim(-200, 1000)
            axs[1].set_xlim(-80, 60)

            fn4 = f'{self.plot_folder}/{fnpre}_{curr_amp}_wtvmut.pdf'
            plt.tight_layout(pad=2.0)  # Adjust the padding
            fig_volts3.savefig(fn4)

    ##TF022924 Ghazaleh's documentation code below, adding to class to call by sim = Na12HMMModel_TF.Na12Model_TF.save2text(self)
    def save2text(ais_nav12_fac=None,
                  ais_nav16_fac=None,
                  nav12=None,
                  nav16=None,
                  nav12name=None,
                  mutname=None,
                  nav16name=None,
                  na12mechs=None,
                  na16mut_name=None,
                  na16mechs=None,
                  params_folder=None,
                  plots_folder=None,
                  ):

        # Create the directory if it doesn't exist
        directory = "Documentation"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Create the text file name with the current date and the value of the mutant variable
        current_date = datetime.date.today().strftime("%d_%m_%Y")
        text_file_name = f"runNa12HMMTF_{current_date}.txt"
        text_file_path = os.path.join(directory, text_file_name)

        # Write the variable documentation to the text file
        with open(text_file_path, "w") as text_file:
            text_file.write(f"ais_nav12_fac: {ais_nav12_fac}\n") if ais_nav12_fac is not None else None
            text_file.write(f"ais_nav16_fac: {ais_nav16_fac}\n") if ais_nav16_fac is not None else None
            text_file.write(f"nav12: {nav12}\n") if nav12 is not None else None
            text_file.write(f"nav16: {nav16}\n") if nav16 is not None else None
            text_file.write(f"nav12name: {nav12name}\n") if nav12name is not None else None
            text_file.write(f"mutname: {mutname}\n") if mutname is not None else None
            text_file.write(f"nav16name: {nav16name}\n") if nav16name is not None else None
            text_file.write(f"na16mut_name: {na16mut_name}\n") if na16mut_name is not None else None
            text_file.write(f"na12mechs: {na12mechs}\n") if na12mechs is not None else None
            text_file.write(f"na16mechs: {na16mechs}\n") if na16mechs is not None else None
            text_file.write(f"params_folder: {params_folder}\n") if params_folder is not None else None
            text_file.write(f"plots_folder: {plots_folder}\n") if plots_folder is not None else None

        # save2text(weights, best_hof, evaluator.init_WT, evaluator.mutant_data, channel_name,csv_file, mutant, cp_file, wild_type_params,objective_names)


####____________________Overexpression and TTX code from Roy's M1TTPC branch from 16HMMtau.py
def overexp(na12name, mut_name, plots_folder, wt_fac, mut_fac, mutTXT=None, plot_wt=True, fnpre='100WT20G1625R',
            axon_KP=1,
            na12mechs=['na12', 'na12_mut'], params_folder='./params/na12HMM_HOF_params/'):
    sim = Na12Model_TF(nav16=wt_fac, KP=axon_KP, na12name=na12name, mut_namet=mut_name, plots_folder=plots_folder,
                       params_folder=params_folder, na12mechs=na12mechs)
    if plot_wt:
        wt_fi = sim.plot_model_FI_Vs_dvdt([0.5, 1, 2],
                                          fnpre=f'{fnpre}_FI_')  # Even if change mut_fac/wt_fac, will use old na16mut mech params since mut not updated
        # wt_fi = sim.plot_model_FI_Vs_dvdt([0.3,0.5,1,1.5,2,2.5,3],fnpre=f'{fnpre}_FI_')
    else:
        wt_fi = []
    print(f'wt_fi is {wt_fi}')
    if mut_fac:
        sim.make_mut(na12mechs[1],
                     f'{params_folder}{mutTXT}')  # updates mech (Arg[1]) with new mod params dict (Arg[2])
        print('making mut')
        update_mod_param(sim.l5mdl, ['na16mut'], mut_fac)  # Adds multiplier to updated mod/mech parameters
        print('updated mod params')
        sim.l5mdl.h.finitialize()
        if plot_wt:
            sim.plot_model_FI_Vs_dvdt([0.5, 1, 2], wt_fi=wt_fi, fnpre=f'{fnpre}mutX{mut_fac}_')
            # sim.plot_model_FI_Vs_dvdt([0.3,0.5,1,1.5,2],wt_fi = wt_fi,fnpre=f'{fnpre}mutX{mut_fac}_')

        else:
            # sim.plot_model_FI_Vs_dvdt([0.3,0.5,1,1.5,2],fnpre=f'{fnpre}mutX{mut_fac}_')
            sim.plot_model_FI_Vs_dvdt([0.5, 1, 2], fnpre=f'{fnpre}mutXtest{mut_fac}_')

    else:
        # sim.plot_model_FI_Vs_dvdt([0.3,0.5,1,1.5,2],fnpre=f'{fnpre}_{mut_fac}_')
        ##sim.plot_model_FI_Vs_dvdt([0.5,1],fnpre=f'{fnpre}_{mut_fac}_else')
        return


def ttx(na16name, na16mut, plots_folder, wt_factor, mut_factor, fnpre='mut_TTX', axon_KP=1):
    sim = Na12Model_TF(KP=axon_KP, nav12=0, na16name=na16name, na16mut=na16mut, plots_folder=plots_folder)
    # if mut_factor>0:
    #     sim.make_mut('na16mut','na16mut44_092623.txt')
    update_mod_param(sim.l5mdl, ['na16'], wt_factor)
    update_mod_param(sim.l5mdl, ['na16mut'], mut_factor)
    update_mod_param(sim.l5mdl, ['na12', 'na12mut'], 0, print_flg=True)

    # make_currentscape_plot(fn_pre=fnpre,sim_obj = sim.l5mdl)
    # sim.plot_model_FI_Vs_dvdt([0.3,0.5,1,1.5,2],fnpre=f'{fnpre}WT_{wt_factor*100}_Mut_{mut_factor *100}_')
    sim.plot_model_FI_Vs_dvdt([1],
                              fnpre=f'{fnpre}WT_{wt_factor * 100}_Mut_{mut_factor * 100}_')  # only plot 1nA rather than range of amps


####____________________________________________________________________________________________


# Scanning Code below for fine tuning
###########################################################################################################
###########################################################################################################
###########################################################################################################


def scan_sec_na():
    for fac in np.arange(0.1, 1, 0.1):
        sim = Na12Model_TF(soma_na16=fac, soma_na12=fac)
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(8), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.5, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/Na16_{fac}_Na12_{fac}.pdf'
        fig_volts.savefig(fn)
        """
        sim = Na12Model_TF(soma_na12=fac)
        fig_volts,axs = plt.subplots(2,figsize=(cm_to_in(8),cm_to_in(15)))
        sim.plot_stim(axs = axs[0],stim_amp = 0.5,dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma,sim.dt,axs[1])
        fn = f'{sim.plot_folder}/Na12_{fac}.pdf'
        fig_volts.savefig(fn)

        sim = Na12Model_TF(node_na=fac)
        fig_volts,axs = plt.subplots(2,figsize=(cm_to_in(8),cm_to_in(15)))
        sim.plot_stim(axs = axs[0],stim_amp = 0.5,dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma,sim.dt,axs[1])
        fn = f'{sim.plot_folder}/node_na_{fac}.pdf'
        fig_volts.savefig(fn)
        """


def scan12_16():
    i12 = .25
    # for i12 in np.arange(.25,1,0.25):
    for i16 in np.arange(1.8, 2.5, 0.1):
        sim = Na12Model_TF(nav12=i12, nav16=i16)
        # sim.make_wt()
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(8), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.5, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/12_{i12}_16_{i16}.pdf'
        fig_volts.savefig(fn)


def scanK():
    for i in np.arange(0.2, 2, .4):  # (.1,5,.5)

        sim = Na12Model_TF(ais_ca=i)
        # sim.make_wt()
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(10), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.1, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/ais_CA_{i}_.pdf'
        fig_volts.savefig(fn)

        sim = Na12Model_TF(ais_Kca=i)
        # sim.make_wt()
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(10), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.1, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/ais_Kca_{i}_.pdf'
        fig_volts.savefig(fn)

        sim = Na12Model_TF(K=i)
        # sim.make_wt()
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(9.5), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.1, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/K_{i}_.pdf'
        fig_volts.savefig(fn)

        sim = Na12Model_TF(somaK=i)
        # sim.make_wt()
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(9.5), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.1, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/somaK_{i}_.pdf'
        fig_volts.savefig(fn)

        sim = Na12Model_TF(KP=i)
        # sim.make_wt()
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(9), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.1, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/Kp_{i}_.pdf'
        fig_volts.savefig(fn)

        sim = Na12Model_TF(KT=i)
        # sim.make_wt()
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(10), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.1, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/Kt_{i}_.pdf'
        fig_volts.savefig(fn)


def scanKv31():
    vtau_orig = 18.700
    vinf_orig = -46.560
    for i in np.arange(0, 21, 5):
        sim = Na12Model_TF()
        update_param_value(sim.l5mdl, ['SKv3_1'], 'vtau', vtau_orig + i)
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(9.5), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.5, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/kv31_shift_vtau_{i}_.pdf'
        fig_volts.savefig(fn)
        update_param_value(sim.l5mdl, ['SKv3_1'], 'vtau', vtau_orig)

        sim = Na12Model_TF()
        update_param_value(sim.l5mdl, ['SKv3_1'], 'vinf', vinf_orig + i)
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(9.5), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.5, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/kv31_shift_vinf_{i}_.pdf'
        fig_volts.savefig(fn)
        update_param_value(sim.l5mdl, ['SKv3_1'], 'vinf', vinf_orig)
    mtaumul_orig = 4
    for i in np.arange(0.1, 1, 0.2):
        sim = Na12Model_TF()
        update_param_value(sim.l5mdl, ['SKv3_1'], 'mtaumul', mtaumul_orig + i)
        fn = f'{sim.plot_folder}/kv31_shift_mtaumul_{i}_.pdf'
        sim.plot_axonal_ks(plot_fn=fn)
    update_param_value(sim.l5mdl, ['SKv3_1'], 'mtaumul', mtaumul_orig)


def scanKT():
    vshift_orig = -10
    for i in np.arange(10, 31, 10):
        sim = Na12Model_TF()
        update_param_value(sim.l5mdl, ['K_Tst'], 'vshift', vshift_orig + i)
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(9.5), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.5, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/kT_vshift_{i}_.pdf'
        fig_volts.savefig(fn)
    update_param_value(sim.l5mdl, ['K_Tst'], 'vshift', vshift_orig)


def test_params():
    for i in range(1, 9):
        na16_name = f'na16WT{i}'
        sim = Na12Model_TF(na16name=na16_name)
        sim.plot_currents()
        fig_volts, axs = plt.subplots(2, figsize=(cm_to_in(9.5), cm_to_in(15)))
        sim.plot_stim(axs=axs[0], stim_amp=0.5, dt=0.005)
        plot_dvdt_from_volts(sim.volt_soma, sim.dt, axs[1])
        fn = f'{sim.plot_folder}/default_na16_{i}.pdf'
        fig_volts.savefig(fn)


def default_model(al1='na12_orig1', al2='na12_orig1', typ=''):
    sim = Na12Model_TF(al1, al2)
    # sim.plot_currents()
    fig_volts, axs = plt.subplots(1, figsize=(cm_to_in(16), cm_to_in(16)))
    sim.plot_stim(axs=axs, stim_amp=0.7, dt=0.005, stim_dur=500)
    axs.set_title(f'{al2}_{typ}')
    # plot_dvdt_from_volts(sim.volt_soma,sim.dt,axs[1])
    fn = f'{sim.plot_folder}/default_na12HMM_{typ}.pdf'
    fig_volts.savefig(fn)


# The combination of two bellow Plots dvdt of allele combinations on top of each other and safe as file compare.pdf
# give the WT and Mutant param file as input, al1 is for WT
# yu don't need to run default anymore

def dvdt_all(al1='na12_orig1', al2='na12_R850P_5may', stim_amp=0.5, Typ=None, stim_dur=500):  # stim_amp = 0.5 #nA
    sim = Na12Model_TF(al1, al2)

    if al1 == al2 and al1 == 'na12_orig1':
        Typ = 'WT'
    elif al1 == al2:
        Typ = 'Hom'
    else:
        Typ = 'Het'

    fig_volts, axs = plt.subplots(1, figsize=(cm_to_in(16), cm_to_in(16)))
    sim.plot_stim(axs=axs, stim_amp=stim_amp, dt=0.005, stim_dur=stim_dur)
    axs.set_title(f'stim: {stim_amp}nA for {stim_dur}ms , al1: {al1}, al2: {al2}', fontsize=9)
    fn = f'{sim.plot_folder}{Typ}_{stim_amp}_{stim_dur}.pdf'
    fig_volts.savefig(fn)
    dvdt = np.gradient(sim.volt_soma) / sim.dt
    v = sim.volt_soma
    return v, dvdt


def dvdt_all_plot(al1='na12_orig1', al2='na12_R850P_5may', stim_amp=0.5, stim_dur=500):
    volt = [[], [], []]
    dvdts = [[], [], []]
    volt[0], dvdts[0] = dvdt_all(al2, al2, stim_amp=stim_amp, stim_dur=stim_dur)  # Homozygous
    volt[1], dvdts[1] = dvdt_all(al1, al2, stim_amp=stim_amp, stim_dur=stim_dur)  # Heterozygous
    volt[2], dvdts[2] = dvdt_all(al1, al1, stim_amp=stim_amp, stim_dur=stim_dur)  # WT
    fig_volts, axs = plt.subplots(1, figsize=(cm_to_in(17), cm_to_in(17)))
    axs.plot(volt[0], dvdts[0], 'g', label=f'Homozygous')
    axs.plot(volt[1], dvdts[1], 'b', label=f'Heterozygous')
    axs.plot(volt[2], dvdts[2], 'r', label=f'WT')

    axs.set_xlabel('voltage(mV)', fontsize=9)
    axs.set_ylabel('dVdt(mV/s)', fontsize=9)
    axs.set_title(f'stim {stim_amp}, al1: {al1}, al2: {al2}', fontsize=9)
    axs.legend()
    fn = f'./Plots/Tim/{al2}_{stim_amp}_{stim_dur}.pdf'
    fig_volts.savefig(fn)


# sim = Na12Model_TF('na12_orig1', 'na12_orig1')
# sim.plot_currents()
# sim.get_ap_init_site()
# scan_sec_na()
# update_param_value(sim.l5mdl,['SKv3_1'],'mtaumul',1)
# sim.plot_volts_dvdt()
# sim.plot_fi_curve(0,1,10)
# default_model(al1 = 'na12_orig1',al2 = 'na12_orig1',typ='WT')
# scanK()
# scanKT()
# scanKv31()
# scan12_16()
##plot_mutant(na12name = 'na12_R850P',mut_name= 'na12_R850P')
# sim.plot_axonal_ks()
"""
for i in range (6,12):
    for j in range (1,3):
        dvdt_all_plot(al1 = 'na12_orig1', al2= 'na12_R850P_5may', stim_amp=i*0.05,  stim_dur = j* 500 )

for i in range (6,12):
    for j in range (1,3):
        dvdt_all_plot(al1 = 'na12_orig1', al2= 'na12_R850P_old', stim_amp=i*0.05,  stim_dur = j* 500 )

for i in range (6,12):
    for j in range (1,3):
        dvdt_all_plot(al1 = 'na12_orig1', al2= 'R850P', stim_amp=i*0.05,  stim_dur = j* 500 )
"""

# dvdt_all_plot(al1 = 'na12_orig1', al2= 'na12_R850P_old', stim_amp=0.7,  stim_dur = 500 )
# dvdt_all_plot(al1 = 'na12_orig1', al2= 'na12_R850P_5may', stim_amp=0.7,  stim_dur = 500 )