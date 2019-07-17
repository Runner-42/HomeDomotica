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
pi_reference=TSTMGMT

echo "Sending Set Loglevel Request event on $active_environment environment"
python3 $path_to_source_files/send_set_loglevel_req.py IQ_RPI_LIGHTSIMULATOR_$pi_reference DEBUG

deactivate