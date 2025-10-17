from netpyne.batchtools.search import search
import os

params = {'weightLong.TPO': [0.2, 0.3],
          'weightLong.TVL': [0.2, 0.3],
          'weightLong.S1': [0.2, 0.3],
          'weightLong.S2': [0.2, 0.3],
          'weightLong.cM1': [0.2, 0.3],
          'weightLong.M2': [0.2, 0.3],
          'weightLong.OC': [0.2, 0.3],
          'EEGain': [0.2, 0.5],
          'IEweights.0': [],    ## L2/3+4
          'IEweights.1': [],    ## L5
          'IEweights.2': [],    ## L6
          'IIweights.0': [],    ## L2/3+4
          'IIweights.1': [],    ## L5
          'IIweights.2': [],    ## L6
          }

sge_config = {
    'queue': 'cpu.q',
    'cores': 64,
    'vmem': '120G',
    'realtime': '15:00:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init_batch.py'}


run_config = sge_config

results = search(job_type = 'sge', # or 'sh'
       comm_type = 'socket',
       label = 'optuna_1',
       params = params,
       output_path = '../grid_batch',
       checkpoint_path = '../ray',
       run_config = run_config,
       num_samples = 1,
       metric = 'loss',
       mode = 'min',
       algorithm = 'optuna',
       max_concurrent = 1
                 )