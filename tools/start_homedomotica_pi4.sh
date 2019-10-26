#!/bin/bash

exec > >(tee -a "/var/log/homedomotica/HomeDomotica.log") 2>&1
date

if [[ $# -gt 0 ]]
then
    active_environment=$1
else
    active_environment=green
fi

echo "Starting Home Domotica processes on $active_environment environment"

source /home/homedomotica/environments/$active_environment/bin/activate

log_level=INFO
path_to_source_file=/home/homedomotica/environments/$active_environment/src
path_to_configuration_file=/home/homedomotica/environments/$active_environment/config
pi_reference=pi4

echo "Starting 'outputventilator' process"
python3  $path_to_source_file/rpi_outputventilator_$pi_reference.py -l $log_level -cfp $path_to_configuration_file &

deactivate
