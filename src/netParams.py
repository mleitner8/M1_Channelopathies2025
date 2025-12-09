"""
netParams.py

High-level specifications for M1 network model using NetPyNE

Contributors: salvadordura@gmail.com
"""

from netpyne import specs
import pickle, json

# Import cfg for new batchtools:
from cfg import cfg

cfg.update()
netParams = specs.NetParams()  # object of class NetParams to store the network parameters
netParams.mappings = cfg.get_mappings()
