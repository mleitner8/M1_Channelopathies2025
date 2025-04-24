from netpyne.batchtools.search import search

params = {'weightLong.TPO': [0.25, 0.8],
          'weightLong.S1': [0.25, 0.8],
          'weightLong.S2': [0.25, 0.8],
          'weightLong.cM1': [0.25, 0.8],
          'weightLong.M2': [0.25, 0.8],
          'weightLong.OC': [0.25, 0.8],
          'EEGain': [0.5, 1.5],
          'IEweights.0': [0.5, 1.5],
          'IEweights.1': [0.5, 1.5],
          'IEweights.2': [0.5, 1.5],
          'IIweights.0': [0.5, 1.5],
          'IIweights.1': [0.5, 1.5],
          'IIweights.2': [0.5, 1.5]
          }

# EXPANSE CONFIG
setup = """
source ~/.bashrc
source ~/default.sh
conda activate M1_batchTools
export LD_LIBRARY_PATH="/home/rbaravalle/.conda/envs/NetPyNE/lib/python3.10/site-packages/mpi4py_mpich.libs/"
"""
slurm_config = {
    'allocation': 'TG-MED240058',
    'realtime': '10:30:00',
    'nodes': 1,
    'coresPerNode': 96,
    'mem': '128G',
    'partition': 'compute',
    'email': 'romanbaravalle@gmail.com',
    'custom': setup,
    'command':'time mpirun -n 96 nrniv -python -mpi init.py'
}

results = search(job_type = 'slurm', # or 'sh'
       comm_type = 'ssh', # if a metric and mode is specified, some method of communicating with the host needs to be defined
       label = 'optuna',
       params = params,
       output_path = '../batchDataMolly/optuna',
       checkpoint_path = '../batchDataMolly/ray',
       run_config = slurm_config,
       metric = 'loss', # if a metric and mode is specified, the search will collect metric data and report on the optimal configuration
       mode = 'min',
       algorithm = "optuna",
       max_concurrent = 1,
       remote_dir='/home/rbaravalle/M1_Channelopathies2025/src',
       host='expanse0',
       key='J4PXKKROVTM3R4ELLVAQ3CJCL6OUP2WN',
       num_samples=500,
       )