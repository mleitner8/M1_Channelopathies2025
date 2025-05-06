import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers
from netpyne import sim
import json
# FOR OLD BATCH UNCOMMENT THIS NEXT LINE
from netParams import netParams, cfg


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

if sim.rank == 0:
    netParams.save("{}/{}_params.json".format(cfg.saveFolder, cfg.simLabel))
    print('transmitting data...')
    inputs = cfg.get_mappings()
    print(json.dumps({**inputs}))
    results = sim.analysis.popAvgRates(show=False)

    sim.simData['popRates'] = results

    fitnessFuncArgs = {}
    pops = {}
    ## Exc pops
    Epops = ['IT2', 'IT4', 'IT5A', 'IT5B', 'PT5B', 'IT6', 'CT6']
    Etune = {'target': 5, 'width': 5, 'min': 0.5}
    for pop in Epops:
        pops[pop] = Etune
    ## Inh pops
    Ipops = ['NGF1', 'PV2', 'SOM2', 'VIP2', 'NGF2',
             'PV4', 'SOM4', 'VIP4', 'NGF4',
             'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',
             'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',
             'PV6', 'SOM6', 'VIP6', 'NGF6']
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