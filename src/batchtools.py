from netpyne.batchtools.search import search

params = {
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
CONFIG_EXPANSE_CPU = """
source ~/.bashrc
module purge
module load shared
module load cpu/0.17.3b
module load slurm
module load sdsc
module load DefaultModules
module load openmpi/mlnx/gcc/64/4.1.5a1
conda activate py312
"""

ssh_expanse_cpu = {
    'job_type': 'ssh_slurm', # or 'sh'
    'comm_type': 'sftp',
    'host': 'expanse0',
    'key':'Z45LIALPT7ZGC4YG7LPJHH7NXQFD4TYF',
    'remotedir': 'home/mleitner/M1_Channelopathies2025',
    'output_path': '../batchData/grid_batch',
    'checkpoint_path': '../batchData/ray',
    'run_config': {
        'allocation': 'TG-MED240058',
        'realtime': '10:30:00',
        'nodes': 1,
        'coresPerNode': 96,
        'mem': '128G',
        'email': 'molly.leitner@downstate.edu',
        'command': f"""
        {CONFIG_EXPANSE_CPU}
        mpirun -n $SLURM_NTASKS nrniv -python -mpi init.py
        """
    }
    }


run_config = ssh_expanse_cpu

search(
    label='grid_1',
    params=params,
    metric = 'loss',
    mode = 'min',
    algorithm='grid',
    max_concurrent = 9,
    num_samples= 1,
    **run_config
)
