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
from netpyne import sim
from netParams import netParams, cfg
import json

#------------------------------------------------------------------------------
## Function to calculate the fitness according to required rate
def rateFitnessFunc(simData, **kwargs):
    import numpy as np
    pops = kwargs['pops']
    maxFitness = kwargs['maxFitness']

    popFitness = [min(np.exp(abs(v['target'] - simData['popRates'][k]) / v['width']), maxFitness)
                  if simData['popRates'][k] > v['min'] else maxFitness for k, v in pops.items()]
    fitness = np.mean(popFitness)

    popInfo = '; '.join(
        ['%s rate=%.1f fit=%1.f' % (p, simData['popRates'][p], popFitness[i]) for i, p in enumerate(pops)])
    print('  ' + popInfo)
    return fitness


#------------------------------------------------------------------------------
## Function to modify cell params during sim (e.g. modify PT ih)
def modifyMechsFunc(simTime):
    from netpyne import sim

    t = simTime

    cellType = cfg.modifyMechs['cellType']
    mech = cfg.modifyMechs['mech']
    prop = cfg.modifyMechs['property']
    newFactor = cfg.modifyMechs['newFactor']
    origFactor = cfg.modifyMechs['origFactor']
    factor = newFactor / origFactor
    change = False

    if cfg.modifyMechs['endTime']-1.0 <= t <= cfg.modifyMechs['endTime']+1.0:
        factor = origFactor / newFactor if abs(newFactor) > 0.0 else origFactor
        change = True

    elif t >= cfg.modifyMechs['startTime']-1.0 <= t <= cfg.modifyMechs['startTime']+1.0:
        factor = newFactor / origFactor if abs(origFactor) > 0.0 else newFactor
        change = True

    if change:
        print('   Modifying %s %s %s by a factor of %f' % (cellType, mech, prop, factor))
        for cell in sim.net.cells:
            if 'cellType' in cell.tags and cell.tags['cellType'] == cellType:
                for secName, sec in cell.secs.items():
                    if mech in sec['mechs'] and prop in sec['mechs'][mech]:
                        # modify python
                        sec['mechs'][mech][prop] = [g * factor for g in sec['mechs'][mech][prop]] if isinstance(sec['mechs'][mech][prop], list) else sec['mechs'][mech][prop] * factor

                        # modify neuron
                        for iseg, seg in enumerate(sec['hObj']):  # set mech params for each segment
                            if sim.cfg.verbose: print('   Modifying %s %s %s by a factor of %f' % (secName, mech, prop, factor))
                            setattr(getattr(seg, mech), prop, getattr(getattr(seg, mech), prop) * factor)



# -----------------------------------------------------------
# Main code
#cfg, netParams = sim.readCmdLineArgs(simConfigDefault='cfg.py', netParamsDefault='netParams.py')
sim.initialize(
    simConfig = cfg, 	
    netParams = netParams)  # create network object and set cfg and net params

sim.pc.timeout(300)                          # set nrn_timeout threshold to X sec (max time allowed without increasing simulation time, t; 0 = turn off)
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations
sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)

# Simulation option 1: standard
sim.runSim()                              # run parallel Neuron simulation (calling func to modify mechs)

#print(cfg.modifyMechs)
# Simulation option 2: interval function to modify mechanism params
#sim.runSimWithIntervalFunc(1000.0, modifyMechsFunc)       # run parallel Neuron simulation (calling func to modify mechs)

# Gather/save data option 1: standard
sim.gatherData()

# Gather/save data option 2: distributed saving across nodes 
#sim.saveDataInNodes()
#sim.gatherDataFromFiles()

sim.saveData()                    			# save params, cell info and sim output to file (pickle,mat,txt,etc)#
sim.analysis.plotData()         			# plot spike raster etc
print('completed simulation...')

if sim.rank == 0:
    netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
    print('transmitting data...')
    inputs = cfg.get_mappings()
    print(json.dumps({**inputs}))
    results = sim.analysis.popAvgRates(show=False)

    print(results)

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
             'PV5A', 'SOM5A',
             'PV5B', 'SOM5B',
             'PV6', 'SOM6']
    Itune = {'target': 10, 'width': 15, 'min': 0.25}
    for pop in Ipops:
        pops[pop] = Itune
    fitnessFuncArgs['pops'] = pops
    fitnessFuncArgs['maxFitness'] = 1000

    rateLoss = rateFitnessFunc(sim.simData, **fitnessFuncArgs)

    # results['PYR_loss'] = (results['PYR'] - 3.33875)**2
    # results['BC_loss']  = (results['BC']  - 19.725 )**2
    # results['OLM_loss'] = (results['OLM'] - 3.470  )**2
    results['loss'] = rateLoss
    out_json = json.dumps({**inputs, **results})

    print(out_json)
    sim.send(out_json)