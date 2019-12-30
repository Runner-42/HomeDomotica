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

path_to_source_files=/home/homedomotica/environments/$active_environment/src
pi_reference=TST1

echo "Sending Set Loglevel Request event on $active_environment environment"
python3 $path_to_source_files/send_set_loglevel_req.py IQ_RPI_INPUTBUTTON_$pi_reference DEBUG
python3 $path_to_source_files/send_set_loglevel_req.py IQ_RPI_OUTPUTLIGHTS_$pi_reference DEBUG
python3 $path_to_source_files/send_set_loglevel_req.py IQ_RPI_OUTPUTRELAY_$pi_reference DEBUG
python3 $path_to_source_files/send_set_loglevel_req.py IQ_RPI_OUTPUTDIMMER_$pi_reference DEBUG
python3 $path_to_source_files/send_set_loglevel_req.py IQ_RPI_OUTPUTVENTILATOR_$pi_reference DEBUG

deactivate