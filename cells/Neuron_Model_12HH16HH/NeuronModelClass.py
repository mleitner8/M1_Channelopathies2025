# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 21:07:44 2021

@author: bensr
"""
import argparse
import numpy as np
from vm_plotter import *
from neuron import h
import os
import csv
import sys
import pandas as pd
import matplotlib.pyplot as plt
from NrnHelper import *
import gc


class NeuronModel:
    def __init__(self, ais_nav16_fac, ais_nav12_fac, mod_dir='..cells/Neuron_Model_12HH16HH/',

                 update=None,
                 ##TF If this is true, mechs are updated with update_mech_from_dict. Turn to false if you don't want update ### maybe not working???????
                 na12name='na12annaTFHH2',
                 na12mut_name='na12annaTFHH2',
                 na12mechs=['na12', 'na12mut'],
                 na16name='na16HH_TF2',
                 na16mut_name='na16HH_TF2',
                 na16mechs=['na16', 'na16mut'],
                 params_folder='..cells/Neuron_Model_12HH16HH/params/',

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
                 fac=None,
                 na12_scale=None,
                 #   morphology_index=0
                 ):

        run_dir = os.getcwd()

        os.chdir(mod_dir)
        self.h = h  # NEURON h
        print(f'running model at {os.getcwd()} run dir is {run_dir}')

        h.load_file("runModel.hoc")

        self.soma_ref = h.root.sec
        self.soma = h.secname(sec=self.soma_ref)
        self.sl = h.SectionList()
        self.sl.wholetree(sec=self.soma_ref)

        ## sections for normal adult neuron.
        self.nexus = h.cell.apic[66]
        self.dist_dend = h.cell.apic[91]
        self.ais = h.cell.axon[0]
        self.axon_proper = h.cell.axon[1]

        ## Adding ability to put scaling factors in for na12 and na12mut separately
        self.na12_scale = na12_scale

        # ___________________Kaustubh params
        h.dend_na12 = 2.48E-03 * dend_nav12

        # h.dend_na16 = 5.05E-06 * dend_nav16 ##TF020624
        h.dend_na16 = 0  ##TF020624 will be updated after initialization
        dend_nav16 = 5.05E-06 * dend_nav16
        h.dend_k = 0.0043685576 * dend_K

        ##062424 original params
        h.soma_na12 = 3.24E-02 * soma_nav12
        h.soma_na16 = 7.88E-02 * soma_nav16

        ##TF062424 testing equal conductances
        # h.soma_na12 = 3.24E-02 * soma_nav12
        # h.soma_na16 = 3.24E-02 * soma_nav16

        h.soma_K = 0.21330453 * soma_K

        # h.ais_na16 = 7.2696676 * ais_nav16
        h.ais_na16 = ais_nav16_fac * ais_nav16

        # h.ais_na12 = 1.03E+00 * ais_nav12
        h.ais_na12 = ais_nav12_fac * ais_nav12  # TF020124 added ais_nav12 factor to fine tune

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

        # h.dend_na12 = h.dend_na12 * nav12 * dend_nav12
        # h.soma_na12 = h.soma_na12 * nav12 * soma_nav12

        h.dend_na12 = h.dend_na12 * dend_nav12  ##TF050125 removed nav12 as it blanket multiples during update_mod_param
        h.soma_na12 = h.soma_na12 * soma_nav12  ##TF050125 removed nav12 as it blanket multiples during update_mod_param

        # h.ais_na12 = h.ais_na12 * nav12 * ais_nav12
        if nav12 != 0:
            h.ais_na12 = (
                                     h.ais_na12 * ais_nav12) / nav12  ##TF020624 decouple ais Nav1.2 from overall nav12. Needed because update_mod_param called later multiplies by nav12
        else:
            h.ais_na12 = h.ais_na12 * ais_nav12

        # h.ais_na16 = h.ais_na16 * nav16 * ais_nav16
        if nav16 != 0:
            h.ais_na16 = (
                                     h.ais_na16 * ais_nav16) / nav16  ##TF020624 decouple ais Nav1.6 from overall nav16. Needed because update_mod_param called later multiplies by nav16
        else:
            h.ais_na12 = h.ais_na16 * ais_nav16

        # h.dend_na16 = h.dend_na16 * nav16 * dend_nav16
        # h.soma_na16 = h.soma_na16 * nav16 * soma_nav16

        h.dend_na16 = h.dend_na16 * dend_nav16  ##TF050125 removed nav16 as it blanket multiples during update_mod_param
        h.soma_na16 = h.soma_na16 * soma_nav16  ##TF050125 removed nav16 as it blanket multiples during update_mod_param

        h.working()

        # h.load_file("/global/homes/t/tfenton/Neuron_general-2/Neuron_Model_12HMM16HH/printSh.hoc")

        # h.printVals12HHWT() ##TF will only work with HH mod files that have params like 'sh', 'tha', 'thi' etc.
        # h.printValsWT16()
        # h.printValsMUT16()

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
            # multiply_param(self,['SKv3_1'],'mtaumul',fac) ##TF083024 updated for hh model
            # multiply_param(self,['SKv3_1'],'vtau',fac)
            # multiply_param(self,['SKv3_1'],'gSKv3_1bar',fac)
            # multiply_param(self,['Ih'],'gIhbar',fac) ##TF82924
            # multiply_param(self,['Ca_LVAst'],'gCa_LVAstbar',fac) ##TF041924 multiplies gbar of Ca_LVAst

            # multiply_param(self,['SK_E2'],'gSK_E2bar',fac) ##TF041924 multiplies gbar of SKE2
            # multiply_param(self,['Ca_LVAst'],'gCa_LVAstbar',fac) ##TF041924 multiplies gbar of Ca_LVAst
            # multiply_param(self,['Ca_HVA'],'gCa_HVAbar',fac) ##TF070124 multiplies gbar of Ca_HVA. ***This was not present for HH model (aka value was 1)

            self.na12wt_mech = [na12mechs[0]]
            self.na12mut_mech = [na12mechs[1]]

            self.na16wt_mech = [na16mechs[0]]  ##TF021424 adding ability to update na16 (HH, shifted HH etc.)
            self.na16mut_mech = [na16mechs[1]]  ##TF021424 adding ability to update na16 (HH, shifted HH etc.)
            self.na16mechs = na16mechs

            self.h.working()
            p_fn_na12 = f'{params_folder}{na12name}.txt'
            p_fn_na12_mech = f'{params_folder}{na12mut_name}.txt'
            # print(f'using wt_file params {na12name}')
            self.na12_p = update_mech_from_dict(self, p_fn_na12, self.na12wt_mech)  ###
            print(eval("h.psection()"))
            # print(f'using mut_file params {na12mut_name}')
            self.na12_pmech = update_mech_from_dict(self, p_fn_na12_mech,
                                                    self.na12mut_mech)  # update_mech_from_dict(mdl,dict_fn,mechs,input_dict = False) 2nd arg (dict) updates 3rd (mech) ###
            print(eval("h.psection()"))

            # Updates gbar in na12 and na12mut mechs with value in nav12. Updates all gbars in all sections including all segments in AIS
            # This is a multiplier. After updating the mechanisms with nav12 params, this multiplies the gbar vals
            # update_mod_param(self,['na12','na12mut'],nav12)
            ## Below is modification to update_mod_param that allows scaling of na12 and na12mut separately TF090825
            if self.na12_scale is not None:
                for mech, fac in self.na12_scale.items():
                    update_mod_param(self, [mech], fac)
                else:
                    update_mod_param(self, ['na12', 'na12mut'], nav12)

            # h.load_file("/global/homes/t/tfenton/Neuron_general-2/Neuron_Model_12HMM16HH/printSh.hoc")
            # h.printVals12HHWT()

            # Adding ability to update with new Na16 mechs ##TF021424
            p_fn_na16 = f'{params_folder}{na16name}.txt'
            p_fn_na16_mech = f'{params_folder}{na16mut_name}.txt'

            # print(f'using na16wt_file params {na16name}')
            # self.na16_p = update_mech_from_dict(self, p_fn_na16,self.na16wt_mech) ###
            # print(eval("h.psection()"))
            # ##TF030624 Can load file below and run h.printValsWT to debug if mod file is getting updated or not
            # # h.load_file("/global/homes/t/tfenton/Neuron_general-2/Neuron_Model_12HMM16HH/printSh.hoc")
            # # h.printValsWT16()

            # print(f'using na16mut_file params {na16mut_name}')
            # self.na16_pmech = update_mech_from_dict(self, p_fn_na16_mech,self.na16mut_mech) ###
            # print(eval("h.psection()"))

            # # add nav16 only to first 20 microns of dendrites (apical and basal (dend)), otherwise gbar 0
            # update_mod_param(self,['na16','na16mut'],nav16)
            # for sec in self.h.allsec():
            #     if 'dend' in sec.name() or 'apic' in sec.name():
            #         for seg in sec:
            #             # for mech in ['na12', 'na12mut']:
            #             #         if hasattr(seg, mech):
            #             #             setattr(getattr(seg, mech), 'gbar', dend_nav12)

            #             if self.h.distance(sec(0.5), seg.x) <= 20:
            #                 for mech in ['na16', 'na16mut']:
            #                     if hasattr(seg, mech):
            #                         setattr(getattr(seg, mech), 'gbar', dend_nav16)
            #             else:
            #                 for mech in ['na16', 'na16mut']:
            #                     if hasattr(seg, mech):
            #                         setattr(getattr(seg, mech), 'gbar', 0)
            # print(eval("h.psection()"))

            print(f'using na16mut_file params {na16mut_name}')
            self.na16_pmech = update_mech_from_dict(self, p_fn_na16_mech, self.na16mut_mech)  ###
            print(eval("h.psection()"))

            # add nav16 only to first 20 microns of dendrites (apical and basal (dend)), otherwise gbar 0
            update_mod_param(self, ['na16', 'na16mut'], nav16)

            # --- Corrected distance calculation and gbar update ---
            # 1. Set the distance origin to the soma center
            soma_sec = self.h.cell.soma[0] if hasattr(self.h.cell, 'soma') else None
            if soma_sec:
                self.h.distance(0, 0.5, sec=soma_sec)
            else:
                print("Warning: Soma not found for distance calculation in __init__.")

            # 2. Iterate and set gbar based on correct path distance
            for sec in self.h.allsec():
                if 'dend' in sec.name() or 'apic' in sec.name():
                    for seg in sec:
                        # h.distance(seg) now gives the correct path distance from the soma
                        if self.h.distance(seg) <= 20:
                            for mech in ['na16', 'na16mut']:
                                if hasattr(seg, mech):
                                    # Note: dend_nav16 is very small (5.05e-6), may not be visible on plot
                                    setattr(getattr(seg, mech), 'gbar', dend_nav16)
                        else:
                            for mech in ['na16', 'na16mut']:
                                if hasattr(seg, mech):
                                    setattr(getattr(seg, mech), 'gbar', 0)

            print(eval("h.psection()"))

            # print(eval('h.cell.axon[0].psection()'))
            ##TF030624 Can load file below and run h.printValsWT to debug if mod file is getting updated or not
            # h.load_file("/global/homes/t/tfenton/Neuron_general-2/Neuron_Model_12HMM16HH/printSh.hoc")
            # h.printValsMUT16()
            # print(h("topology()"))

            # map_connectivity("numbered_connectivity_After.txt")

            # section = h.cell.axon[0]
            # print("Section properties:")
            # print(h.cell.axon[0].properties())

            # for sec in h.cell.axon:
            #     print("SKv3_1",sec.SKv3_1)
            #     print("SH",sec.sh_na16)
            #     # print("sh",sec.gIhbar_Ih)
            ############################################################

    ## map section connectivity and print gbar of na12 and na12mut for each section
    def map_connectivity(self, filename):
        def print_section_connectivity(sec, depth=0, file=None):
            indent = "  " * depth
            line = f"{indent}{depth + 1}. Section: {sec.name()} (L = {sec.L} um, nseg = {sec.nseg})\n"
            if file:
                file.write(line)
            else:
                print(line, end='')

            # Add gbar of na16 and na16mut
            for seg in sec:
                if hasattr(seg, 'na16'):
                    gbar_na16 = getattr(seg.na16, 'gbar', 'N/A')
                    line = f"{indent}  gbar_na16 = {gbar_na16}\n"
                    if file:
                        file.write(line)
                    else:
                        print(line, end='')
                if hasattr(seg, 'na16mut'):
                    gbar_na16mut = getattr(seg.na16mut, 'gbar', 'N/A')
                    line = f"{indent}  gbar_na16mut = {gbar_na16mut}\n"
                    if file:
                        file.write(line)
                    else:
                        print(line, end='')
            for seg in sec:
                if hasattr(seg, 'na12'):
                    gbar_na12 = getattr(seg.na12, 'gbar', 'N/A')
                    line = f"{indent}  gbar_na12 = {gbar_na12}\n"
                    if file:
                        file.write(line)
                    else:
                        print(line, end='')
                if hasattr(seg, 'na12mut'):
                    gbar_na12mut = getattr(seg.na12mut, 'gbar', 'N/A')
                    line = f"{indent}  gbar_na12mut = {gbar_na12mut}\n"
                    if file:
                        file.write(line)
                    else:
                        print(line, end='')

            for child in sec.children():
                print_section_connectivity(child, depth + 1, file)

        with open(filename, 'w') as file:
            file.write("Section connectivity map:\n")
            for sec in h.allsec():
                if sec.parentseg() is None:  # This is a root section (e.g., soma)
                    print_section_connectivity(sec, file=file)

    # map_connectivity("insert12_numbered_connectivity.txt")

    def get_gbar_sections(self, filename="gbars2.csv"):
        """
        Record gbar values for na12, na16, na12mut, na16mut, and Ih for every section.
        Save to CSV with section name and index.
        """
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["SectionName", "SectionIndex", "gbar_na12", "gbar_na16", "gbar_na12mut", "gbar_na16mut", "gbar_Ih"])
            for idx, sec in enumerate(h.allsec()):
                seg = sec(0.5)  # Use midpoint segment

                def safe_gbar(mech_name, attr='gbar'):
                    try:
                        if hasattr(seg, mech_name):
                            return getattr(getattr(seg, mech_name), attr)
                    except Exception:
                        pass
                    return 'N/A'

                gbar_na12 = safe_gbar('na12')
                gbar_na16 = safe_gbar('na16')
                gbar_na12mut = safe_gbar('na12mut')
                gbar_na16mut = safe_gbar('na16mut')
                gbar_Ih = safe_gbar('Ih', 'gIhbar')
                writer.writerow([sec.name(), idx, gbar_na12, gbar_na16, gbar_na12mut, gbar_na16mut, gbar_Ih])

    # get_gbar_sections()

    ## Map all sections connectivity and list parent sections
    def map_connectivity_parentchild(self, filename="connectivity_map_parentchild.txt"):
        def print_section_connectivity(sec, depth=0, branch_num=1, file=None):
            indent = "  " * depth
            line = f"{indent}{depth + 1}. Section: {sec.name()} (L = {sec.L} um, nseg = {sec.nseg}"

            if sec.parentseg():
                parent_name = sec.parentseg().sec.name()
                line += f", Parent: {parent_name})\n"
            else:
                line += f", Parent: None (Root section))\n"

            if file:
                file.write(line)
            else:
                print(line, end='')

            # Print psection for the current section
            psection_str = str(sec.psection())
            line = f"{indent}  psection(): {psection_str}\n"
            if file:
                file.write(line)
            else:
                print(line, end='')

            for child in sec.children():
                print_section_connectivity(child, depth + 1, branch_num + 1, file)

        with open(filename, 'w') as file:
            file.write("Mapping out section connectivity:\n")
            for sec in h.allsec():
                if sec.parentseg() is None:  # This is a root section (e.g., soma)
                    print_section_connectivity(sec, file=file)

    # map_connectivity_parentchild()

    # Function for determining and plotting the distribution of Na channels in axon.
    def chandensities(self, name=f"./Plots/12HH16HH/5-newAIS_raiseDVDT/49-vshift12_092424"):
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
        plt.savefig(f'{name}.pdf', dpi=400)

    ## Function for plotting channel densities in apical dendrite, soma, axon
    def chandensities2(self, name=f"./Plots/12HH16HH/5-newAIS_raiseDVDT/49-vshift12_092424"):
        distances = []
        na12_densities = []
        na16_densities = []
        na12mut_densities = []
        na16mut_densities = []
        sections = []

        for sec in h.cell.apic[0]:
            print(sec)
            section = f'h.distance.{sec}'
            distance = h.distance(0,
                                  sec) * -1  # h.distance(0,seg) ## Because section only has 1 seg, there is no distance
            print(f'Distance_SEG{distance}')
            distances.append(distance)
            sections.append(section)

            na12_gbar = sec.gbar_na12
            print(na12_gbar)
            na12_densities.append(na12_gbar)

            na16_gbar = sec.gbar_na16
            print(na16_gbar)
            na16_densities.append(na16_gbar)

            na12mut_gbar = sec.gbar_na12mut
            na12mut_densities.append(na12mut_gbar)

            na16mut_gbar = sec.gbar_na16mut
            na16mut_densities.append(na16mut_gbar)

        for sec in h.cell.soma[0]:
            print(sec)
            section = f'h.distance.{sec}'
            distance = 0  # h.distance(0,seg) ## Because section only has 1 seg, there is no distance
            print(f'Distance_SEG{distance}')
            distances.append(distance)
            sections.append(section)

            na12_gbar = sec.gbar_na12
            print(na12_gbar)
            na12_densities.append(na12_gbar)

            na16_gbar = sec.gbar_na16
            print(na16_gbar)
            na16_densities.append(na16_gbar)

            na12mut_gbar = sec.gbar_na12mut
            na12mut_densities.append(na12mut_gbar)

            na16mut_gbar = sec.gbar_na16mut
            na16mut_densities.append(na16mut_gbar)

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
        # plt.xticks(range(-1, len(distances)), rotation=270, fontsize=4)
        plt.xticks(range(-1, len(distances), 2), rotation=270, fontsize=4)
        ax.set_xticks(range(-1, len(distances)))
        ax.set_xticklabels([str(i) if i % 10 == 0 else '' for i in range(-1, len(distances))], rotation=270, fontsize=4)
        plt.xlabel('Segment of Axon')
        plt.ylabel('gbar')
        plt.title("Distribution of Nav12 and Nav16")
        # plt.savefig(name+".png", dpi=400)
        plt.savefig(name + ".pdf", dpi=400)

    ## Function for plotting channel densities in apical and basal dendrites
    def dend_chandensities2(self, regions=['apic', 'dend', 'soma', 'axon'],
                            name=f"./Plots/12HH16HH/5-newAIS_raiseDVDT/49-vshift12_092424"):
        # --- Data Collection ---
        data = {
            'Distance': [], 'na12': [], 'na16': [], 'na12mut': [], 'na16mut': [],
            'skv31': [], 'lva': [], 'hva': [], 'ltype': [], 'ske2': [], 'ih': [], 'section_name': []
        }

        # Helper to safely get gbar from a segment
        def get_gbar(seg, mech_name):
            try:
                if mech_name == 'SKv3_1': return seg.gSKv3_1bar_SKv3_1
                if mech_name == 'Ca_LVAst': return seg.gCa_LVAstbar_Ca_LVAst
                if mech_name == 'Ca_HVA': return seg.gCa_HVAbar_Ca_HVA
                if mech_name == 'Ca_Ltype': return seg.gCa_Ltypebar_Ca_Ltype
                if mech_name == 'SK_E2': return seg.gSK_E2bar_SK_E2
                if mech_name == 'Ih': return seg.gIhbar_Ih
                # For na12, na16, etc.
                if hasattr(seg, f'gbar_{mech_name}'):
                    return getattr(seg, f'gbar_{mech_name}')
            except AttributeError:
                return 0
            return 0

        # Set the distance measurement origin to the soma center
        soma_sec = h.cell.soma[0] if hasattr(h.cell, 'soma') else None
        if soma_sec:
            h.distance(0, 0.5, sec=soma_sec)
        else:
            print("Warning: Soma section not found. Distances may be incorrect.")
            return

        # Collect all apical and basal dendritic sections
        sections_to_plot = []
        for region_name in regions:
            if hasattr(h.cell, region_name):
                sections_to_plot.extend(list(getattr(h.cell, region_name)))
            else:
                print(f"Warning: Region '{region_name}' not found in h.cell.")

        # Iterate over each segment of each section
        for sec in sections_to_plot:
            for seg in sec:
                dist = h.distance(seg.x, sec=sec)
                data['Distance'].append(dist)
                data['section_name'].append(sec.name())
                data['na12'].append(get_gbar(seg, 'na12'))
                data['na16'].append(get_gbar(seg, 'na16'))
                data['na12mut'].append(get_gbar(seg, 'na12mut'))
                data['na16mut'].append(get_gbar(seg, 'na16mut'))
                data['skv31'].append(get_gbar(seg, 'SKv3_1'))
                data['lva'].append(get_gbar(seg, 'Ca_LVAst'))
                data['hva'].append(get_gbar(seg, 'Ca_HVA'))
                data['ltype'].append(get_gbar(seg, 'Ca_Ltype'))
                data['ske2'].append(get_gbar(seg, 'SK_E2'))
                data['ih'].append(get_gbar(seg, 'Ih'))

        # --- Plotting ---
        df = pd.DataFrame(data).sort_values(by='Distance')

        fig, ax = plt.subplots(figsize=(12, 7))

        channels = ['na12', 'na12mut', 'na16', 'na16mut', 'skv31', 'lva', 'hva', 'ltype', 'ske2', 'ih']
        cmap = plt.get_cmap('rainbow')
        colors = cmap(np.linspace(0, 1, len(channels)))

        for i, channel in enumerate(channels):
            linestyle = 'solid'
            if 'mut' in channel:
                linestyle = 'dotted'
            ax.plot(df['Distance'], df[channel], label=channel, color=colors[i], linewidth=3.0, linestyle=linestyle)

        ax.legend(title="Channels", fontsize=14, title_fontsize=16, loc='upper left')
        ax.set_xlabel('Distance from Soma (µm)', fontsize=16)
        ax.set_ylabel('Conductance (gbar)', fontsize=16)
        ax.set_title(f'Channel Density Distribution in {", ".join(regions)}', fontsize=18)
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)

        plt.tight_layout()
        plt.savefig(f"{name}.pdf", dpi=400)
        plt.close(fig)

    def dend_chandensities3(self, regions=['apic', 'dend', 'soma', 'axon'],
                            name=f"./Plots/12HH16HH/5-newAIS_raiseDVDT/49-vshift12_092424"):
        # --- Data Collection ---
        data = {
            'Distance': [], 'na12': [], 'na16': [], 'na12mut': [], 'na16mut': [],
            'skv31': [], 'lva': [], 'hva': [], 'ltype': [], 'ske2': [], 'ih': [], 'section_name': []
        }

        # Helper to safely get gbar from a segment
        def get_gbar(seg, mech_name):
            try:
                if mech_name == 'SKv3_1': return seg.gSKv3_1bar_SKv3_1
                if mech_name == 'Ca_LVAst': return seg.gCa_LVAstbar_Ca_LVAst
                if mech_name == 'Ca_HVA': return seg.gCa_HVAbar_Ca_HVA
                if mech_name == 'Ca_Ltype': return seg.gCa_Ltypebar_Ca_Ltype
                if mech_name == 'SK_E2': return seg.gSK_E2bar_SK_E2
                if mech_name == 'Ih': return seg.gIhbar_Ih
                # For na12, na16, etc.
                if hasattr(seg, f'gbar_{mech_name}'):
                    return getattr(seg, f'gbar_{mech_name}')
            except AttributeError:
                return 0
            return 0

        # Set the distance measurement origin to the soma center
        soma_sec = h.cell.soma[0] if hasattr(h.cell, 'soma') else None
        if soma_sec:
            h.distance(0, 0.5, sec=soma_sec)
        else:
            print("Warning: Soma section not found. Distances may be incorrect.")
            return

        # Iterate over regions to collect data
        for region_name in regions:
            sections_to_plot = []

            # Explicitly handle axon to ensure we get all sections as requested
            if region_name == 'axon':
                sections_to_plot = list(h.cell.axon)
            elif hasattr(h.cell, region_name):
                sections_to_plot = list(getattr(h.cell, region_name))
            else:
                print(f"Warning: Region '{region_name}' not found in h.cell.")
                continue

            # Iterate over each segment of each section
            for sec in sections_to_plot:
                for seg in sec:
                    # Calculate path distance from soma
                    # Using h.distance(seg) which calculates distance from origin to segment center
                    dist = h.distance(seg)

                    # Apply sign based on region: Dendrites negative (left), Axon/Soma positive (right)
                    if region_name in ['apic', 'dend']:
                        dist = -dist

                    data['Distance'].append(dist)
                    data['section_name'].append(sec.name())
                    data['na12'].append(get_gbar(seg, 'na12'))
                    data['na16'].append(get_gbar(seg, 'na16'))
                    data['na12mut'].append(get_gbar(seg, 'na12mut'))
                    data['na16mut'].append(get_gbar(seg, 'na16mut'))
                    data['skv31'].append(get_gbar(seg, 'SKv3_1'))
                    data['lva'].append(get_gbar(seg, 'Ca_LVAst'))
                    data['hva'].append(get_gbar(seg, 'Ca_HVA'))
                    data['ltype'].append(get_gbar(seg, 'Ca_Ltype'))
                    data['ske2'].append(get_gbar(seg, 'SK_E2'))
                    data['ih'].append(get_gbar(seg, 'Ih'))

        # --- Plotting ---
        # Sort by distance to ensure lines connect correctly from left (negative) to right (positive)
        df = pd.DataFrame(data).sort_values(by='Distance')

        fig, ax = plt.subplots(figsize=(12, 7))

        channels = ['na12', 'na12mut', 'na16', 'na16mut', 'skv31', 'lva', 'hva', 'ltype', 'ske2', 'ih']
        # Use tab10 for distinct, modern colors
        cmap = plt.get_cmap('rainbow')
        colors = cmap(np.linspace(0, 1, len(channels)))

        for i, channel in enumerate(channels):
            linestyle = 'solid'
            if 'mut' in channel:
                linestyle = 'dotted'
            ax.plot(df['Distance'], df[channel], label=channel, color=colors[i], linewidth=1.5, linestyle=linestyle)

        ax.set_yscale('log')  # Set y-axis to log scale
        ax.legend(title="Channels")
        ax.set_xlabel('Distance from Soma (µm) \n(<- Dendrites | Axon ->)')
        ax.set_ylabel('Conductance (gbar) [Log Scale]')
        ax.set_title(f'Channel Density Distribution')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Add a vertical line at 0 to mark the soma
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)

        plt.tight_layout()
        plt.savefig(f"{name}.pdf", dpi=400)
        plt.close(fig)

    # def init_stim(self, sweep_len = 800, stim_start = 30, stim_dur = 500, amp = 0.3, dt = 0.1): #Na16 zoom into single peak args
    # def init_stim(self, sweep_len = 800, stim_start = 100, stim_dur = 500, amp = 0.3, dt = 0.1): ##TF050924 Changed to default for HH figs for grant 061424 ##This is a good new setting

    # def init_stim(self, sweep_len = 300, stim_start = 100, stim_dur = 300, amp = 0.3, dt = 0.01): ##faster for debugging tf012926
    def init_stim(self, sweep_len=700, stim_start=100, stim_dur=500, amp=0.3,
                  dt=0.01):  ##TF050924 Changed to default for HH figs for grant 061424 ##This is a good new setting
        # def init_stim(self, sweep_len = 1200, stim_start = 100, stim_dur = 1000, amp = 0.3, dt = 0.01): ##TF102025 Long sweeps for better traces + FIs for paper

        h("st.del = " + str(stim_start))
        h("st.dur = " + str(stim_dur))
        h("st.amp = " + str(amp))
        h.tstop = sweep_len
        h.dt = dt

    def init_stim_dend(self, sweep_len=150, stim_start=30, stim_dur=100, amp=0.5,
                       dt=0.1):  ## This stimulates dend[0] segment 0.5 (runModel.hoc line 181-184)
        h("st_dend.del = " + str(stim_start))
        h("st_dend.dur = " + str(stim_dur))
        h("st_dend.amp = " + str(amp))
        h.tstop = sweep_len
        h.dt = dt

    def init_stim_dend_youpicksection(self, sweep_len=150, amp=0.5, stim_dur=100, stim_start=30, dt=0.1,
                                      section_type='dend', section_index=0, section_seg=0.5):
        # Use Python object access for reliability, fallback to HOC
        try:
            # Note: in Python NEURON, 'del' is accessed as 'delay'
            h.st_dend.delay = stim_start
            h.st_dend.dur = stim_dur
            h.st_dend.amp = amp
        except Exception as e:
            print(f"Warning: Could not set st_dend params via Python interface ({e}). Trying HOC...")
            h(f"st_dend.del = {stim_start}")
            h(f"st_dend.dur = {stim_dur}")
            h(f"st_dend.amp = {amp}")

        try:
            if hasattr(h.cell, section_type):
                target_section = getattr(h.cell, section_type)[section_index]
                h.st_dend.loc(section_seg, sec=target_section)
                # print(f"Moved st_dend to {target_section.name()}({section_seg})")
            else:
                print(f"Error: Section type '{section_type}' not found in h.cell")
        except Exception as e:
            print(f"Error updating stimulus location: {e}")

        h.tstop = sweep_len
        h.dt = dt

    def init_dend_epsp_stim(self, sweep_len=150, amp=0.5, stim_start=30, dt=0.1,
                            tau1=1.0, tau2=6.0,
                            section_type='apic', section_index=77, section_seg=0.5):
        """
        Injects a current with a double-exponential shape (mimicking an EPSP)
        into a dendritic section.
        Formula: I(t) = Norm * Amp * (1 - exp(-t/tau1)) * exp(-t/tau2)
        Larkum et al. (1999): tau1 ~0.5-2ms, tau2 ~2-8ms.
        """
        # 1. Set location
        try:
            target_section = getattr(h.cell, section_type)[section_index]
            h.st_dend.loc(section_seg, sec=target_section)
        except Exception as e:
            print(f"Error setting EPSP stim location values: {e}")

        # 2. Setup time vector
        h.dt = dt
        h.tstop = sweep_len
        n_steps = int(sweep_len / dt) + 1
        t_vec = np.linspace(0, sweep_len, n_steps)
        i_vec = np.zeros_like(t_vec)

        # 3. Calculate Double Exponential Waveform
        # Find peak time to normalize amplitude
        # Function f(t) = (1 - exp(-t/tau1)) * exp(-t/tau2)
        # We solve for max manually or just compute max of array to normalize

        # Determine indices where stim is active
        start_idx = int(stim_start / dt)

        # Generate raw curve
        local_t = t_vec[start_idx:] - stim_start
        # Prevent division by zero or errors if taus are bad
        if tau1 <= 0 or tau2 <= 0: tau1, tau2 = 1.0, 6.0

        raw_wave = (1 - np.exp(-local_t / tau1)) * np.exp(-local_t / tau2)

        # Normalize so the peak equals 'amp'
        if len(raw_wave) > 0 and raw_wave.max() > 0:
            raw_wave = raw_wave / raw_wave.max() * amp

        i_vec[start_idx:] = raw_wave[:len(i_vec[start_idx:])]

        # 4. Use Vector play
        # We must store these vectors in self so they aren't garbage collected
        self.dend_stim_t = h.Vector(t_vec)
        self.dend_stim_i = h.Vector(i_vec)

        # Configure st_dend to be controlled by the vector
        h.st_dend.delay = 0  # delay is handled by the 0s in the vector
        h.st_dend.dur = 1e9  # turn it "on" forever, vector amplitude controls signal
        h.st_dend.amp = 0  # base amplitude

        # Play the vector into the source amplitude
        self.dend_stim_i.play(h.st_dend._ref_amp, self.dend_stim_t, True)

    def init_dual_stim_and_run(self, sweep_len=150, dt=0.1,
                               soma_amp=0.3, soma_dur=100, soma_start=30,
                               dend_amp=0.5, dend_dur=100, dend_start=30,
                               dend_section_type='dend', dend_section_index=0, dend_section_seg=0.5,
                               dend2_section_type=None, dend2_section_index=None, dend2_section_seg=0.5,
                               rec_extra=False,
                               dend_shape='epsp', tau1=1.0, tau2=6.0):  # if not 'epsp', use 'square' for step current
        """
        Initializes both somatic and dendritic stimuli, runs the model, and returns data.
        """
        # Ensure somatic stimulus is at the soma
        h.st.loc(0.5, sec=self.soma_ref)

        self.init_stim(sweep_len=sweep_len, stim_start=soma_start, stim_dur=soma_dur, amp=soma_amp, dt=dt)

        if dend_shape == 'epsp':
            self.init_dend_epsp_stim(sweep_len=sweep_len, amp=dend_amp, stim_start=dend_start, dt=dt,
                                     tau1=tau1, tau2=tau2,
                                     section_type=dend_section_type, section_index=dend_section_index,
                                     section_seg=dend_section_seg)
        else:
            self.init_stim_dend_youpicksection(sweep_len=sweep_len, amp=dend_amp, stim_dur=dend_dur,
                                               stim_start=dend_start, dt=dt,
                                               section_type=dend_section_type, section_index=dend_section_index,
                                               section_seg=dend_section_seg)

        # 3. Run Model
        # Note: run_model uses h.tstop which was set by init_stim/init_stim_dend_youpicksection

        # We need to record the dendritic voltage as well
        # Create a vector to record the dendritic voltage
        dend_v_vec = h.Vector()
        target_section = getattr(h.cell, dend_section_type)[dend_section_index]
        dend_v_vec.record(target_section(dend_section_seg)._ref_v)

        dend2_v_vec = None
        if dend2_section_type is not None and dend2_section_index is not None:
            dend2_v_vec = h.Vector()
            target_section2 = getattr(h.cell, dend2_section_type)[dend2_section_index]
            dend2_v_vec.record(target_section2(dend2_section_seg)._ref_v)

        # Run the model
        if rec_extra:
            Vm, I, t, stim, extra_vms, dend_stim = self.run_model(dt=dt, rec_extra=rec_extra)
            dend2_res = np.array(dend2_v_vec)[:len(Vm)] if dend2_v_vec else None
            return Vm, I, t, stim, extra_vms, np.array(dend_v_vec)[:len(Vm)], dend2_res, dend_stim
        else:
            Vm, I, t, stim, dend_stim = self.run_model(dt=dt, rec_extra=rec_extra)
            dend2_res = np.array(dend2_v_vec)[:len(Vm)] if dend2_v_vec else None
            return Vm, I, t, stim, np.array(dend_v_vec)[:len(Vm)], dend2_res, dend_stim

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
        dend_stim = np.zeros(timesteps)
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
            stim[i] = h.st.i  # Changed to .i to capture actual current delivered

            # Capture dendritic stim current if st_dend is active
            if hasattr(h, 'st_dend'):
                dend_stim[i] = h.st_dend.i

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
            return Vm, I, t, stim, extra_Vms, dend_stim
        else:
            return Vm, I, t, stim, dend_stim

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


