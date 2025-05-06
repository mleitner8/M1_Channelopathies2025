#!/bin/bash
#SBATCH --job-name=optuna_f299ccf3
#SBATCH -A TG-MED240058
#SBATCH -t 10:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=96
#SBATCH --cpus-per-task=1
#SBATCH --mem=128G
#SBATCH --partition=compute
#SBATCH -o /home/rbaravalle/M1_Channelopathies2025/batchDataMolly/optuna4/optuna_f299ccf3.run
#SBATCH -e /home/rbaravalle/M1_Channelopathies2025/batchDataMolly/optuna4/optuna_f299ccf3.err
#SBATCH --mail-user=romanbaravalle@gmail.com
#SBATCH --mail-type=end
#SBATCH --export=ALL
export JOBID=$SLURM_JOB_ID
export MSGFILE="/home/rbaravalle/M1_Channelopathies2025/batchDataMolly/optuna4/optuna_f299ccf3.out"
export SGLFILE="/home/rbaravalle/M1_Channelopathies2025/batchDataMolly/optuna4/optuna_f299ccf3.sgl"

export FLOATRUNTK0="weightLong.TPO*=0.5061099115169708"
export FLOATRUNTK1="weightLong.S1*=0.45058602157786976"
export FLOATRUNTK2="weightLong.S2*=0.7478805393962564"
export FLOATRUNTK3="weightLong.cM1*=0.45059529359905853"
export FLOATRUNTK4="weightLong.M2*=0.40376625166536373"
export FLOATRUNTK5="weightLong.OC*=0.37864051373450897"
export FLOATRUNTK6="EEGain*=1.0939092396603576"
export FLOATRUNTK7="IEweights.0*=0.7241994340866678"
export FLOATRUNTK8="IEweights.1*=1.0460085214641164"
export FLOATRUNTK9="IEweights.2*=1.2464929184087095"
export FLOATRUNTK10="IIweights.0*=1.031543287804867"
export FLOATRUNTK11="IIweights.1*=1.4746262221548458"
export FLOATRUNTK12="IIweights.2*=0.8321796046752619"
export STRRUNTK13="saveFolder*=../batchDataMolly/optuna4"
export STRRUNTK14="simLabel*=optuna_f299ccf3"

source ~/.bashrc
source ~/default.sh
conda activate M1_batchTools
export LD_LIBRARY_PATH="/home/rbaravalle/.conda/envs/NetPyNE/lib/python3.10/site-packages/mpi4py_mpich.libs/"

cd /home/rbaravalle/M1_Channelopathies2025/src
time mpirun -n 96 nrniv -python -mpi init.py
wait
