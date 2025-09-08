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
# use batch_sge_config if running on a
sge_config = {
    'queue': 'cpu.q',
    'cores': 64,
    'vmem': '120G',
    'realtime': '15:00:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init_batch.py'}


run_config = sge_config

search(job_type = 'sge', # or 'sh'
       comm_type = 'socket',
       label = 'ihGbar',
       params = params,
       output_path = '../grid_batch',
       checkpoint_path = '../ray',
       run_config = run_config,
       num_samples = 1,
       metric = 'loss',
       mode = 'min',
       algorithm = "variant_generator",
       max_concurrent = 9)
"""

# EXPANSE CONFIG   -- need to change conda environment and add source
setup = """
source ~/.bashrc
conda activate py312
export LD_LIBRARY_PATH="/ddn/mollyleitner/miniconda3/envs/py312/lib/python3.12/site-packages/mpi4py_mpich.libs/"
"""

slurm_config = {
    'allocation': 'TG-MED240058',
    'realtime': '10:30:00',
    'nodes': 1,
    'coresPerNode': 96,
    'mem': '128G',
    'partition': 'compute',
    'email': 'molly.leitner@downstate.edu',
    'custom': setup,
    'command': 'time mpirun -n 96 nrniv -python -mpi init_batch.py'
}

results = search(job_type = 'ssh_slurm', # or 'sh'
       comm_type = 'sftp', # if a metric and mode is specified, some method of communicating with the host needs to be defined
       label = 'grid',
       params = params,
       output_path = '../batchData/grid_batch',
       checkpoint_path = '../batchData/ray',
       run_config = slurm_config,
       metric = 'loss', # if a metric and mode is specified, the search will collect metric data and report on the optimal configuration
       mode = 'min',
       algorithm = "grid",
       max_concurrent = 1,
       remote_dir='/home/mleitner/expanse/M1_Channelopathies2025/src',
       host= 'login.expanse.sdsc.edu',
       key='',
       num_samples=2,
       )