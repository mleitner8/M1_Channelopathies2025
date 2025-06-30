ssh node01
conda activate GPU
export PATH=$HOME/neuronGPU/bin:$PATH
export PYTHONPATH=$HOME/neuronGPU/lib/python:$PYTHONPATH
export LD_LIBRARY_PATH="/usr/lib64/openmpi/lib/":"/opt/nvidia/hpc_sdk/Linux_x86_64/23.9/compilers/lib"
nrnivmodl -coreneuron ../mod