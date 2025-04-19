from netpyne import specs 
import json 

netParams = specs.NetParams() 
cellRule = netParams.importCellParams('PT5B_full', 'Na12HH16HHModel_TF.py', 'Na12Model_TF') 

netParams.renameCellParamsSec(label='PT5B_full', oldSec='soma_0', newSec='soma')
cellRule = netParams.cellParams['PT5B_full']

cellRule['secs']['axon_0']['geom']['pt3d'] = [[0,0,0,0]] #[[1e30, 1e30, 1e30, 1e30]] #stupid workaround that should$
cellRule['secs']['axon_1']['geom']['pt3d'] = [[1e30, 1e30, 1e30, 1e30]] #breaks in simulations btw. Just used for t$

nonSpiny = ['apic_0' ,'apic_1']

netParams.addCellParamsSecList(label='PT5B_full', secListName='perisom', somaDist=[0, 50])  # sections within 50 um$
netParams.addCellParamsSecList(label='PT5B_full', secListName='below_soma', somaDistY=[-600, 0])  # sections within$

for sec in nonSpiny: # N.B. apic_1 not in `perisom` . `apic_0` and `apic_114` are
    if sec in cellRule['secLists']['perisom']: # fixed logic
        cellRule['secLists']['perisom'].remove(sec)
cellRule['secLists']['alldend'] = [sec for sec in cellRule['secs'] if ('dend' in sec or 'apic' in sec)] # basal+api$
cellRule['secLists']['apicdend'] = [sec for sec in cellRule['secs'] if ('apic' in sec)] # apical
cellRule['secLists']['spiny'] = [sec for sec in cellRule['secLists']['alldend'] if sec not in nonSpiny]
cellRule['secs']['axon_0']['spikeGenLoc'] = 0.5

cellRule['secs']['soma']['threshold'] = 0. # Lowering since it looks like v in soma is not reaching high voltages w$

del netParams.cellParams['PT5B_full']['secs']['axon_0']['geom']['pt3d']
del netParams.cellParams['PT5B_full']['secs']['axon_1']['geom']['pt3d']

netParams.cellParams['PT5B_full']['conds'] = {'cellModel': 'HH_full', 'cellType': 'PT'}
#netParams.addCellParamsWeightNorm('PT5B_full', '../conn/PT5B_full_weightNorm.pkl', threshold=cfg.weightNormThreshol$
#if saveCellParams: netParams.saveCellParamsRule(label='PT5B_full', fileName='../cells/PT5B_full_cellParams.pkl')

out_file = open("../Na12HH16HH_TF.json", "w")
json.dump(cellRule, out_file)