from netpyne.batchtools.search import search
import numpy as np
import json

sections = list(json.load(open('../cells/Na12HH16HH_TF.json', 'r'))['secs'].keys())
sections.remove('axon_0')
sections.remove('axon_1')

weights = list(np.arange(0.01, 0.22, 0.05)/100.0) 
# weights = list(np.arange(0.01, 0.22, 0.05)) 
# Create parameter grid for search
params = {
    'sec'   : sections,
    'weight': weights,
}

# use batch_sge_config if running on a
sge_config = {
    'command': 'python test.py'}

result_grid = search(job_type = 'sh',
       comm_type       = "socket",
       params          = params,
       run_config      = sge_config,
       label           = "grid_search",
       output_path     = "./grid_batch",
       checkpoint_path = "./ray",
       num_samples     = 1,
       metric          = 'epsp',
       mode            = 'min',
       algorithm       = "variant_generator",
       max_concurrent  = 9)
