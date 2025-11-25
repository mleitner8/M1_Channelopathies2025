from batchtk.algos import optuna_search
from batchtk.utils import expand_path
from netpyne.batchtools.search import generate_constructors



search_space = {
          'EEGain': [0.5, 1.5],
          'IEweights.0': [0.5, 1.5],
          'IEweights.1': [0.5, 1.5],
          'IEweights.2': [0.5, 1.5],
          'IIweights.0': [0.5, 1.5],
          'IIweights.1': [0.5, 1.5],
          'IIweights.2': [0.5, 1.5],
          }

param_space_samplers = [ 'float' for _ in search_space]

param_bounds = {
    key: [min(values)-1, max(values)+1] for key, values in search_space.items()
}


dispatcher, submit = generate_constructors('slurm', 'sfs')

# EXPANSE CONFIG   -- need to change conda environment and add source
CONFIG_EXPANSE_CPU = """
source ~/.bashrc
module purge
module load shared
module load cpu/0.17.3b
module load slurm
module load sdsc
module load DefaultModules
module load openmpi/mlnx/gcc/64/4.1.5a1
conda activate M1c
"""

run_config = {
        'allocation': 'TG-MED240058',
        'realtime': '10:30:00',
        'nodes': 1,
        'coresPerNode': 96,
        'mem': '128G',
        'email': 'molly.leitner@downstate.edu',
        'command': f"""
        {CONFIG_EXPANSE_CPU}
        mpirun -n $SLURM_NTASKS nrniv -python -mpi init_batch.py
        """
    }



results = optuna_search(
    study_label='optuna',
    param_space=param_bounds,
    metrics={'loss': 'minimize'},
    num_trials=10, num_workers = 4,
    algo='optuna',
    dispatcher_constructor=dispatcher,
    submit_constructor=submit,
    submit_kwargs=run_config,
    interval=10,
    project_path='/home/mleitner/M1_Channelopathies2025',
    output_path=expand_path('../batchData/grid_batch/optuna', create_dirs=True)
)

