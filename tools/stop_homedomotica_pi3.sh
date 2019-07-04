#!/bin/bash

exec > >(tee -a "/var/log/homedomotica/HomeDomotica.log") 2>&1
date

if [[ $# -gt 0 ]]
then
    active_environment=$1
else
    active_environment=green
fi

echo "Stopping Home Domotica processes on $active_environment environment"

source /home/homedomotica/environments/$active_environment/bin/activate

path_to_source_files=/home/homedomotica/environments/$active_environment/src
pi_reference=pi3

echo "Stopping 'inputbutton' process"
python3 $path_to_source_files/send_stop_req.py IQ_RPI_INPUTBUTTON_$pi_reference
echo "Stopping 'outputrelay' process"
python3 $path_to_source_files/send_stop_req.py IQ_RPI_OUTPUTRELAY_$pi_reference
echo "Stopping 'outputlights' process"
python3 $path_to_source_files/send_stop_req.py IQ_RPI_OUTPUTLIGHTS_$pi_reference
echo "Stopping 'outputdimmer' process"
python3 $path_to_source_files/send_stop_req.py IQ_RPI_OUTPUTDIMMER_$pi_reference

deactivate