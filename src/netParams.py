
"""
netParams.py 

High-level specifications for M1 network model using NetPyNE

Contributors: salvadordura@gmail.com
"""

from netpyne import specs
import pickle, json

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

netParams.version = 56

#Import cfg for new batchtools:
from cfg import cfg
cfg.update()
import csv

# Import cfg for old batch:
#try:
    #from __main__ import cfg  # import SimConfig object with params from parent module
#except:
    #from cfg import cfg

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# General network parameters
#------------------------------------------------------------------------------
netParams.scale = cfg.scale # Scale factor for number of cells
netParams.sizeX = cfg.sizeX # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ # z-dimension (horizontal depth) size in um
netParams.shape = 'cylinder' # cylindrical (column-like) volume

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
netParams.scaleConnWeight = 1.0 # Connection weight scale factor (default if no model specified)
netParams.scaleConnWeightModels = {'HH_simple': 1.0, 'HH_reduced': 1.0, 'HH_full': 1.0} #scale conn weight factor for each cell model
netParams.scaleConnWeightNetStims = 1.0 #0.5  # scale conn weight factor for NetStims
netParams.defaultThreshold = 0.0 # spike threshold, 10 mV is NetCon default, lower it for all cells
netParams.defaultDelay = 2.0 # default conn delay (ms)
netParams.propVelocity = 500.0 # propagation velocity (um/ms)
netParams.probLambda = 100.0  # length constant (lambda) for connection probability decay (um)
netParams.defineCellShapes = True  # convert stylized geoms to 3d points


# special condition to change Kgbar together with ih when running batch
# note min Kgbar is assumed to be 0.5, so this is set here as an offset 
if cfg.makeKgbarFactorEqualToNewFactor:
    cfg.KgbarFactor = 0.5 + cfg.modifyMechs['newFactor']

#------------------------------------------------------------------------------
# Cell parameters
#------------------------------------------------------------------------------
cellModels = ['HH_simple', 'HH_reduced', 'HH_full']
layer = {'1':[0.0, 0.1], '2': [0.1,0.29], '4': [0.29,0.37], '5A': [0.37,0.47], '24':[0.1,0.37], '5B': [0.47,0.8], '6': [0.8,1.0], 
'longTPO': [2.0,2.1], 'longTVL': [2.1,2.2], 'longS1': [2.2,2.3], 'longS2': [2.3,2.4], 'longcM1': [2.4,2.5], 'longM2': [2.5,2.6], 'longOC': [2.6,2.7]}  # normalized layer boundaries

netParams.correctBorder = {'threshold': [cfg.correctBorderThreshold, cfg.correctBorderThreshold, cfg.correctBorderThreshold],
                        'yborders': [layer['2'][0], layer['5A'][0], layer['6'][0], layer['6'][1]]}  # correct conn border effect

#------------------------------------------------------------------------------
## Load cell rules previously saved using netpyne format
cellParamLabels = ['IT2_reduced', 'IT4_reduced', 'IT5A_reduced', 'IT5B_reduced', 'PT5B_reduced',
    'IT6_reduced', 'CT6_reduced', 'PV_simple', 'SOM_simple', 'IT5A_full', 'PT5B_full'] # 'NGF_simple', 'VIP_reduced'] # list of cell rules to load from file
loadCellParams = cellParamLabels
saveCellParams = False

for ruleLabel in loadCellParams:
    netParams.loadCellParamsRule(label=ruleLabel, fileName='../cells/'+ruleLabel+'_cellParams.pkl')
    
    # Adapt K gbar
    if ruleLabel in ['IT2_reduced', 'IT4_reduced', 'IT5A_reduced', 'IT5B_reduced', 'IT6_reduced', 'CT6_reduced', 'IT5A_full']:
        cellRule = netParams.cellParams[ruleLabel]
        for secName in cellRule['secs']:
            for kmech in [k for k in cellRule['secs'][secName]['mechs'].keys() if k.startswith('k') and k!='kBK']:
                cellRule['secs'][secName]['mechs'][kmech]['gbar'] *= cfg.KgbarFactor 

#------------------------------------------------------------------------------
# Specification of cell rules not previously loaded
# Includes importing from hoc template or python class, and setting additional params

#------------------------------------------------------------------------------
# Reduced cell model params (6-comp) 
reducedCells = {  # layer and cell type for reduced cell models
    'IT2_reduced':  {'layer': '2',  'cname': 'CSTR6', 'carg': 'BS1578'}, 
    'IT4_reduced':  {'layer': '4',  'cname': 'CSTR6', 'carg': 'BS1578'},
    'IT5A_reduced': {'layer': '5A', 'cname': 'CSTR6', 'carg': 'BS1579'},
    'IT5B_reduced': {'layer': '5B', 'cname': 'CSTR6', 'carg': 'BS1579'},
    'PT5B_reduced': {'layer': '5B', 'cname': 'SPI6',  'carg':  None},
    'IT6_reduced':  {'layer': '6',  'cname': 'CSTR6', 'carg': 'BS1579'},
    'CT6_reduced':  {'layer': '6',  'cname': 'CSTR6', 'carg': 'BS1578'}}

reducedSecList = {  # section Lists for reduced cell model
    'alldend':  ['Adend1', 'Adend2', 'Adend3', 'Bdend'],
    'spiny':    ['Adend1', 'Adend2', 'Adend3', 'Bdend'],
    'apicdend': ['Adend1', 'Adend2', 'Adend3'],
    'perisom':  ['soma']}

for label, p in reducedCells.items():  # create cell rules that were not loaded 
    if label not in loadCellParams:
        cellRule = netParams.importCellParams(label=label, conds={'cellType': label[0:2], 'cellModel': 'HH_reduced', 'ynorm': layer[p['layer']]},
        fileName='cells/'+p['cname']+'.py', cellName=p['cname'], cellArgs={'params': p['carg']} if p['carg'] else None)
        dendL = (layer[p['layer']][0]+(layer[p['layer']][1]-layer[p['layer']][0])/2.0) * cfg.sizeY  # adapt dend L based on layer
        for secName in ['Adend1', 'Adend2', 'Adend3', 'Bdend']: cellRule['secs'][secName]['geom']['L'] = dendL / 3.0  # update dend L
        for k,v in reducedSecList.items(): cellRule['secLists'][k] = v  # add secLists
        netParams.addCellParamsWeightNorm(label, 'conn/'+label+'_weightNorm.pkl', threshold=cfg.weightNormThreshold)  # add weightNorm

        # set 3d points
        offset, prevL = 0, 0
        somaL = netParams.cellParams[label]['secs']['soma']['geom']['L']
        for secName, sec in netParams.cellParams[label]['secs'].items():
            sec['geom']['pt3d'] = []
            if secName in ['soma', 'Adend1', 'Adend2', 'Adend3']:  # set 3d geom of soma and Adends
                sec['geom']['pt3d'].append([offset+0, prevL, 0, sec['geom']['diam']])
                prevL = float(prevL + sec['geom']['L'])
                sec['geom']['pt3d'].append([offset+0, prevL, 0, sec['geom']['diam']])
            if secName in ['Bdend']:  # set 3d geom of Bdend
                sec['geom']['pt3d'].append([offset+0, somaL, 0, sec['geom']['diam']])
                sec['geom']['pt3d'].append([offset+sec['geom']['L'], somaL, 0, sec['geom']['diam']])        
            if secName in ['axon']:  # set 3d geom of axon
                sec['geom']['pt3d'].append([offset+0, 0, 0, sec['geom']['diam']])
                sec['geom']['pt3d'].append([offset+0, -sec['geom']['L'], 0, sec['geom']['diam']])   

        if saveCellParams: netParams.saveCellParamsRule(label=label, fileName='cells/'+label+'_cellParams.pkl')


#------------------------------------------------------------------------------
## PT5B full cell model params (700+ comps)
#UC Davis PT Cell

if 'PT5B_full' not in loadCellParams:
    # import cell model from NEURON/python code
    netParams.importCellParams('PT5B_full', '../cells/Neuron_Model_12HH16HH/Na12HH16HHModel_TF.py', 'Na12Model_TF')

    # rename soma to conform to netpyne standard
    netParams.renameCellParamsSec(label='PT5B_full', oldSec='soma_0', newSec='soma')

    # set variable so easier to work with below
    cellRule = netParams.cellParams['PT5B_full']

    # set the spike generation location to the axon (default in NEURON is the soma)
    cellRule['secs']['axon_0']['spikeGenLoc'] = 0.5

    # add pt3d for axon sections so SecList does not break
    cellRule['secs']['axon_0']['geom']['pt3d'] = [[-25.435224533081055, 34.14994812011719, 0, 1.6440753936767578],
                                                  [-25.065839767456055, 34.10675811767578, 0, 1.6440753936767578],
                                                  [-24.327072143554688, 34.02037811279297, 0, 1.6440753936767578],
                                                  [-23.588302612304688, 33.933998107910156, 0, 1.6440753936767578],
                                                  [-22.849533081054688, 33.847618103027344, 0, 1.6440753936767578],
                                                  [-22.11076545715332, 33.7612419128418, 0, 1.6440753936767578],
                                                  [-21.37199592590332, 33.674861907958984, 0, 1.6440753936767578],
                                                  [-20.63322639465332, 33.58848190307617, 0, 1.6440753936767578],
                                                  [-19.894458770751953, 33.50210189819336, 0, 1.6440753936767578],
                                                  [-19.155689239501953, 33.41572189331055, 0, 1.6440753936767578],
                                                  [-18.416919708251953, 33.329341888427734, 0, 1.6440753936767578],
                                                  [-17.678152084350586, 33.24296188354492, 0, 1.6440753936767578],
                                                  [-16.939382553100586, 33.15658187866211, 0, 1.6440753936767578],
                                                  [-16.200613021850586, 33.0702018737793, 0, 1.6440753936767578],
                                                  [-15.461844444274902, 32.98382568359375, 0, 1.6440753936767578],
                                                  [-14.723075866699219, 32.89744567871094, 0, 1.6440753936767578],
                                                  [-13.984307289123535, 32.811065673828125, 0, 1.6440753936767578],
                                                  [-13.245537757873535, 32.72468566894531, 0, 1.6440753936767578],
                                                  [-12.506769180297852, 32.6383056640625, 0, 1.6440753936767578],
                                                  [-11.768000602722168, 32.55192565917969, 0, 1.6440753936767578],
                                                  [-11.029231071472168, 32.465545654296875, 0, 1.6440753936767578],
                                                  [-10.290462493896484, 32.37916564941406, 0, 1.6440753936767578],
                                                  [-9.5516939163208, 32.29278564453125, 0, 1.6440753936767578],
                                                  [-8.8129243850708, 32.2064094543457, 0, 1.6440753936767578],
                                                  [-8.074155807495117, 32.12002944946289, 0, 1.6440753936767578],
                                                  [-7.335386753082275, 32.03364944458008, 0, 1.6440753936767578],
                                                  [-6.596618175506592, 31.947269439697266, 0, 1.6440753936767578],
                                                  [-5.85784912109375, 31.860889434814453, 0, 1.6440753936767578],
                                                  [-5.119080066680908, 31.77450942993164, 0, 1.6440753936767578],
                                                  [-4.380311489105225, 31.68813133239746, 0, 1.6440753936767578],
                                                  [-3.641542434692383, 31.60175132751465, 0, 1.6440753936767578],
                                                  [-2.90277361869812, 31.515371322631836, 0, 1.6440753936767578],
                                                  [-2.1640045642852783, 31.428991317749023, 0, 1.6440753936767578],
                                                  [-1.4252357482910156, 31.342613220214844, 0, 1.6440753936767578],
                                                  [-0.6864668726921082, 31.25623321533203, 0, 1.6440753936767578],
                                                  [0.05230199918150902, 31.16985321044922, 0, 1.6440753936767578],
                                                  [0.7910708785057068, 31.083473205566406, 0, 1.6440753936767578],
                                                  [1.5298397541046143, 30.997093200683594, 0, 1.6440753936767578],
                                                  [2.268608570098877, 30.910715103149414, 0, 1.6440753936767578],
                                                  [3.0073776245117188, 30.8243350982666, 0, 1.6440753936767578],
                                                  [3.7461464405059814, 30.73795509338379, 0, 1.6440753936767578],
                                                  [4.484915256500244, 30.651575088500977, 0, 1.6440753936767578],
                                                  [5.223684310913086, 30.565196990966797, 0, 1.6440753936767578],
                                                  [5.9624528884887695, 30.478816986083984, 0, 1.6440753936767578],
                                                  [6.701221942901611, 30.392436981201172, 0, 1.6440753936767578],
                                                  [7.439990997314453, 30.30605697631836, 0, 1.6440753936767578],
                                                  [8.178759574890137, 30.21967887878418, 0, 1.6440753936767578],
                                                  [8.91752815246582, 30.133298873901367, 0, 1.6440753936767578],
                                                  [9.65629768371582, 30.046918869018555, 0, 1.6440753936767578],
                                                  [10.395066261291504, 29.960538864135742, 0, 1.6440753936767578],
                                                  [11.133834838867188, 29.87415885925293, 0, 1.6440753936767578],
                                                  [11.872604370117188, 29.78778076171875, 0, 1.6440753936767578],
                                                  [12.611372947692871, 29.701400756835938, 0, 1.6440753936767578],
                                                  [13.350141525268555, 29.615020751953125, 0, 1.6440753936767578],
                                                  [14.088911056518555, 29.528640747070312, 0, 1.6440753936767578],
                                                  [14.827679634094238, 29.442262649536133, 0, 1.6440753936767578],
                                                  [15.566448211669922, 29.35588264465332, 0, 1.6440753936767578],
                                                  [16.305217742919922, 29.269502639770508, 0, 1.6440753936767578],
                                                  [17.043987274169922, 29.183122634887695, 0, 1.6440753936767578],
                                                  [17.78275489807129, 29.096744537353516, 0, 1.6440753936767578],
                                                  [18.52152442932129, 29.010364532470703, 0, 1.6440753936767578],
                                                  [19.260292053222656, 28.92398452758789, 0, 1.6440753936767578],
                                                  [19.999061584472656, 28.837604522705078, 0, 1.6440753936767578],
                                                  [20.737831115722656, 28.751224517822266, 0, 1.6440753936767578],
                                                  [21.476598739624023, 28.664846420288086, 0, 1.6440753936767578],
                                                  [22.215368270874023, 28.578466415405273, 0, 1.6440753936767578],
                                                  [22.954137802124023, 28.49208641052246, 0, 1.6440753936767578],
                                                  [23.69290542602539, 28.40570640563965, 0, 1.6440753936767578],
                                                  [24.43167495727539, 28.31932830810547, 0, 1.6440753936767578],
                                                  [25.17044448852539, 28.232948303222656, 0, 1.6440753936767578],
                                                  [25.909212112426758, 28.146568298339844, 0, 1.6440753936767578],
                                                  [26.647981643676758, 28.06018829345703, 0, 1.6440753936767578],
                                                  [27.386751174926758, 27.97381019592285, 0, 1.6440753936767578],
                                                  [28.125518798828125, 27.88743019104004, 0, 1.6440753936767578],
                                                  [28.864288330078125, 27.801050186157227, 0, 1.6440753936767578],
                                                  [29.603057861328125, 27.714670181274414, 0, 1.6440753936767578],
                                                  [30.341825485229492, 27.6282901763916, 0, 1.6440753936767578],
                                                  [31.080595016479492, 27.541912078857422, 0, 1.6440753936767578],
                                                  [31.819364547729492, 27.45553207397461, 0, 1.6440753936767578],
                                                  [32.55813217163086, 27.369152069091797, 0, 1.6440753936767578],
                                                  [33.29690170288086, 27.282772064208984, 0, 1.6440753936767578],
                                                  [34.03567123413086, 27.196393966674805, 0, 1.6440753936767578],
                                                  [34.77444076538086, 27.110013961791992, 0, 1.6440753936767578],
                                                  [35.51321029663086, 27.02363395690918, 0, 1.6440753936767578],
                                                  [36.251976013183594, 26.937253952026367, 0, 1.6440753936767578],
                                                  [36.990745544433594, 26.850875854492188, 0, 1.6440753936767578],
                                                  [37.729515075683594, 26.764495849609375, 0, 1.6440753936767578],
                                                  [38.468284606933594, 26.678115844726562, 0, 1.6440753936767578],
                                                  [39.207054138183594, 26.59173583984375, 0, 1.6440753936767578],
                                                  [39.945823669433594, 26.505355834960938, 0, 1.6440753936767578],
                                                  [40.68458938598633, 26.418977737426758, 0, 1.6440753936767578],
                                                  [41.42335891723633, 26.332597732543945, 0, 1.6440753936767578],
                                                  [42.16212844848633, 26.246217727661133, 0, 1.6440753936767578],
                                                  [42.90089797973633, 26.15983772277832, 0, 1.6440753936767578],
                                                  [43.63966751098633, 26.07345962524414, 0, 1.6440753936767578],
                                                  [44.37843322753906, 25.987079620361328, 0, 1.6440753936767578],
                                                  [45.11720275878906, 25.900699615478516, 0, 1.6440753936767578],
                                                  [45.85597229003906, 25.814319610595703, 0, 1.6440753936767578],
                                                  [46.59474182128906, 25.727941513061523, 0, 1.6440753936767578],
                                                  [47.33351135253906, 25.64156150817871, 0, 1.6440753936767578],
                                                  [48.07228088378906, 25.5551815032959, 0, 1.6440753936767578],
                                                  [48.8110466003418, 25.468801498413086, 0, 1.6440753936767578],
                                                  [49.5498161315918, 25.382421493530273, 0, 1.6440753936767578],
                                                  [50.2885856628418, 25.296043395996094, 0, 1.6440753936767578],
                                                  [51.0273551940918, 25.20966339111328, 0, 1.6440753936767578],
                                                  [51.7661247253418, 25.12328338623047, 0, 1.6440753936767578],
                                                  [52.5048942565918, 25.036903381347656, 0, 1.6440753936767578],
                                                  [53.24365997314453, 24.950525283813477, 0, 1.6440753936767578],
                                                  [53.98242950439453, 24.864145278930664, 0, 1.6440753936767578],
                                                  [54.72119903564453, 24.77776527404785, 0, 1.6440753936767578],
                                                  [55.45996856689453, 24.69138526916504, 0, 1.6440753936767578],
                                                  [56.19873809814453, 24.60500717163086, 0, 1.6440753936767578],
                                                  [56.93750762939453, 24.518627166748047, 0, 1.6440753936767578],
                                                  [57.676273345947266, 24.432247161865234, 0, 1.6440753936767578],
                                                  [58.415042877197266, 24.345867156982422, 0, 1.6440753936767578],
                                                  [59.153812408447266, 24.25948715209961, 0, 1.6440753936767578],
                                                  [59.892581939697266, 24.17310905456543, 0, 1.6440753936767578],
                                                  [60.631351470947266, 24.086729049682617, 0, 1.6440753936767578],
                                                  [61.370121002197266, 24.000349044799805, 0, 1.6440753936767578],
                                                  [62.10888671875, 23.913969039916992, 0, 1.6440753936767578],
                                                  [62.84765625, 23.827590942382812, 0, 1.6440753936767578],
                                                  [63.58642578125, 23.7412109375, 0, 1.6440753936767578],
                                                  [63.955810546875, 23.698020935058594, 0, 1.6440753936767578]]
    cellRule['secs']['axon_1']['geom']['pt3d'] = [[63.955810546875, 23.698020935058594, 0, 1.6440753936767578],
                                                  [65.31021881103516, 23.539657592773438, 0, 1.6440753936767578],
                                                  [68.01904296875, 23.222932815551758, 0, 1.6440753936767578],
                                                  [70.72785949707031, 22.906208038330078, 0, 1.6440753936767578],
                                                  [73.43667602539062, 22.5894832611084, 0, 1.6440753936767578],
                                                  [76.14550018310547, 22.27275848388672, 0, 1.6440753936767578],
                                                  [78.85431671142578, 21.956031799316406, 0, 1.6440753936767578],
                                                  [81.5631332397461, 21.639307022094727, 0, 1.6440753936767578],
                                                  [84.27195739746094, 21.322582244873047, 0, 1.6440753936767578],
                                                  [86.98077392578125, 21.005857467651367, 0, 1.6440753936767578],
                                                  [89.68959045410156, 20.689132690429688, 0, 1.6440753936767578],
                                                  [92.3984146118164, 20.372407913208008, 0, 1.6440753936767578],
                                                  [93.75282287597656, 20.21404457092285, 0, 1.6440753936767578]]

    #define cell conds
    netParams.cellParams['PT5B_full']['conds'] = {'cellModel': 'HH_full', 'cellType': 'PT'}

    # clean secLists from Tim's code
    cellRule['secLists'] = {}

    # create lists useful to define location of synapses
    nonSpiny = ['apic_0', 'apic_1']
    netParams.addCellParamsSecList(label='PT5B_full', secListName='perisom', somaDist=[0, 50])  # sections within 50 um of soma
    netParams.addCellParamsSecList(label='PT5B_full', secListName='below_soma', somaDistY=[-600, 0])  # sections within 0-300 um of soma
    cellRule['secLists']['alldend'] = [sec for sec in cellRule.secs if ('dend' in sec or 'apic' in sec)] # basal+apical
    cellRule['secLists']['apicdend'] = [sec for sec in cellRule.secs if ('apic' in sec)] # apical
    cellRule['secLists']['spiny'] = [sec for sec in cellRule['secLists']['alldend'] if sec not in nonSpiny]

    for sec in nonSpiny: # N.B. apic_1 not in `perisom` . `apic_0` and `apic_114` are
        if sec in cellRule['secLists']['perisom']: # fixed logic
            cellRule['secLists']['perisom'].remove(sec)

    # Decrease dendritic Na
    #for secName in netParams.cellParams['PT5B_full']['secs']:
        #if secName.startswith('apic'):
            #print(netParams.cellParams['PT5B_full']['secs'][secName]['mechs']['na12mut'])
            #print(netParams.cellParams['PT5B_full']['secs'][secName]['mechs']['na12'])
            #netParams.cellParams['PT5B_full']['secs'][secName]['mechs']['na12'] = cfg.dendNa
            #netParams.cellParams['PT5B_full']['secs'][secName]['mechs']['na12mut'] = cfg.dendNa

    # Change params for UCDAVIS mutants
    #for secName in netParams.cellParams['PT5B_full']['secs']: #decrease dendritic nav1.2
        #if secName.startswith('apic'):
            #netParams.cellParams['PT5B_full']['secs'][secName]['na12mut'] = {'mod': 'na12', 'gbar': 1e-5}

    #def csv_to_dict(filepath):
        #result = {}
        #with open(filepath, mode='r', newline='') as file:
            #reader = csv.DictReader(file)
            #fieldnames = reader.fieldnames
            #key_field = fieldnames[0]  # Use the first column as key
            #for row in reader:
                #key = row[key_field]
                #value = {k: v for k, v in row.items() if k != key_field}
                #result[key] = value
        #return result

    #Load CSV with Mutant Params
    if cfg.loadmutantParams == True:
        variants = csv_to_dict('MutantParameters_updated_050625.csv')
        for secName in netParams.cellParams:  # mutant R119I
            netParams.cellParams['PT5B_full']['secs'][secName]['na12mut'] = variants[cfg.variant]

    #To change params manually
    #for secName in netParams.cellParams: #mutant R119I
        #netParams.cellParams['PT5B_full']['secs']['PT5B_full']['secs'][secName]['na12mut'] = \
            #{'mod': 'na12mut', 'Ra': 0.19953217, 'Rb': 0.09365142, 'Rd': 0.02022166, 'Rg': 0.01116065, 'a0s': 0.0000775,
             #'gms': 0.141628828, 'hmin': 0.011878279, 'mmin': 0.02378683, 'q10': 1.75422509,
            # 'qa': 3.28099731, 'qd': 0.90335573, 'qg': 2.14380902, 'qinf': 6.3951063, 'sh': 9.10593486,
             #'smax': 5.63912804, 'tha': -37.025873, 'thi1': -78.898604, 'thi2': -64.498989, 'thinf': -53.104936,
             #'vhalfs': -63.652573, 'vvh': -44.61452, 'vvs': 1.6172257, 'zetas': 14.3424517}

    # set weight normalization
    netParams.addCellParamsWeightNorm('PT5B_full', '../conn/PT5B_full_weightNorm.pkl', threshold=cfg.weightNormThreshold)  # load weight norm

    # save to json with all the above modifications so easier/faster to load
    if saveCellParams: netParams.saveCellParamsRule(label='PT5B_full', fileName='../cells/PT5B_full_cellParams.pkl')

else:
    #load existing params
    netParams.loadCellParams('PT5B_full', '../cells/PT5B_full_cellParams.pkl')

    # set weight normalization
    netParams.addCellParamsWeightNorm('PT5B_full', '../conn/PT5B_full_weightNorm.pkl',
                                      threshold=cfg.weightNormThreshold)

#------------------------------------------------------------------------------
## IT5A full cell model params (700+ comps)
if 'IT5A_full' not in loadCellParams:
    cellRule = netParams.importCellParams(label='IT5A_full', conds={'cellType': 'IT', 'cellModel': 'HH_full', 'ynorm': layer['5A']},
      fileName='cells/ITcell.py', cellName='ITcell', cellArgs={'params': 'BS1579'}, somaAtOrigin=True)
    netParams.renameCellParamsSec(label='IT5A_full', oldSec='soma_0', newSec='soma')
    netParams.addCellParamsWeightNorm('IT5A_full', 'conn/IT_full_BS1579_weightNorm.pkl', threshold=cfg.weightNormThreshold) # add weightNorm before renaming soma_0
    netParams.addCellParamsSecList(label='IT5A_full', secListName='perisom', somaDist=[0, 50])  # sections within 50 um of soma
    cellRule['secLists']['alldend'] = [sec for sec in cellRule.secs if ('dend' in sec or 'apic' in sec)] # basal+apical
    cellRule['secLists']['apicdend'] = [sec for sec in cellRule.secs if ('apic' in sec)] # basal+apical
    cellRule['secLists']['spiny'] = [sec for sec in cellRule['secLists']['alldend'] if sec not in ['apic_0', 'apic_1']]
    # Adapt K gbar
    for secName in cellRule['secs']:
        for kmech in [k for k in cellRule['secs'][secName]['mechs'].keys() if k.startswith('k') and k!='kBK']:
            cellRule['secs'][secName]['mechs'][kmech]['gbar'] *= cfg.KgbarFactor 
    if saveCellParams: netParams.saveCellParamsRule(label='IT5A_full', fileName='cells/IT5A_full_cellParams.pkl')


#------------------------------------------------------------------------------
## IT5B full cell model params (700+ comps) - not used
# if 'IT5B_full' not in loadCellParams:
#   cellRule = netParams.importCellParams(label='IT5B_full', conds={'cellType': 'IT', 'cellModel': 'HH_full', 'ynorm': layer['5B']},
#     fileName='cells/ITcell.py', cellName='ITcell', cellArgs={'params': 'BS1579'}, somaAtOrigin=True)
#   netParams.addCellParamsSecList(label='IT5B_full', secListName='perisom', somaDist=[0, 50])  # sections within 50 um of soma
#   cellRule['secLists']['alldend'] = [sec for sec in cellRule.secs if ('dend' in sec or 'apic' in sec)] # basal+apical
#   cellRule['secLists']['apicdend'] = [sec for sec in cellRule.secs if ('apic' in sec)] # basal+apical
#   cellRule['secLists']['spiny'] = [sec for sec in cellRule['secLists']['alldend'] if sec not in ['apic_0', 'apic_1']]
#   netParams.addCellParamsWeightNorm('IT5B_full', 'conn/IT_full_BS1579_weightNorm.pkl')
#   netParams.saveCellParamsRule(label='IT5B_full', fileName='cells/IT5B_full_cellParams.pkl')


#------------------------------------------------------------------------------
## PV cell params (3-comp)
if 'PV_simple' not in loadCellParams:
    cellRule = netParams.importCellParams(label='PV_simple', conds={'cellType':'PV', 'cellModel':'HH_simple'}, 
      fileName='cells/FS3.hoc', cellName='FScell1', cellInstance = True)
    cellRule['secLists']['spiny'] = ['soma', 'dend']
    netParams.addCellParamsWeightNorm('PV_simple', 'conn/PV_simple_weightNorm.pkl', threshold=cfg.weightNormThreshold)
    if saveCellParams: netParams.saveCellParamsRule(label='PV_simple', fileName='cells/PV_simple_cellParams.pkl')


#------------------------------------------------------------------------------
## SOM cell params (3-comp)
if 'SOM_simple' not in loadCellParams:
    cellRule = netParams.importCellParams(label='SOM_simple', conds={'cellType':'SOM', 'cellModel':'HH_simple'}, 
      fileName='cells/LTS3.hoc', cellName='LTScell1', cellInstance = True)
    cellRule['secLists']['spiny'] = ['soma', 'dend']
    netParams.addCellParamsWeightNorm('SOM_simple', 'conn/SOM_simple_weightNorm.pkl', threshold=cfg.weightNormThreshold)
    if saveCellParams: netParams.saveCellParamsRule(label='SOM_simple', fileName='cells/SOM_simple_cellParams.pkl')




#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
## load densities
with open('../cells/cellDensity.pkl', 'rb') as fileObj: density = pickle.load(fileObj)['density']

## Local populations

netParams.popParams['IT2']  =   {'cellModel': cfg.cellmod['IT2'],  'cellType': 'IT', 'ynormRange': layer['2'], 'density': density[('M1','E')][0]}
netParams.popParams['SOM2'] =   {'cellModel': 'HH_simple',         'cellType': 'SOM','ynormRange': layer['24'], 'density': density[('M1','SOM')][5]}
netParams.popParams['PV2']  =   {'cellModel': 'HH_simple',         'cellType': 'PV', 'ynormRange': layer['24'], 'density': density[('M1','PV')][5]}
netParams.popParams['IT4']  =   {'cellModel': cfg.cellmod['IT4'],  'cellType': 'IT', 'ynormRange': layer['4'], 'density': density[('M1','E')][1]}
netParams.popParams['IT5A'] =   {'cellModel': cfg.cellmod['IT5A'], 'cellType': 'IT', 'ynormRange': layer['5A'], 'density': density[('M1','E')][2]}
netParams.popParams['SOM5A'] =  {'cellModel': 'HH_simple',         'cellType': 'SOM','ynormRange': layer['5A'], 'density': density[('M1','SOM')][2]} #changed
netParams.popParams['PV5A']  =  {'cellModel': 'HH_simple',         'cellType': 'PV', 'ynormRange': layer['5A'], 'density': density[('M1','PV')][2]}
netParams.popParams['IT5B'] =   {'cellModel': cfg.cellmod['IT5B'], 'cellType': 'IT', 'ynormRange': layer['5B'], 'density': 0.5*density[('M1','E')][3]}
netParams.popParams['PT5B'] =   {'cellModel': cfg.cellmod['PT5B'], 'cellType': 'PT', 'ynormRange': layer['5B'], 'density': 0.5*density[('M1','E')][3]}
netParams.popParams['SOM5B'] =  {'cellModel': 'HH_simple',         'cellType': 'SOM','ynormRange': layer['5B'], 'density': density[('M1','SOM')][3]}
netParams.popParams['PV5B']  =  {'cellModel': 'HH_simple',         'cellType': 'PV', 'ynormRange': layer['5B'], 'density': density[('M1','PV')][3]}
netParams.popParams['IT6']  =   {'cellModel': cfg.cellmod['IT6'],  'cellType': 'IT', 'ynormRange': layer['6'],  'density': 0.5*density[('M1','E')][4]}
netParams.popParams['CT6']  =   {'cellModel': cfg.cellmod['CT6'],  'cellType': 'CT', 'ynormRange': layer['6'],  'density': 0.5*density[('M1','E')][4]}
netParams.popParams['SOM6'] =   {'cellModel': 'HH_simple',         'cellType': 'SOM','ynormRange': layer['6'],  'density': density[('M1','SOM')][4]} #changed
netParams.popParams['PV6']  =   {'cellModel': 'HH_simple',         'cellType': 'PV', 'ynormRange': layer['6'],  'density': density[('M1','PV')][4]}

if cfg.singleCellPops:
    for pop in netParams.popParams.values(): pop['numCells'] = 1

#------------------------------------------------------------------------------
## Long-range input populations (VecStims)
if cfg.addLongConn:
    ## load experimentally based parameters for long range inputs
    with open('../conn/conn_long.pkl', 'rb') as fileObj: connLongData = pickle.load(fileObj)
    #ratesLong = connLongData['rates']

    numCells = cfg.numCellsLong
    noise = cfg.noiseLong
    start = cfg.startLong

    longPops = ['TPO', 'TVL', 'S1', 'S2', 'cM1', 'M2', 'OC']
    ## create populations with fixed 
    for longPop in longPops:
        netParams.popParams[longPop] = {'cellModel': 'VecStim', 'numCells': numCells, 'rate': cfg.ratesLong[longPop], 
                                        'noise': noise, 'start': start, 'pulses': [], 'ynormRange': layer['long'+longPop]}
        if isinstance(cfg.ratesLong[longPop], str): # filename to load spikes from
            spikesFile = cfg.ratesLong[longPop]
            with open(spikesFile, 'r') as f: spks = json.load(f)
            netParams.popParams[longPop].pop('rate')
            netParams.popParams[longPop]['spkTimes'] = spks


#------------------------------------------------------------------------------
# Synaptic mechanism parameters
#------------------------------------------------------------------------------
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': 15, 'tau2NMDA': 150, 'e': 0}
netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.05, 'tau2': 5.3*cfg.AMPATau2Factor, 'e': 0}
netParams.synMechParams['GABAB'] = {'mod':'MyExp2SynBB', 'tau1': 3.5, 'tau2': 260.9, 'e': -93} 
netParams.synMechParams['GABAA'] = {'mod':'MyExp2SynBB', 'tau1': 0.07, 'tau2': 18.2, 'e': -80}
netParams.synMechParams['GABAASlow'] = {'mod': 'MyExp2SynBB','tau1': 2, 'tau2': 100, 'e': -80}
netParams.synMechParams['GABAASlowSlow'] = {'mod': 'MyExp2SynBB', 'tau1': 200, 'tau2': 400, 'e': -80}

ESynMech = ['AMPA', 'NMDA']
SOMESynMech = ['GABAASlow','GABAB']
SOMISynMech = ['GABAASlow']
PVSynMech = ['GABAA']


#------------------------------------------------------------------------------
# Long range input pulses
#------------------------------------------------------------------------------
if cfg.addPulses:
    for key in [k for k in dir(cfg) if k.startswith('pulse')]:
        params = getattr(cfg, key, None)
        [pop, start, end, rate, noise] = [params[s] for s in ['pop', 'start', 'end', 'rate', 'noise']]
        if 'duration' in params and params['duration'] is not None and params['duration'] > 0:
            end = start + params['duration']

        if pop in netParams.popParams:
            if 'pulses' not in netParams.popParams[pop]: netParams.popParams[pop]['pulses'] = {}    
            netParams.popParams[pop]['pulses'].append({'start': start, 'end': end, 'rate': rate, 'noise': noise})



#------------------------------------------------------------------------------
# Current inputs (IClamp)
#------------------------------------------------------------------------------
if cfg.addIClamp:
    for key in [k for k in dir(cfg) if k.startswith('IClamp')]:
        params = getattr(cfg, key, None)
        [pop,sec,loc,start,dur,amp] = [params[s] for s in ['pop','sec','loc','start','dur','amp']]

        #cfg.analysis['plotTraces']['include'].append((pop,0))  # record that pop

        # add stim source
        netParams.stimSourceParams[key] = {'type': 'IClamp', 'delay': start, 'dur': dur, 'amp': amp}
        
        # connect stim source to target
        netParams.stimTargetParams[key+'_'+pop] =  {
            'source': key, 
            'conds': {'pop': pop},
            'sec': sec, 
            'loc': loc}

#------------------------------------------------------------------------------
# NetStim inputs
#------------------------------------------------------------------------------
if cfg.addNetStim:
    for key in [k for k in dir(cfg) if k.startswith('NetStim')]:
        params = getattr(cfg, key, None)
        [pop, ynorm, sec, loc, synMech, synMechWeightFactor, start, interval, noise, number, weight, delay] = \
        [params[s] for s in ['pop', 'ynorm', 'sec', 'loc', 'synMech', 'synMechWeightFactor', 'start', 'interval', 'noise', 'number', 'weight', 'delay']] 

        # cfg.analysis['plotTraces']['include'] = [(pop,0)]

        if synMech == ESynMech:
            wfrac = cfg.synWeightFractionEE
        elif synMech == SOMESynMech:
            wfrac = cfg.synWeightFractionSOME
        else:
            wfrac = [1.0]

        # add stim source
        netParams.stimSourceParams[key] = {'type': 'NetStim', 'start': start, 'interval': interval, 'noise': noise, 'number': number}

        # connect stim source to target
        # for i, syn in enumerate(synMech):
        netParams.stimTargetParams[key+'_'+pop] =  {
            'source': key, 
            'conds': {'pop': pop, 'ynorm': ynorm},
            'sec': sec, 
            'loc': loc,
            'synMech': synMech,
            'weight': weight,
            'synMechWeightFactor': synMechWeightFactor,
            'delay': delay}

#------------------------------------------------------------------------------
# Local connectivity parameters
#------------------------------------------------------------------------------
with open('../conn/conn.pkl', 'rb') as fileObj: connData = pickle.load(fileObj)
pmat = connData['pmat']
wmat = connData['wmat']
bins = connData['bins']
#import conn_param
# pmat = conn_param.pmat
# wmat = conn_param.wmat
# bins = conn_param.bins

#------------------------------------------------------------------------------
## E -> E
if cfg.addConn and cfg.EEGain > 0.0:
    labelsConns = [('W+AS_norm', 'IT', 'L2/3,4'), ('W+AS_norm', 'IT', 'L5A,5B'), 
                   ('W+AS_norm', 'PT', 'L5B'), ('W+AS_norm', 'IT', 'L6'), ('W+AS_norm', 'CT', 'L6')]
    labelPostBins = [('W+AS', 'IT', 'L2/3,4'), ('W+AS', 'IT', 'L5A,5B'), ('W+AS', 'PT', 'L5B'), 
                    ('W+AS', 'IT', 'L6'), ('W+AS', 'CT', 'L6')]
    labelPreBins = ['W', 'AS', 'AS', 'W', 'W']
    preTypes = [['IT'], ['IT'], ['IT', 'PT'], ['IT','CT'], ['IT','CT']] 
    postTypes = ['IT', 'IT', 'PT', 'IT','CT']
    ESynMech = ['AMPA','NMDA']

    for i,(label, preBinLabel, postBinLabel) in enumerate(zip(labelsConns,labelPreBins, labelPostBins)):
        for ipre, preBin in enumerate(bins[preBinLabel]):
            for ipost, postBin in enumerate(bins[postBinLabel]):
                for cellModel in cellModels:
                    ruleLabel = 'EE_'+cellModel+'_'+str(i)+'_'+str(ipre)+'_'+str(ipost)
                    netParams.connParams[ruleLabel] = { 
                        'preConds': {'cellType': preTypes[i], 'ynorm': list(preBin)}, 
                        'postConds': {'cellModel': cellModel, 'cellType': postTypes[i], 'ynorm': list(postBin)},
                        'synMech': ESynMech,
                        'probability': pmat[label][ipost,ipre],
                        'weight': wmat[label][ipost,ipre] * cfg.EEGain / cfg.synsperconn[cellModel], 
                        'synMechWeightFactor': cfg.synWeightFractionEE,
                        'delay': 'defaultDelay+dist_3D/propVelocity',
                        'synsPerConn': cfg.synsperconn[cellModel],
                        'sec': 'spiny'}
            

#------------------------------------------------------------------------------
## E -> I
if cfg.EIGain: # Use IEGain if value set
    cfg.EPVGain = cfg.EIGain
    cfg.ESOMGain = cfg.EIGain
else: 
    cfg.EIGain = (cfg.EPVGain+cfg.ESOMGain)/2.0

if cfg.addConn and (cfg.EPVGain > 0.0 or cfg.ESOMGain > 0.0):
    labelsConns = ['FS', 'LTS']
    labelPostBins = ['FS/LTS', 'FS/LTS']
    labelPreBins = ['FS/LTS', 'FS/LTS']
    preTypes = ['IT', 'PT', 'CT']
    postTypes = ['PV', 'SOM']
    ESynMech = ['AMPA','NMDA']
    lGain = [cfg.EPVGain, cfg.ESOMGain] # E -> PV or E -> SOM
    for i,(label, preBinLabel, postBinLabel) in enumerate(zip(labelsConns,labelPreBins, labelPostBins)):
        for ipre, preBin in enumerate(bins[preBinLabel]):
            for ipost, postBin in enumerate(bins[postBinLabel]):
                ruleLabel = 'EI_'+str(i)+'_'+str(ipre)+'_'+str(ipost)
                netParams.connParams[ruleLabel] = {
                    'preConds': {'cellType': preTypes, 'ynorm': list(preBin)},
                    'postConds': {'cellType': postTypes[i], 'ynorm': list(postBin)},
                    'synMech': ESynMech,
                    'probability': pmat[label][ipost,ipre],
                    'weight': wmat[label][ipost,ipre] * lGain[i],
                    'synMechWeightFactor': cfg.synWeightFractionEI,
                    'delay': 'defaultDelay+dist_3D/propVelocity',
                    'sec': 'soma'} # simple I cells used right now only have soma



#------------------------------------------------------------------------------
## I -> all
if cfg.IEGain: # Use IEGain if value set
    cfg.PVEGain = cfg.IEGain
    cfg.SOMEGain = cfg.IEGain
else: 
    cfg.IEGain = (cfg.PVEGain+cfg.SOMEGain)/2.0

if cfg.IIGain:  # Use IIGain if value set
    cfg.SOMPVGain = cfg.IIGain
    cfg.PVSOMGain = cfg.IIGain
    cfg.SOMSOMGain = cfg.IIGain
    cfg.PVPVGain = cfg.IIGain
else:
    cfg.IIGain = (cfg.PVSOMGain+cfg.SOMPVGain+cfg.SOMSOMGain+cfg.PVPVGain)/4.0

if cfg.addConn and (cfg.IEGain > 0.0 or cfg.IIGain > 0.0):
    # Local, intralaminar only; all-to-all but distance-based; high weights; L5A/B->L5A/B
    preCellTypes = ['SOM', 'SOM', 'SOM', 'PV', 'PV', 'PV']
    ynorms = [(layer['2'][0],layer['4'][1]), (layer['5A'][0],layer['5B'][1]), (layer['6'][0],layer['6'][1])]*2
    IEweights = cfg.IEweights * 2  # [I->E2/3+4, I->E5, I->E6] weights (Note * 2 is repeat list operator)
    IIweights = cfg.IIweights * 2  # [I->I2/3+4, I->I5, I->I6] weights (Note * 2 is repeat list operator)
    postCellTypes = ['PT', ['IT','CT'], 'PV', 'SOM']
    IEdisynBiases = [None, cfg.IEdisynapticBias, cfg.IEdisynapticBias, None, cfg.IEdisynapticBias, cfg.IEdisynapticBias]
    disynapticBias = None  # default, used for I->I

    # preCellTypes = ['SOM', 'PV']
    # ynorms = [[0,1]]*2
    # IEweights = cfg.IEweights * 2  # [I->E2/3+4, I->E5, I->E6] weights (Note * 2 is repeat list operator)
    # IIweights = cfg.IIweights * 2  # [I->I2/3+4, I->I5, I->I6] weights (Note * 2 is repeat list operator)
    # postCellTypes = ['PT', ['IT','CT'], 'PV', 'SOM']
    # IEdisynBiases = [cfg.IEdisynapticBias, cfg.IEdisynapticBias]
    # disynapticBias = None  # default, used for I->I

    for i,(preCellType, ynorm, IEweight, IIweight, IEdisynBias) in enumerate(zip(preCellTypes, ynorms, IEweights, IIweights, IEdisynBiases)):
        for ipost, postCellType in enumerate(postCellTypes):
            for cellModel in cellModels:
                if postCellType == 'PV':    # postsynaptic I cell
                    sec = 'soma'
                    synWeightFraction = [1]
                    if preCellType == 'PV':             # PV->PV
                        weight = IIweight * cfg.PVPVGain
                        synMech = PVSynMech
                    else:                           # SOM->PV
                        weight = IIweight * cfg.SOMPVGain
                        synMech = SOMISynMech
                elif postCellType == 'SOM': # postsynaptic I cell
                    sec = 'soma'
                    synWeightFraction = [1]
                    if preCellType == 'PV':             # PV->SOM
                        weight = IIweight * cfg.PVSOMGain
                        synMech = PVSynMech
                    else:                           # SOM->SOM
                        weight = IIweight * cfg.SOMSOMGain
                        synMech = SOMISynMech
                elif postCellType == ['IT','CT']: # postsynaptic IT,CT cell
                    disynapticBias = IEdisynBias
                    if preCellType == 'PV':             # PV->E
                        weight = IEweight * cfg.PVEGain
                        synMech = PVSynMech
                        sec = 'perisom'
                    else:                           # SOM->E
                        weight = IEweight * cfg.SOMEGain
                        synMech = SOMESynMech
                        sec = 'spiny'
                        synWeightFraction = cfg.synWeightFractionSOME
                elif postCellType == 'PT': # postsynaptic PT cell
                    disynapticBias = IEdisynBias
                    if preCellType == 'PV':             # PV->E
                        weight = IEweight * cfg.IPTGain * cfg.PVEGain
                        synMech = PVSynMech
                        sec = 'perisom'
                    else:                           # SOM->E
                        weight = IEweight * cfg.IPTGain * cfg.SOMEGain
                        synMech = SOMESynMech
                        sec = 'spiny'
                        synWeightFraction = cfg.synWeightFractionSOME
                if cellModel == 'HH_full':
                    weight = weight * cfg.IFullGain


                ruleLabel = 'I_'+cellModel+'_'+str(i)+'_'+str(ipost)
                netParams.connParams[ruleLabel] = {
                    'preConds': {'cellType': preCellType, 'ynorm': ynorm},
                    'postConds': {'cellModel': cellModel, 'cellType': postCellType, 'ynorm': ynorm},
                    'synMech': synMech,
                    'probability': '1.0 * exp(-dist_3D_border/probLambda)',
                    'weight': weight / cfg.synsperconn[cellModel],
                    'delay': 'defaultDelay+dist_3D_border/propVelocity',
                    'synsPerConn': cfg.synsperconn[cellModel],
                    'synMechWeightFactor': synWeightFraction,
                    'sec': sec,
                    'disynapticBias': disynapticBias}


#------------------------------------------------------------------------------
# Long-range  connectivity parameters
#------------------------------------------------------------------------------
if cfg.addLongConn:

    # load experimentally based parameters for long range inputs
    cmatLong = connLongData['cmat']
    binsLong = connLongData['bins']

    longPops = ['TPO', 'TVL', 'S1', 'S2', 'cM1', 'M2', 'OC']
    cellTypes = ['IT', 'PT', 'CT', 'PV', 'SOM']
    EorI = ['exc', 'inh']
    syns = {'exc': ESynMech, 'inh': 'GABAA'}
    synFracs = {'exc': cfg.synWeightFractionEE, 'inh': [1.0]}

    for longPop in longPops:
        for ct in cellTypes:
            for EorI in ['exc', 'inh']:
                for i, (binRange, convergence) in enumerate(zip(binsLong[(longPop, ct)], cmatLong[(longPop, ct, EorI)])):
                    for cellModel in cellModels:
                        ruleLabel = longPop+'_'+ct+'_'+EorI+'_'+cellModel+'_'+str(i)
                        netParams.connParams[ruleLabel] = { 
                            'preConds': {'pop': longPop}, 
                            'postConds': {'cellModel': cellModel, 'cellType': ct, 'ynorm': list(binRange)},
                            'synMech': syns[EorI],
                            'convergence': convergence,
                            'weight': cfg.weightLong[longPop] / cfg.synsperconn[cellModel],
                            'synMechWeightFactor': cfg.synWeightFractionEE,
                            'delay': 'defaultDelay+dist_3D/propVelocity',
                            'synsPerConn': cfg.synsperconn[cellModel],
                            'sec': 'spiny'}


#------------------------------------------------------------------------------
# Subcellular connectivity (synaptic distributions)
#------------------------------------------------------------------------------         
if cfg.addSubConn:
    with open('../conn/conn_dend_PT.json', 'r') as fileObj: connDendPTData = json.load(fileObj)
    with open('../conn/conn_dend_IT.json', 'r') as fileObj: connDendITData = json.load(fileObj)
    
    #------------------------------------------------------------------------------
    # L2/3,TVL,S2,cM1,M2 -> PT (Suter, 2015)
    lenY = 30 
    spacing = 50
    gridY = range(0, -spacing*lenY, -spacing)
    synDens, _, fixedSomaY = connDendPTData['synDens'], connDendPTData['gridY'], connDendPTData['fixedSomaY']
    for k in synDens.keys():
        prePop,postType = k.split('_')  # eg. split 'M2_PT'
        if prePop == 'L2': prePop = 'IT2'  # include conns from layer 2/3 and 4
        netParams.subConnParams[k] = {
        'preConds': {'pop': prePop}, 
        'postConds': {'cellType': postType},  
        'sec': 'spiny',
        'groupSynMechs': ESynMech, 
        'density': {'type': '1Dmap', 'gridX': None, 'gridY': gridY, 'gridValues': synDens[k], 'fixedSomaY': fixedSomaY}} 


    #------------------------------------------------------------------------------
    # TPO, TVL, M2, OC  -> E (L2/3, L5A, L5B, L6) (Hooks 2013)
    lenY = 26
    spacing = 50
    gridY = range(0, -spacing*lenY, -spacing)
    synDens, _, fixedSomaY = connDendITData['synDens'], connDendITData['gridY'], connDendITData['fixedSomaY']
    for k in synDens.keys():
        prePop,post = k.split('_')  # eg. split 'M2_L2'
        postCellTypes = ['IT','PT','CT'] if prePop in ['OC','TPO'] else ['IT','CT']  # only OC,TPO include PT cells
        postyRange = list(layer[post.split('L')[1]]) # get layer yfrac range 
        if post == 'L2': postyRange[1] = layer['4'][1]  # apply L2 rule also to L4 
        netParams.subConnParams[k] = {
        'preConds': {'pop': prePop}, 
        'postConds': {'ynorm': postyRange , 'cellType': postCellTypes},  
        'sec': 'spiny',
        'groupSynMechs': ESynMech, 
        'density': {'type': '1Dmap', 'gridX': None, 'gridY': gridY, 'gridValues': synDens[k], 'fixedSomaY': fixedSomaY}} 


    #------------------------------------------------------------------------------
    # S1, S2, cM1 -> E IT/CT; no data, assume uniform over spiny
    netParams.subConnParams['S1,S2,cM1->IT,CT'] = {
        'preConds': {'pop': ['S1','S2','cM1']}, 
        'postConds': {'cellType': ['IT','CT']},
        'sec': 'spiny',
        'groupSynMechs': ESynMech, 
        'density': 'uniform'} 


    #------------------------------------------------------------------------------
    # rest of local E->E (exclude IT2->PT); uniform distribution over spiny
    netParams.subConnParams['IT2->non-PT'] = {
        'preConds': {'pop': ['IT2']}, 
        'postConds': {'cellType': ['IT','CT']},
        'sec': 'spiny',
        'groupSynMechs': ESynMech, 
        'density': 'uniform'} 
        
    netParams.subConnParams['non-IT2->E'] = {
        'preConds': {'pop': ['IT4','IT5A','IT5B','PT5B','IT6','CT6']}, 
        'postConds': {'cellType': ['IT','PT','CT']},
        'sec': 'spiny',
        'groupSynMechs': ESynMech, 
        'density': 'uniform'} 


    #------------------------------------------------------------------------------
    # PV->E; perisomatic (no sCRACM)
    netParams.subConnParams['PV->E'] = {
        'preConds': {'cellType': 'PV'}, 
        'postConds': {'cellType': ['IT', 'CT', 'PT']},  
        'sec': 'perisom', 
        'density': 'uniform'} 


    #------------------------------------------------------------------------------
    # SOM->E; apical dendrites (no sCRACM)
    netParams.subConnParams['SOM->E'] = {
        'preConds': {'cellType': 'SOM'}, 
        'postConds': {'cellType': ['IT', 'CT', 'PT']},  
        'sec': 'apicdend',
        'groupSynMechs': SOMESynMech,
        'density': 'uniform'} 


    #------------------------------------------------------------------------------
    # All->I; apical dendrites (no sCRACM)
    netParams.subConnParams['All->I'] = {
        'preConds': {'cellType': ['IT', 'CT', 'PT', 'SOM', 'PV']+longPops}, 
        'postConds': {'cellType': ['SOM', 'PV']},  
        'sec': 'spiny',
        'groupSynMechs': ESynMech,
        'density': 'uniform'} 


#------------------------------------------------------------------------------
# Description
#------------------------------------------------------------------------------
netParams.description = """ 
- M1 net, 6 layers, 7 cell types 
- NCD-based connectivity from  Weiler et al. 2008; Anderson et al. 2010; Kiritani et al. 2012; 
  Yamawaki & Shepherd 2015; Apicella et al. 2012
- Parametrized version based on Sam's code
- Updated cell models and mod files
- Added parametrized current inputs
- Fixed bug: prev was using cell models in /usr/site/nrniv/local/python/ instead of cells 
- Use 5 synsperconn for 5-comp cells (HH_reduced); and 1 for 1-comp cells (HH_simple)
- Fixed bug: made global h params separate for each cell model
- Fixed v_init for different cell models
- New IT cell with same geom as PT
- Cleaned cfg and moved background inputs here
- Set EIGain and IEGain for each inh cell type
- Added secLists for PT full
- Fixed reduced CT (wrong vinit and file)
- Added subcellular conn rules to distribute synapses
- PT full model soma centered at 0,0,0 
- Set cfg seeds here to ensure they get updated
- Added PVSOMGain and SOMPVGain
- PT subcellular distribution as a cfg param
- Cylindrical volume
- DefaultDelay (for local conns) = 2ms
- Added long range connections based on Yamawaki 2015a,b; Suter 2015; Hooks 2013; Meyer 2011
- Updated cell densities based on Tsai 2009; Lefort 2009; Katz 2011; Wall 2016; 
- Separated PV and SOM of L5A vs L5B
- Fixed bugs in local conn (PT, PV5, SOM5, L6)
- Added perisom secList including all sections 50um from soma
- Added subcellular conn rules (for both full and reduced models)
- Improved cell models, including PV and SOM fI curves
- Improved subcell conn rules based on data from Suter15, Hooks13 and others
- Adapted Bdend L of reduced cell models
- Made long pop rates a cfg param
- Set threshold to 0.0 mV
- Parametrized I->E/I layer weights
- Added missing subconn rules (IT6->PT; S1,S2,cM1->IT/CT; long->SOM/PV)
- Added threshold to weightNorm (PT threshold=10x)
- weightNorm threshold as a cfg parameter
- Separate PV->SOM, SOM->PV, SOM->SOM, PV->PV gains 
- Conn changes: reduced IT2->IT4, IT5B->CT6, IT5B,6->IT2,4,5A, IT2,4,5A,6->IT5B; increased CT->PV6+SOM6
- Parametrized PT ih gbar
- Added IFullGain parameter: I->E gain for full detailed cell models
- Replace PT ih with Migliore 2012
- Parametrized ihGbar, ihGbarBasal, dendNa, axonNa, axonRa, removeNa
- Replaced cfg list params with dicts
- Parametrized ihLkcBasal and AMPATau2Factor
- Fixed synMechWeightFactor
- Parametrized PT ih slope
- Added disynapticBias to I->E (Yamawaki&Shepherd,2015)
- Fixed E->CT bin 0.9-1.0
- Replaced GABAB with exp2syn and adapted synMech ratios
- Parametrized somaNa
- Added ynorm condition to NetStims
- Added option to play back recorded spikes into long-range inputs
- Fixed Bdend pt3d y location
- Added netParams.convertCellShapes = True to convert stylized geoms to 3d points
- New layer boundaries, cell densities, conn, FS+SOM L4 grouped with L2/3, low cortical input to L4
- Increased exc->L4 based on Yamawaki 2015 fig 5
- v54: Moved from NetPyNE v0.7.9 to v0.9.1 (v54_batch1-6)
- v54: Moved to NetPyNE v0.9.1 and py3 (v54_batch7 onwards)
- v56: Reduced dt from 0.05 to 0.025 (note this version follows from v54, i.e. without new cell types; branch 'paper2019_py3')
- v56: (included in prev version): Added cfg.KgbarFactor
"""
