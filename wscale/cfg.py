from netpyne import specs

cfg = specs.SimConfig()

    # General simulation paramaters
cfg.duration = 3500           # Simulation duration in ms
cfg.dt       = 0.025          # Simulation time step in ms
cfg.verbose  = True           # Verbose output

    # config sec/weight
cfg.sec    = 'soma'
cfg.weight = 0.001

    # Hyperparameters
cfg.hParams = {
        'celsius' : 34.0,
        'v_init'  : -65         # Initial membrane potential
}

cfg.recordStep   = 0.1       # Step size in ms to save data (e.g., V traces, LFP, etc)

    # Saving options
cfg.filename     = 'wscale'       # Output file name prefix
cfg.savePickle   = False       # Save simulation data to a pickle file
cfg.saveJson     = False       # Save simulation data to a .json file
cfg.saveFolder   = '.'
cfg.simLabel     = 'wscale'

    # Analysis options
    # Other options
cfg.cache_efficient = True




# Initialize configuration

