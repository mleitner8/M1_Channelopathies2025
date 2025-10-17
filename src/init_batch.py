"""
init.py

Starting script to run NetPyNE-based M1 model.

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py

Contributors: salvadordura@gmail.com
"""

import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers
from netpyne import sim, specs
import json
# FOR OLD BATCH UNCOMMENT THIS NEXT LINE
from netParams import netParams, cfg
import numpy as np


def rateFitnessFunc(simData, extraConds=False, **kwargs):

    pops = kwargs['pops']
    maxFitness = kwargs['maxFitness']

    factor = 1
    # Add extra conditions to the fitness. It 'breaks' the fitness function
    if extraConds:
        # check I > E in each layer
        condsIE_L23 = (simData['popRates']['PV2'] > simData['popRates']['IT2']) and (
                    simData['popRates']['SOM2'] > simData['popRates']['IT2'])
        condsIE_L5A = (simData['popRates']['PV5A'] > simData['popRates']['IT5A']) and (
                    simData['popRates']['SOM5A'] > simData['popRates']['IT5A'])
        condsIE_L5B = (simData['popRates']['PV5B'] > simData['popRates']['IT5B']) and (
                    simData['popRates']['SOM5B'] > simData['popRates']['IT5B'])
        condsIE_L6 = (simData['popRates']['PV6'] > simData['popRates']['IT6']) and (
                    simData['popRates']['SOM6'] > simData['popRates']['IT6'])
        # check E L5 > L6 > L2
        condEE562_0 = (simData['popRates']['IT5A'] + simData['popRates']['IT5B'] + simData['popRates']['PT5B']) / 3 > (
                    simData['popRates']['IT6'] + simData['popRates']['CT6']) / 2
        condEE562_1 = (simData['popRates']['IT6'] + simData['popRates']['CT6']) / 2 > simData['popRates']['IT2']
        # check PV > SOM in each layer
        condsPVSOM_L23 = (simData['popRates']['PV2'] > simData['popRates']['SOM2'])
        condsPVSOM_L5A = (simData['popRates']['PV5A'] > simData['popRates']['SOM5A'])
        condsPVSOM_L5B = (simData['popRates']['PV5B'] > simData['popRates']['SOM5B'])
        condsPVSOM_L6 = (simData['popRates']['PV6'] > simData['popRates']['SOM6'])

        conds = [condsIE_L23, condsIE_L5A, condsIE_L5B, condsIE_L6, condEE562_0, condEE562_1, condsPVSOM_L23,
                 condsPVSOM_L5A, condsPVSOM_L5B, condsPVSOM_L6]

        if not all(conds): factor = 1.5

    popFitness = [min(np.exp(factor * abs(v['target'] - simData['popRates'][k]) / v['width']), maxFitness)
                  if simData['popRates'][k] > v['min'] else maxFitness for k, v in pops.items()]
    fitness = np.mean(popFitness)

    popInfo = '; '.join(
        ['%s rate=%.1f fit=%1.f' % (p, simData['popRates'][p], popFitness[i]) for i, p in enumerate(pops)])
    print('  ' + popInfo)
    return fitness
# -----------------------------------------------------------
# Main code
# FOR OLD BATCH UNCOMMENT THIS NEXT LINE
# cfg, netParams = sim.readCmdLineArgs()
sim.initialize(
    simConfig = cfg,
    netParams = netParams)  				# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations
sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                      			# run parallel Neuron simulation
sim.gatherData()                  			# gather spiking data and cell info from each node
sim.saveData()                    			# save params, cell info and sim output to file (pickle,mat,txt,etc)#
sim.analysis.plotData()         			# plot spike raster etc

# -----------------------------------------------------------
# Algorithm Specs
# -----------------------------------------------------------
if sim.rank == 0:
    # netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
    print('transmitting data...')
    inputs = cfg.get_mappings()
    # print(json.dumps({**inputs}))
    results = sim.analysis.popAvgRates(tranges=cfg.timeRanges, show=False)

    sim.simData['popRates'] = results

    fitnessFuncArgs = {}
    pops = {}
    ## Exc pops
    Epops = ['IT2', 'IT4', 'IT5A', 'IT5B', 'PT5B', 'IT6', 'CT6']
    Etune = {'target': 5, 'width': 5, 'min': 0.5}
    for pop in Epops:
        pops[pop] = Etune
    ## Inh pops
    Ipops = ['PV2', 'SOM2',
             'PV4', 'SOM4',
             'PV5A', 'SOM5A',
             'PV5B', 'SOM5B',
             'PV6', 'SOM6']
    Itune = {'target': 10, 'width': 15, 'min': 0.25}
    for pop in Ipops:
        pops[pop] = Itune
    fitnessFuncArgs['pops'] = pops
    fitnessFuncArgs['maxFitness'] = 1000

    rateLoss = rateFitnessFunc(sim.simData, **fitnessFuncArgs)
    results['loss'] = rateLoss
    out_json = json.dumps({**inputs, **results})

    print(out_json)
    sim.send(out_json)


