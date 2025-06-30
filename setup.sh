unset DISPLAY
conda activate M1_VIPNGF
export PYTHONPATH=$PYTHONPATH:$PWD # do it in \src and in parent folder
cd src
export PYTHONPATH=$PYTHONPATH:$PWD # do it in \src and in parent folder
nrnivmodl ../mod/