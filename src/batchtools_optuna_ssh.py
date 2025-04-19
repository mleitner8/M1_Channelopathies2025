from netpyne.batchtools.search import search

params = {'weightLong.TPO': [0.25, 0.75],
          'weightLong.S1': [0.25, 0.75],
          'weightLong.S2': [0.25, 0.75],
          'weightLong.cM1': [0.25, 0.75],
          'weightLong.M2': [0.25, 0.75],
          'weightLong.OC': [0.25, 0.75],
          'EEGain': [0.5, 1.5],
          'IEweights.0': [0.5, 1.5],
          'IEweights.1': [0.5, 1.5],
          'IEweights.2': [0.5, 1.5],
          'IIweights.0': [0.5, 1.5],
          'IIweights.1': [0.5, 1.5],
          'IIweights.2': [0.5, 1.5],
          }
"""
# SGE GPU CONFIG
sge_config = {
    'queue': 'gpu.q',
    'cores': 19,
    'vmem': '90G', #90G
    'realtime': '15:00:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) ./x86_64/special -python -mpi init.py'}

run_config = sge_config

search(job_type = 'sge', # or sh
       comm_type = 'socket',
       label = 'optuna',
       params = params,
       output_path = '../batchData/optuna_batch',
       checkpoint_path = '../batchData/ray',
       run_config = run_config,
       num_samples = 1,
       metric = 'loss',
       mode = 'min',
       algorithm = 'optuna',
       max_concurrent = 1)
"""

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
    'coresPerNode': 128,
    'mem': '128G',
    'partition': 'compute',
    'email': 'romanbaravalle@gmail.com',
    'custom': setup,
    'command':'time mpirun -n 128 nrniv -python -mpi init.py'
}

# use batch_shell_config if running directly on the machine
shell_config = {'command': 'nrniv -python init.py'}

results = search(job_type = 'sh', # slurm or 'sh'
       comm_type = 'ssh', # ssh, socket if a metric and mode is specified, some method of communicating with the host needs to be defined
       label = 'optuna',
       params = params,
       output_path = '../batchData/optuna_batch',
       checkpoint_path = '../batchData/ray',
       run_config = slurm_config, # or slurm_config
       metric = 'loss', # if a metric and mode is specified, the search will collect metric data and report on the optimal configuration
       mode = 'min',
       algorithm = "optuna",
       max_concurrent = 1,
       remote_dir='/home/rbaravalle/M1_Channelopathies2025/src',
       host='expanse0',
       key='',
       num_samples=100,
       )