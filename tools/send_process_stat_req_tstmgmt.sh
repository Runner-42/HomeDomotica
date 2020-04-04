#!/bin/bash

exec > >(tee -a "/var/log/homedomotica/HomeDomotica.log") 2>&1
date

if [[ $# -gt 0 ]]
then
    active_environment=$1
else
    active_environment=green
fi

source /home/homedomotica/environments/$active_environment/bin/activate

path_to_src_files=/home/homedomotica/environments/$active_environment/src
pi_reference=TSTMGMT

echo "Sending Process Status Request event on $active_environment environment"
python3 $path_to_src_files/send_process_stat_req.py IQ_RPI_INPUTBUTTON_$pi_reference
python3 $path_to_src_files/send_process_stat_req.py IQ_RPI_OUTPUTLIGHTS_$pi_reference
python3 $path_to_src_files/send_process_stat_req.py IQ_RPI_OUTPUTRELAY_$pi_reference
python3 $path_to_src_files/send_process_stat_req.py IQ_RPI_OUTPUTDIMMER_$pi_reference

deactivate
