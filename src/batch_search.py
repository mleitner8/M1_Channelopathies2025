from batchtk.algos import optuna_search
from batchtk.utils import expand_path

from netpyne.batchtools.search import generate_constructors

#option for local run
dispatcher, submit = generate_constructors('sge', 'sfs')

#option for slurm run
#dispatcher, submit = generate_constructors('slurm', 'sfs')

params = {'weightLong.TPO': [0.2, 0.3],
          'weightLong.TVL': [0.2, 0.3],
          'weightLong.S1': [0.2, 0.3],
          'weightLong.S2': [0.2, 0.3],
          'weightLong.cM1': [0.2, 0.3],
          'weightLong.M2': [0.2, 0.3],
          'weightLong.OC': [0.2, 0.3],
          'EEGain': [0.2, 0.5],
          'IEweights.0': [0.4, 0.6],  ## L2/3+4
          'IEweights.1': [0.4, 0.6],  ## L5
          'IEweights.2': [0.4, 0.6],  ## L6
          'IIweights.0': [1.5, 2.0],  ## L2/3+4
          'IIweights.1': [1.5, 2.0],  ## L5
          'IIweights.2': [1.5, 2.0],  ## L6
          }


sge_config = {
    'queue': 'cpu.q',
    'cores': 64,
    'vmem': '120G',
    'realtime': '15:00:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init_batch.py'}


results = optuna_search(
    study_label='optuna',
    param_space=params,
    metrics={'loss': 'minimize'}, # metric is loss, direction is to minimize
    num_trials=1, num_workers=1, # change the number of trials and concurrency here
    dispatcher_constructor=dispatcher,
    submit_constructor=submit,
    submit_kwargs=sge_config, # sge run
    interval=30, # can increase the polling time since simulations run long.
    project_path='.',
    output_path=expand_path('../optuna_search', create_dirs=True),
)
