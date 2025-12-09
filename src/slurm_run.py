# EXPANSE CONFIG
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
        'coresPerNode': 1,
        'mem': '4G',
        'email': 'molly.leitner@downstate.edu',
    'partition': 'shared',
    'custom': '',
        'command': f"""
        {CONFIG_EXPANSE_CPU}
        mpirun -n $SLURM_NTASKS nrniv -python -mpi init_batch.py
        """
    }


setup = """
source ~/.bashrc
source ~/default.sh
source ~/conda.sh
conda activate netpyne
"""
slurm_config = { # many of this config will be relevant to the user, resource allocation and script
    'allocation': 'csd403',
    'realtime': '00:30:00',
    'nodes': 1,
    'coresPerNode': 4,
    'mem': '32G',
    'partition': 'shared',
    'email': 'jchen.6727@gmail.com',
    'custom': setup,
    'command':'time mpirun -n 4 nrniv -python -mpi init.py'
}