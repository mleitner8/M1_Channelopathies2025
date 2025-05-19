# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 21:07:44 2021

@author: bensr
"""
import argparse
import numpy as np
# from vm_plotter import *
from neuron import h
import os
import csv
import sys
import pandas as pd
import matplotlib.pyplot as plt
from NrnHelper import *


class NeuronModel:
    def __init__(self, ais_nav16_fac, ais_nav12_fac, mod_dir='../cells/Neuron_Model_12HH16HH/',
                 # './Neuron_Model_12HH16HH/',#'./Neuron_Model_HH/',

                 update=True,
                 ##TF If this is true, mechs are updated with update_mech_from_dict. Turn to false if you don't want update ### maybe not working???????
                 na12name='na12annaTFHH2',
                 na12mut_name='na12annaTFHH2',  ## TF041525 this is same as na12name since we want homozygous WT
                 na12mechs=['na12', 'na12mut'],
                 na16name='na16HH_TF2',
                 na16mut_name='na16HH_TF2',  ## TF041525 this is same as na16name since we want homozygous WT
                 na16mechs=['na16', 'na16mut'],
                 params_folder='./Neuron_Model_12HH16HH/params/',

                 nav12=1,
                 nav16=1,
                 dend_nav12=1,
                 soma_nav12=1,
                 dend_nav16=1,
                 soma_nav16=1,
                 ais_nav12=1,
                 ais_nav16=1,
                 ais_ca=1,
                 ais_KCa=1,
                 axon_Kp=1,
                 axon_Kt=1,
                 axon_K=1,
                 axon_Kca=1,
                 axon_HVA=1,
                 axon_LVA=1,
                 node_na=1,
                 soma_K=1,
                 dend_K=1,
                 gpas_all=1,
                 fac=None
                 ):
        run_dir = os.getcwd()

        os.chdir(mod_dir)
        self.h = h  # NEURON h
        print(f'running model at {os.getcwd()} run dir is {run_dir}')
        print(f'There is {nav16} of WT nav16')
        print(f'There is {nav12} of WT nav12')
        h.load_file("runModel.hoc")

        self.soma_ref = h.root.sec
        self.soma = h.secname(sec=self.soma_ref)
        self.sl = h.SectionList()
        self.sl.wholetree(sec=self.soma_ref)
        self.nexus = h.cell.apic[66]
        self.dist_dend = h.cell.apic[91]
        self.ais = h.cell.axon[0]
        self.axon_proper = h.cell.axon[1]

        h.dend_na12 = 2.48E-03 * dend_nav12
        h.dend_na16 = 0
        h.dend_k = 0.0043685576 * dend_K
        h.soma_na12 = 3.24E-02 * soma_nav12
        h.soma_na16 = 7.88E-02 * soma_nav16
        h.soma_K = 0.21330453 * soma_K
        h.ais_na16 = ais_nav16_fac * ais_nav16
        h.ais_na12 = ais_nav12_fac * ais_nav12
        h.ais_ca = 0.0010125926 * ais_ca
        h.ais_KCa = 0.0009423347 * ais_KCa
        h.node_na = 0.9934221 * node_na
        h.axon_KP = 0.43260124 * axon_Kp
        h.axon_KT = 1.38801 * axon_Kt
        h.axon_K = 0.89699364 * 2.1 * axon_K
        h.axon_LVA = 0.00034828275 * axon_LVA
        h.axon_HVA = 1.05E-05 * axon_HVA
        h.axon_KCA = 0.4008224 * axon_Kca
        h.gpas_all = 1.34E-05 * gpas_all
        h.cm_all = 1.6171424
        # added gpas to see if i_pas changes on currentscape
        # h.gpas_all = .001

        h.dend_na12 = h.dend_na12 * nav12 * dend_nav12
        h.soma_na12 = h.soma_na12 * nav12 * soma_nav12

        if nav12 != 0:
            h.ais_na12 = (h.ais_na12 * ais_nav12) / nav12  ##TF020624 decouple ais Nav1.2 from overall nav12
        else:
            h.ais_na12 = h.ais_na12 * ais_nav12

        if nav16 != 0:
            h.ais_na16 = (h.ais_na16 * ais_nav16) / nav16  ##TF020624 decouple ais Nav1.6 from overall nav16
        else:
            h.ais_na12 = h.ais_na16 * ais_nav16

        h.dend_na16 = h.dend_na16 * nav16 * dend_nav16
        h.soma_na16 = h.soma_na16 * nav16 * soma_nav16

        h.working()

        os.chdir(run_dir)

        #############################################################
        ##Add update_mech_from_dict and update_param_value here #####
        ##TF052124 need to comment out update_mech_from_dict if using HH model -- Fixed this issue##
        if update:
            print("UPDATING ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print(eval('h.psection()'))
            # print(eval('h.cell.axon[0].psection()'))
            update_param_value(self, ['SKv3_1'], 'mtaumul', 6)  ##TF041924 ORIGINAL val=6
            multiply_param(self, ['SKv3_1'], 'mtaumul', 0.85)  ##TF083024 updated for hh model

            self.na12wt_mech = [na12mechs[0]]
            self.na12mut_mech = [na12mechs[1]]

            self.na16wt_mech = [na16mechs[0]]  ##TF021424 adding ability to update na16 (HH, shifted HH etc.)
            self.na16mut_mech = [na16mechs[1]]  ##TF021424 adding ability to update na16 (HH, shifted HH etc.)
            self.na16mechs = na16mechs

            self.h.working()
            p_fn_na12 = f'{params_folder}{na12name}.txt'
            p_fn_na12_mech = f'{params_folder}{na12mut_name}.txt'
            print(f'using wt_file params {na12name}')
            self.na12_p = update_mech_from_dict(self, p_fn_na12, self.na12wt_mech)  ###
            print(eval("h.psection()"))
            print(f'using mut_file params {na12mut_name}')
            self.na12_pmech = update_mech_from_dict(self, p_fn_na12_mech,
                                                    self.na12mut_mech)  # update_mech_from_dict(mdl,dict_fn,mechs,input_dict = False) 2nd arg (dict) updates 3rd (mech) ###
            print(eval("h.psection()"))

            # Updates gbar in na12 and na12mut mechs with value in nav12. Updates all gbars in all sections including all segments in AIS
            update_mod_param(self, ['na12', 'na12mut'], nav12)

            # h.load_file("/global/homes/t/tfenton/Neuron_general-2/Neuron_Model_12HMM16HH/printSh.hoc")
            # h.printVals12HHWT()

            # Adding ability to update with new Na16 mechs ##TF021424
            p_fn_na16 = f'{params_folder}{na16name}.txt'
            p_fn_na16_mech = f'{params_folder}{na16mut_name}.txt'

            print(f'using na16wt_file params {na16name}')
            self.na16_p = update_mech_from_dict(self, p_fn_na16, self.na16wt_mech)  ###
            print(eval("h.psection()"))
            ##TF030624 Can load file below and run h.printValsWT to debug if mod file is getting updated or not
            # h.load_file("/global/homes/t/tfenton/Neuron_general-2/Neuron_Model_12HMM16HH/printSh.hoc")
            # h.printValsWT16()

            print(f'using na16mut_file params {na16mut_name}')
            self.na16_pmech = update_mech_from_dict(self, p_fn_na16_mech, self.na16mut_mech)  ###
            print(eval("h.psection()"))

            update_mod_param(self, ['na16', 'na16mut'], nav16)

            print(eval("h.psection()"))

    # Function for determining and plotting the distribution of Na channels in axon.
    def chandensities(
            name=f"/global/homes/t/tfenton/Neuron_general-2/Plots/12HMM16HH_TF/ManuscriptFigs/Restart030824/4-FixModMistake_HH/22-changeIh"):
        distances = []
        na12_densities = []
        na16_densities = []
        na12mut_densities = []
        na16mut_densities = []
        sections = []

        for sec in h.cell.axon:
            for seg in sec:
                print(seg)
                section = f'h.distance.{seg}'
                distance = h.distance(0, seg)
                print(f'Distance_SEG{distance}')
                distances.append(distance)
                sections.append(section)

                na12_gbar = seg.gbar_na12
                print(na12_gbar)
                na12_densities.append(na12_gbar)

                na16_gbar = seg.gbar_na16
                print(na16_gbar)
                na16_densities.append(na16_gbar)

                na12mut_gbar = seg.gbar_na12mut
                na12mut_densities.append(na12mut_gbar)

                na16mut_gbar = seg.gbar_na16mut
                na16mut_densities.append(na16mut_gbar)

        print(distances)
        print(na12_densities)
        print(na16_densities)

        # Save data to dataframes to write to csv.
        df1 = pd.DataFrame(distances)
        df2 = pd.DataFrame(na12_densities)
        df3 = pd.DataFrame(na16_densities)
        df4 = pd.DataFrame(na12mut_densities)
        df5 = pd.DataFrame(na16mut_densities)
        df6 = pd.DataFrame(sections)
        df = pd.concat([df1, df2, df4, df3, df5, df6], axis=1,
                       keys=['Distance', 'na12', 'na12mut', 'na16', 'na16mut', 'sections'])
        # df.to_csv(name+'.csv')

        # Plot line graph of different contributions
        fig1, ax = plt.subplots()
        plt.plot(df['na12'], label='Nav12', color='blue')
        plt.plot(df['na12mut'], label='Nav12_Mut', color='cyan', linestyle='dashed')
        plt.plot(df['na16'], label='Nav16', color='red')
        plt.plot(df['na16mut'], label='Nav16_Mut', color='orange', alpha=0.5, linestyle='dashed')
        plt.legend()
        plt.xticks(range(1, len(distances)), rotation=270)
        plt.xlabel('Segment of Axon')
        plt.ylabel('gbar')
        plt.title("Distribution of Nav12 and Nav16")
        plt.savefig(name + ".png", dpi=400)

    # def init_stim(self, sweep_len = 800, stim_start = 30, stim_dur = 500, amp = 0.3, dt = 0.1): #Na16 zoom into single peak args
    # def init_stim(self, sweep_len = 800, stim_start = 100, stim_dur = 500, amp = 0.3, dt = 0.1): ##TF050924 Changed to default for HH figs for grant 061424 ##This is a good new setting
    # def init_stim(self, sweep_len = 200, stim_start = 30, stim_dur = 100, amp = 0.3, dt = 0.1): ##TF060724 Using to get AP initiation/propogation to simulate less
    # def init_stim(self, sweep_len = 60, stim_start = 30, stim_dur = 100, amp = 0.3, dt = 0.1): ##TF061424 getting single AP for SFARI grant
    # def init_stim(self, sweep_len = 150, stim_start = 30, stim_dur = 120, amp = 0.3, dt = 0.1): ##TF071524 getting 1-3 APs for Roy

    # def init_stim(self, sweep_len = 300, stim_start = 30, stim_dur = 200, amp = 0.3, dt = 0.1): ##TF071524 getting 1-3 APs for Roy
    # def init_stim(self, sweep_len = 800, stim_start = 100, stim_dur = 500, amp = 0.3, dt = 0.1):
    # def init_stim(self, sweep_len = 800, stim_start = 100, stim_dur = 500, amp = -0.4, dt = 0.1): #HCN hyperpolarizing
    # def init_stim(self, sweep_len = 800, stim_start = 200, stim_dur = 500, amp = -0.4, dt = 0.1): #HCN Kevin request #2
    # def init_stim(self, sweep_len = 1000, stim_start = 100, stim_dur = 700, amp = 0.3, dt = 0.1):
    def init_stim(self, sweep_len=2000, stim_start=100, stim_dur=1700, amp=0.3, dt=0.1):

        # updates the stimulation params used by the model
        # time values are in ms
        # amp values are in nA

        h("st.del = " + str(stim_start))
        h("st.dur = " + str(stim_dur))
        h("st.amp = " + str(amp))
        h.tstop = sweep_len
        h.dt = dt

    def start_stim(self, tstop=800, start_Vm=-72):
        h.finitialize(start_Vm)
        h.tstop = tstop

    def run_model2(self, stim_start=100, stim_dur=0.2, amp=0.3, dt=0.1,
                   rec_extra=False):  # works in combinition with stim_start for working with physiological stimultion
        h.dt = dt
        h("st.del = " + str(stim_start))
        h("st.dur = " + str(stim_dur))
        h("st.amp = " + str(amp))
        timesteps = int(stim_dur / h.dt)  # changed from h.tstop to stim_dur
        Vm = np.zeros(timesteps)
        I = {}
        I['Na'] = np.zeros(timesteps)
        I['Ca'] = np.zeros(timesteps)
        I['K'] = np.zeros(timesteps)
        stim = np.zeros(timesteps)
        t = np.zeros(timesteps)
        if rec_extra:
            extra_Vms = {}
            extra_Vms['ais'] = np.zeros(timesteps)
            extra_Vms['nexus'] = np.zeros(timesteps)
            extra_Vms['dist_dend'] = np.zeros(timesteps)
            extra_Vms['axon'] = np.zeros(timesteps)

        for i in range(timesteps):
            Vm[i] = h.cell.soma[0].v
            I['Na'][i] = h.cell.soma[0](0.5).ina
            I['Ca'][i] = h.cell.soma[0](0.5).ica
            I['K'][i] = h.cell.soma[0](0.5).ik
            stim[i] = h.st.amp
            t[i] = (
                               stim_start + i * h.dt) / 1000  # after each run_modl2 call, the stim_start is updated to the current time
            if rec_extra:
                nseg = int(self.h.L / 10) * 2 + 1  # create 19 segments from this axon section
                ais_end = 10 / nseg  # specify the end of the AIS as halfway down this section
                ais_mid = 4 / nseg  # specify the middle of the AIS as 1/5 of this section
                extra_Vms['ais'][i] = self.ais(ais_mid).v
                extra_Vms['nexus'][i] = self.nexus(0.5).v
                extra_Vms['dist_dend'][i] = self.dist_dend(0.5).v
                extra_Vms['axon'][i] = self.axon_proper(0.5).v
            h.fadvance()
        if rec_extra:
            return Vm, I, t, stim, extra_Vms
        else:
            return Vm, I, t, stim

    def run_model(self, start_Vm=-72, dt=0.1, rec_extra=False):
        h.dt = dt
        h.finitialize(start_Vm)
        timesteps = int(h.tstop / h.dt)  # change later to h.tstop

        Vm = np.zeros(timesteps)
        I = {}
        I['Na'] = np.zeros(timesteps)
        I['Ca'] = np.zeros(timesteps)
        I['K'] = np.zeros(timesteps)
        stim = np.zeros(timesteps)
        t = np.zeros(timesteps)
        if rec_extra:
            extra_Vms = {}
            extra_Vms['ais'] = np.zeros(timesteps)
            extra_Vms['nexus'] = np.zeros(timesteps)
            extra_Vms['dist_dend'] = np.zeros(timesteps)
            extra_Vms['axon'] = np.zeros(timesteps)

        for i in range(timesteps):
            Vm[i] = h.cell.soma[0].v
            I['Na'][i] = h.cell.soma[0](0.5).ina
            I['Ca'][i] = h.cell.soma[0](0.5).ica
            I['K'][i] = h.cell.soma[0](0.5).ik
            stim[i] = h.st.amp
            t[i] = i * h.dt / 1000
            if rec_extra:
                nseg = int(self.h.L / 10) * 2 + 1  # create 19 segments from this axon section
                ais_end = 10 / nseg  # specify the end of the AIS as halfway down this section
                ais_mid = 4 / nseg  # specify the middle of the AIS as 1/5 of this section
                extra_Vms['ais'][i] = self.ais(ais_mid).v
                extra_Vms['nexus'][i] = self.nexus(0.5).v
                extra_Vms['dist_dend'][i] = self.dist_dend(0.5).v
                extra_Vms['axon'][i] = self.axon_proper(0.5).v
            h.fadvance()
        if rec_extra:
            return Vm, I, t, stim, extra_Vms
        else:
            return Vm, I, t, stim

    def run_sim_model(self, start_Vm=-72, dt=0.1, sim_config={
        # changing to get different firing at different points along neuron TF 011624
        'section': 'soma',
        'segment': 0.5,
        'section_num': 0,
        'currents': ['ina', 'ica', 'ik'],
        'ionic_concentrations': ["cai", "ki", "nai"]
    }):

        """
        Runs a simulation model and returns voltage, current, time, and stimulation data.

        Args:
            start_Vm (float): Initial membrane potential (default: -72 mV).
            dt (float): Time step size for the simulation (default: 0.1 ms).
            sim_config (dict): Configuration dictionary for simulation parameters (default: see below).

        Returns:
            Vm (ndarray): Recorded membrane voltages over time.
            I (dict): Current traces for different current types.
            t (ndarray): Time points corresponding to the recorded data.
            stim (ndarray): Stimulation amplitudes over time.

        Description:
            This function runs a simulation model and records the membrane voltage, current traces, time points,
            and stimulation amplitudes over time. The simulation model is configured using the provided parameters.

        Default Simulation Configuration:
            'section': 'soma'
            'segment': 0.5
            'section_num' : 0
            'currents'  :['ina','ica','ik'],
            'ionic_concentrations' :["cai", "ki", "nai"]

        #Section: axon, section_num:0, segment:0 == AIS
        #Section: dend, section_num: 70, segment: 0.5 == Basal dendrite mid-shaft ***should check this in gui
        #Section: apic, section_num:77, segment:0       77(0) or 66(1)  == Apical Nexus
        #Section: apic, section_num:90, segment:0.5   == Most distal apical dendrite

        Example Usage:
            Vm, I, t, stim = run_sim_model(start_Vm=-70, dt=0.05, sim_config={
                'section': 'soma',
                'section_num' : 0,
                'segment': 0.5,
                'currents'  :['ina','ica','ik'],
                'ionic_concentrations' :["cai", "ki", "nai"]
            })
        """

        h.dt = dt
        h.finitialize(start_Vm)
        timesteps = int(h.tstop / h.dt)
        # initialise to zeros,
        # current_types = list(set(sim_config['inward'] + sim_config['outward']))
        current_types = sim_config['currents']
        ionic_types = sim_config['ionic_concentrations']
        Vm = np.zeros(timesteps, dtype=np.float64)
        I = {current_type: np.zeros(timesteps, dtype=np.float64) for current_type in current_types}
        ionic = {ionic_type: np.zeros(timesteps, dtype=np.float64) for ionic_type in ionic_types}

        ##TF062724 Adding 8state state values for every timestep
        states12 = [["c1", "c2", "c3", "i1", "i2", "i3", "i4", "o"]]
        states16 = [["c1", "c2", "c3", "i1", "i2", "i3", "i4", "o"]]

        # print(f"I : {I}")
        stim = np.zeros(timesteps, dtype=np.float64)
        t = np.zeros(timesteps, dtype=np.float64)
        section = sim_config['section']
        section_number = sim_config['section_num']
        segment = sim_config['segment']
        volt_var = "h.cell.{section}[{section_number}]({segment}).v".format(section=section,
                                                                            section_number=section_number,
                                                                            segment=segment)
        # print(eval("h.psection()"))
        # print(h("topology()"))
        # val = eval("h.cADpyr232_L5_TTPC1_0fb1ca4724[0].soma[0](0.5).na12mut.ina_ina")
        # print(f"na16 mut {val}")
        curr_vars = {}
        # for current_type in current_types:
        #     #if current_type == 'ina_ina_na12':
        #     if current_type == 'na12.ina_ina':
        #         curr_vars[current_type] =  "h.cell.{section}[0].{current_type}".format(section=section, segment=segment, current_type=current_type)
        #     else:
        #         curr_vars[current_type] = "h.cell.{section}[0]({segment}).{current_type}".format(section=section, segment=segment, current_type=current_type)
        curr_vars = {
            current_type: "h.cell.{section}[{section_number}]({segment}).{current_type}".format(section=section,
                                                                                                section_number=section_number,
                                                                                                segment=segment,
                                                                                                current_type=current_type)
            for current_type in current_types}
        # print(f"current_vars : {curr_vars}") #####commented 12/11/23 TF
        ionic_vars = {ionic_type: "h.cell.{section}[{section_number}]({segment}).{ionic_type}".format(section=section,
                                                                                                      section_number=section_number,
                                                                                                      segment=segment,
                                                                                                      ionic_type=ionic_type)
                      for ionic_type in ionic_types}
        # print(f"ionic_vars : {ionic_vars}") ####commented 12/11/23 TF
        print(f"############################## Timesteps____________{timesteps}")
        for i in range(timesteps):

            Vm[i] = eval(volt_var)

            try:
                for current_type in current_types:
                    I[current_type][i] = eval(curr_vars[current_type])

                # getting the ionic concentrations
                for ionic_type in ionic_types:
                    ionic[ionic_type][i] = eval(ionic_vars[ionic_type])
                    # print(str(ionic_type) + "------" + str(i) + "-----" + str(eval(ionic_vars[ionic_type]))) ###for debugging
            except Exception as e:
                print(e)
                print("Check the config files for the correct Attribute")
                sys.exit(1)

            stim[i] = h.st.amp
            t[i] = i * h.dt / 1000

            ##TF062724 State values for 8 state HMM model
            #     states12.append([h.cell.soma[0].c1_na12,
            #                h.cell.soma[0].c2_na12,
            #                h.cell.soma[0].c3_na12,
            #                h.cell.soma[0].i1_na12,
            #                h.cell.soma[0].i2_na12,
            #                h.cell.soma[0].i3_na12,
            #                h.cell.soma[0].i4_na12,
            #                h.cell.soma[0].o_na12])

            #     states16.append([h.cell.soma[0].c1_na16,
            #                h.cell.soma[0].c2_na16,
            #                h.cell.soma[0].c3_na16,
            #                h.cell.soma[0].i1_na16,
            #                h.cell.soma[0].i2_na16,
            #                h.cell.soma[0].i3_na16,
            #                h.cell.soma[0].i4_na16,
            #                h.cell.soma[0].o_na16])

            h.fadvance()

        ###
        # df1 = pd.DataFrame(states12)
        # df2 = pd.DataFrame(states16)
        # df1.to_csv("/global/homes/t/tfenton/Neuron_general-2/Plots/Channel_state_plots/na12_channel_states.csv", header=False,index=False)
        # df2.to_csv("/global/homes/t/tfenton/Neuron_general-2/Plots/Channel_state_plots/na16_channel_states.csv", header=False,index=False)
        ###

        # print(f"I : {I}")
        return Vm, I, t, stim, ionic

    def plot_crazy_stim(self, stim_csv, stim_duration=None):
        if not stim_duration:
            stim_duration = 0.2  # ms

#######################
# MAIN
#######################

