#!/bin/bash
#SBATCH --mail-user=hao.qiu@vanderbilt.edu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=1-00:00:00
#SBATCH --mem-per-cpu=10000mb
#SBATCH -o mibenchpvf_default.log

# Load modules
module load GCC/8.2.0  OpenMPI/3.1.4 Intel/2019.1.144  IntelMPI/2018.4.274
module load SciPy-bundle

# Declase PATH Variables
BASEDIR=../
TRACE_TEST=$BASEDIR/TraceDir
# Scan the raw traces in TRACE_OUTPUT, panalyze these raw files on by one automatically
for file in $TRACE_TEST/*; do
	fullfilename="$(basename "$file")"
	filename="${fullfilename%.*}"
	echo "--------------Processing $filename-----------------" 
	python3 panalyzer_main.py --filename $filename
done

