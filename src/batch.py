from batchtk.algos import optuna_search
from batchtk.utils import expand_path
from netpyne.batchtools.search import generate_constructors

from local_run import run_config as local_run_config
from sge_run import run_config as sge_run_config
from slurm_run import run_config as slurm_run_config

SLURM = ('slurm', 'sfs')
LOCAL = ('sh', 'sfs')
SGE   = ('sge', 'sfs')
RUN_CONFIG = local_run_config # or sge_run_config or slurm_run_config

# keep params ... change according to model.
search_space = {
          'EEGain': [0.5, 1.5],
          'IEweights.0': [0.5, 1.5],
          'IEweights.1': [0.5, 1.5],
          'IEweights.2': [0.5, 1.5],
          'IIweights.0': [0.5, 1.5],
          'IIweights.1': [0.5, 1.5],
          'IIweights.2': [0.5, 1.5]
          }

param_space_samplers = [ 'float' for _ in search_space]

param_bounds = {
    key: [min(values)-1, max(values)+1] for key, values in search_space.items()
}


dispatcher, submit = generate_constructors(*LOCAL)

results = optuna_search(
    study_label='optuna',
    param_space=param_bounds,
    metrics={'loss': 'minimize'},
    num_trials=5, num_workers = 5, # test concurrency, can change this to 1, 1
    algo='tspe',
    dispatcher_constructor=dispatcher,
    submit_constructor=submit,
    submit_kwargs=RUN_CONFIG,
    interval=10,
    project_path=expand_path('.'),
    output_path=expand_path('../mre_test', create_dirs=True)
)

