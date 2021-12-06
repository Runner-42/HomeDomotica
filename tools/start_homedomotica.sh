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

log_level=DEBUG

path_to_source_file=/home/homedomotica/environments/$active_environment/src
path_to_configuration_file=/home/homedomotica/environments/$active_environment/config

# Extract pi reference as the last character of the hostname
# example DomoticaPi1 => pi reference = 1
h=`hostname`
pi_reference=`echo -n $h|tail -c 1`

echo "Starting 'inputbutton' process"
python3  $path_to_source_file/rpi_inputbutton_pi$pi_reference.py -l $log_level -cfp $path_to_configuration_file &
echo "Starting 'outputrelay' process"
python3  $path_to_source_file/rpi_outputrelay_pi$pi_reference.py -l $log_level -cfp $path_to_configuration_file &
echo "Starting 'outputlights' process"
python3  $path_to_source_file/rpi_outputlights_pi$pi_reference.py -l $log_level -cfp $path_to_configuration_file &
echo "Starting 'outputdimmer' process"
python3  $path_to_source_file/rpi_outputdimmer_pi$pi_reference.py -l $log_level -cfp $path_to_configuration_file &
deactivate
