from netpyne.batchtools.search import search

params = {'weightLong.TPO': [0.4, 0.8],
          'weightLong.S1': [0.4, 0.8],
          'weightLong.S2': [0.4, 0.8],
          'weightLong.cM1': [0.4, 0.8],
          'weightLong.M2': [0.4, 0.8],
          'weightLong.OC': [0.4, 0.8],
          'EEGain': [0.5, 0.7],
          'IEweights.0': [0.5, 0.6],
          'IEweights.1': [0.7, 0.8],
          'IEweights.2': [1.0, 1.1],
          'IIweights.0': [1.4, 1.5],
          'IIweights.1': [0.7, 0.8],
          'IIweights.2': [1.1, 1.2]
          }

# EXPANSE CONFIG   -- need to change conda environment and add source
setup = """
source ~/.bashrc
source ~/default.sh
conda activate M1_batchTools 
export LD_LIBRARY_PATH="/home/mollyleitner/miniconda3/envs/py312/lib/python3.12/site-packages/mpi4py_mpich.libs/"
"""
slurm_config = {
    'allocation': 'TG-MED240058', #change with project information
    'realtime': '10:30:00',
    'nodes': 1,
    'coresPerNode': 96,
    'mem': '128G',
    'partition': 'compute',
    'email': 'molly.leitner@downstate.edu',
    'custom': setup,
    'command':'time mpirun -n 96 nrniv -python -mpi init_batch.py'
}

# use batch_shell_config if running directly on the machine
shell_config = {'command': 'nrniv -python init.py'}

results = search(job_type = 'slurm', # slurm or 'sh'
       comm_type = 'ssh', # ssh or socket if a metric and mode is specified, some method of communicating with the host needs to be defined
       label = 'optuna',
       params = params,
       output_path = '../batchData/optuna',
       checkpoint_path = '../batchData/ray',
       run_config = shell_config, # or slurm_config
       metric = 'loss', # if a metric and mode is specified, the search will collect metric data and report on the optimal configuration
       mode = 'min',
       algorithm = "optuna",
       max_concurrent = 1,
       remote_dir='/home/mollyleitner/M1_Channelopathies2025/src',
       host='expanse0',
       key='',
       num_samples=2,
       )