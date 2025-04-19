"""
cfg.py

Simulation configuration for M1 model (using NetPyNE)

Contributors: salvadordura@gmail.com
"""

from netpyne import specs
import pickle
import os

cfg = specs.SimConfig()

# ------------------------------------------------------------------------------
#
# SIMULATION CONFIGURATION
#
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Run parameters
# ------------------------------------------------------------------------------
cfg.duration = 1000
cfg.dt = 0.025
cfg.seeds = {'conn': 4321, 'stim': 1234, 'loc': 4321}
cfg.hParams = {'celsius': 34, 'v_init': -80}
cfg.verbose = 0
cfg.createNEURONObj = 1
cfg.createPyStruct = 1
cfg.connRandomSecFromList = False  # set to false for reproducibility
cfg.cvode_active = False
cfg.cvode_atol = 1e-6
cfg.cache_efficient = True
cfg.printRunTime = 0.1
cfg.oneSynPerNetcon = True  # only affects conns not in subconnParams; produces identical results

cfg.includeParamsLabel = False  # True # needed for modify synMech False
cfg.printPopAvgRates = [1000., 5000.]

cfg.checkErrors = False

cfg.saveInterval = 100  # define how often the data is saved, this can be used with interval run if you want to update the weights more often than you save
cfg.intervalFolder = 'interval_saving'

cfg.UCDAVIS = True

# ------------------------------------------------------------------------------
# Recording
# ------------------------------------------------------------------------------
allpops = ['IT2', 'PV2', 'SOM2', 'IT4', 'IT5A', 'PV5A', 'SOM5A', 'IT5B', 'PT5B', 'PV5B', 'SOM5B', 'IT6', 'CT6', 'PV6',
           'SOM6']

cfg.cellsrec = 1
if cfg.cellsrec == 0:
    cfg.recordCells = ['all']  # record all cells
elif cfg.cellsrec == 1:
    cfg.recordCells = [(pop, s) for pop in allpops for s in [0, 10, 20, 30, 40]]  # record one cell of each pop
elif cfg.cellsrec == 2:
    cfg.recordCells = [('IT2', 10), ('IT5A', 10), ('PT5B', 10), ('PV5B', 10), ('SOM5B', 10)]  # record selected cells
elif cfg.cellsrec == 3:
    cfg.recordCells = [(pop, 50) for pop in ['IT5A', 'PT5B']] + [('PT5B', x) for x in [393, 579, 19,
                                                                                       104]]  # ,214,1138,799]] # record selected cells # record selected cells
elif cfg.cellsrec == 4:
    cfg.recordCells = [(pop, 50) for pop in ['IT2', 'IT4', 'IT5A', 'PT5B']] \
                      + [('IT5A', x) for x in [393, 447, 579, 19, 104]] \
                      + [('PT5B', x) for x in [393, 447, 579, 19, 104, 214, 1138, 979, 799]]  # record selected cells

# cfg.recordTraces = {'V_soma': {'sec':'soma', 'loc':0.5, 'var':'v'}}

cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v', 'conds': {'pop': 'PT5B'}},
                    'V_axon_0': {'sec': 'axon_0', 'loc': 0.5, 'var': 'v', 'conds': {'pop': 'PT5B'}}}

cfg.recordStim = False
cfg.recordTime = False
cfg.recordStep = 0.1

# ------------------------------------------------------------------------------
# Saving
# ------------------------------------------------------------------------------
cfg.simLabel = 'v2_tune14'
cfg.saveFolder = '../data/v2_manualTune'
cfg.savePickle = True
cfg.saveJson = True
cfg.saveDataInclude = ['simData', 'simConfig', 'netParams']  # , 'net']
cfg.backupCfgFile = None  # ['cfg.py', 'backupcfg/']
cfg.gatherOnlySimData = False
cfg.saveCellSecs = False
cfg.saveCellConns = False
cfg.compactConnFormat = 0

# ------------------------------------------------------------------------------
# Analysis and plotting
# ------------------------------------------------------------------------------
with open('../cells/popColors.pkl', 'rb') as fileObj: popColors = pickle.load(fileObj)['popColors']

cfg.analysis['plotRaster'] = {'include': allpops, 'orderBy': ['pop', 'y'], 'timeRange': [0, cfg.duration],
                              'saveFig': True, 'showFig': False, 'popRates': True, 'orderInverse': True,
                              'popColors': popColors, 'figSize': (12, 10), 'lw': 0.3, 'markerSize': 3, 'marker': '.',
                              'dpi': 300}

cfg.analysis['plotTraces'] = {'include': cfg.recordCells, 'timeRange': [0, cfg.duration], 'overlay': True,
                              'oneFigPer': 'trace', 'figSize': (10, 4), 'saveFig': True, 'showFig': False}

# ------------------------------------------------------------------------------
# Cells
# ------------------------------------------------------------------------------
cfg.cellmod = {'IT2': 'HH_reduced',
               'IT4': 'HH_reduced',
               'IT5A': 'HH_full',
               'IT5B': 'HH_reduced',
               'PT5B': 'HH_full',
               'IT6': 'HH_reduced',
               'CT6': 'HH_reduced'}

cfg.ihModel = 'migliore'  # ih model
cfg.ihGbar = 1.0  # multiplicative factor for ih gbar in PT cells
cfg.ihGbarZD = None  # multiplicative factor for ih gbar in PT cells
cfg.ihGbarBasal = 1.0  # 0.1 # multiplicative factor for ih gbar in PT cells
cfg.ihlkc = 0.2  # ih leak param (used in Migliore)
cfg.ihlkcBasal = 1.0
cfg.ihlkcBelowSoma = 0.01
cfg.ihlke = -86  # ih leak param (used in Migliore)
cfg.ihSlope = 14 * 2

cfg.removeNa = False  # simulate TTX; set gnabar=0s
cfg.somaNa = 5
cfg.dendNa = 0.3
cfg.axonNa = 7
cfg.axonRa = 0.005

cfg.gpas = 0.5  # multiplicative factor for pas g in PT cells
cfg.epas = 0.9  # multiplicative factor for pas e in PT cells

cfg.KgbarFactor = 1.0  # multiplicative factor for K channels gbar in all E cells
cfg.makeKgbarFactorEqualToNewFactor = False

if cfg.UCDAVIS == False:
    cfg.modifyMechs = {'startTime': 500, 'endTime': 1000, 'cellType': 'PT', 'mech': 'hd', 'property': 'gbar',
                       'newFactor': 1.00, 'origFactor': 0.75}
else:
    cfg.modifyMechs = {'startTime': 1e20 * 500, 'endTime': 1e20 * 1000, 'cellType': 'PT', 'mech': 'hd',
                       'property': 'gbar', 'newFactor': 1.00, 'origFactor': 0.75}

cfg.PTNaFactor = 1

# ------------------------------------------------------------------------------
# Synapses
# ------------------------------------------------------------------------------
cfg.synWeightFractionEE = [0.5, 0.5]  # E->E AMPA to NMDA ratio
cfg.synWeightFractionEI = [0.5, 0.5]  # E->I AMPA to NMDA ratio
cfg.synWeightFractionSOME = [0.9, 0.1]  # SOM -> E GABAASlow to GABAB ratio

cfg.synsperconn = {'HH_full': 5, 'HH_reduced': 1, 'HH_simple': 1}
cfg.AMPATau2Factor = 1.0

# ------------------------------------------------------------------------------
# Network
# ------------------------------------------------------------------------------
cfg.singleCellPops = False  # Create pops with 1 single cell (to debug)
cfg.weightNorm = 1  # use weight normalization
cfg.weightNormThreshold = 4.0  # weight normalization factor threshold

cfg.addConn = 1
cfg.scale = 1
cfg.sizeY = 1350.0
cfg.sizeX = 300.0
cfg.sizeZ = 300.0
cfg.correctBorderThreshold = 150.0

cfg.L5BrecurrentFactor = 1.0
cfg.ITinterFactor = 1.0
cfg.strengthFactor = 1.0

cfg.EEGain = 1.0  # 0.5
cfg.EIGain = 1.0
cfg.IEGain = 1.0
cfg.IIGain = 1.0

cfg.IEdisynapticBias = None  # increase prob of I->Ey conns if Ex->I and Ex->Ey exist

# ------------------------------------------------------------------------------
## E->I gains
cfg.EPVGain = 1.0
cfg.ESOMGain = 1.0

# ------------------------------------------------------------------------------
## I->E gains
cfg.PVEGain = 1.0
cfg.SOMEGain = 1.0

# ------------------------------------------------------------------------------
## I->I gains
cfg.PVSOMGain = None  # 0.25
cfg.SOMPVGain = None  # 0.25
cfg.PVPVGain = None  # 0.75
cfg.SOMSOMGain = None  # 0.75

# ------------------------------------------------------------------------------
## I->E/I layer weights (L2/3+4, L5, L6)
cfg.IEweights = [0.8592, 1.492, 1.2818]  # [0.8, 1.2, 1.0]
cfg.IIweights = [1.4254, 0.6253, 1.4879]  # [1.4, 1.1, 1.4] #

cfg.IPTGain = 1.0
cfg.IFullGain = 1.0

# ------------------------------------------------------------------------------
# Subcellular distribution
# ------------------------------------------------------------------------------
cfg.addSubConn = False

# ------------------------------------------------------------------------------
# Long range inputs
# ------------------------------------------------------------------------------
cfg.addLongConn = 1
cfg.numCellsLong = 1000  # num of cells per population
cfg.noiseLong = 1.0  # firing rate random noise
cfg.delayLong = 5.0  # (ms)
factor = 1
cfg.weightLong = {'TPO': 0.5, 'TVL': 0.5,
                  'S1': 0.5, 'S2': 0.5,
                  'cM1': 0.5, 'M2': 0.5,
                  'OC': 0.5}
# {'TPO': 0.5*factor, 'TVL': 0.5*factor, 'S1': 0.5*factor, 'S2': 0.5*factor,
# 'cM1': 0.5*factor, 'M2': 0.5*factor, 'OC': 0.5*factor}  # corresponds to unitary connection somatic EPSP (mV)
cfg.startLong = 0  # start at 0 ms
cfg.ratesLong = {'TPO': [0, 5], 'TVL': [0, 2.5], 'S1': [0, 5], 'S2': [0, 5], 'cM1': [0, 2.5], 'M2': [0, 2.5],
                 'OC': [0, 5]}

## input pulses
cfg.addPulses = 1
cfg.pulse = {'pop': 'None', 'start': 1000, 'end': 1200, 'rate': [0, 20], 'noise': 0.8}
cfg.pulse2 = {'pop': 'None', 'start': 1000, 'end': 1200, 'rate': [0, 20], 'noise': 0.5, 'duration': 500}

# ------------------------------------------------------------------------------
# Current inputs
# ------------------------------------------------------------------------------
cfg.addIClamp = 0

cfg.IClamp1 = {'pop': 'IT5B', 'sec': 'soma', 'loc': 0.5, 'start': 0, 'dur': 1000, 'amp': 0.50}

# ------------------------------------------------------------------------------
# NetStim inputs
# ------------------------------------------------------------------------------
cfg.addNetStim = 0

## pop, sec, loc, synMech, start, interval, noise, number, weight, delay
cfg.NetStim1 = {'pop': 'IT5B', 'sec': 'soma', 'loc': 0.5, 'synMech': ['AMPA', 'NMDA'],
                'synMechWeightFactor': [0.5, 0.5],
                'start': 0, 'interval': 1000.0 / 40.0, 'noise': 0.0, 'number': 1000.0, 'weight': 0.5, 'delay': 0}
