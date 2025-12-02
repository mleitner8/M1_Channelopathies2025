"""
init.py

Starting script to run NetPyNE-based M1 model.

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py

Contributors: salvadordura@gmail.com
"""

from netpyne import sim, specs
import json
# FOR OLD BATCH UNCOMMENT THIS NEXT LINE
from netParams import netParams, cfg

sim.initialize(
    simConfig = cfg,
    netParams = netParams)  				# create network object and set cfg and net params

sim.saveData()                    			# save params, cell info and sim output to file (pickle,mat,txt,etc)#


mappings = cfg.get_mappings()
results = {'loss': 0, **mappings}

sim.send(results)


