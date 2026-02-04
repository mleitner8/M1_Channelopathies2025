from netpyne.batchtools.search import search
#from batchtk.utils import expand_path
#from netpyne.batchtools.search import generate_constructors

#dispatcher, submit = generate_constructors('sge', 'sfs')

params = {'variant': ['G211D', 'G822S', 'G879R']}

# use batch_sge_config if running on a
sge_config = {
    'queue': 'cpu.q',
    'cores': 64,
    'vmem': '120G',
    'realtime': '15:00:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init_batch.py'}

run_config = sge_config

search(#dispatcher_constructor=dispatcher,
    #submit_constructor=submit,
    job_type = 'sge', comm_type = 'sfs',
    run_config = run_config,
    label='grid_74aee313_variants',
    params=params,
    algorithm = 'variant_generator',
    output_path = '../grid_batch',
    checkpoint_path = '../ray',
    max_concurrent = 9,
    metric = 'loss',
    mode = 'min',
    num_samples = 1)
