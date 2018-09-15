#!/bin/bash

exec > >(tee -a "/var/log/homedomotica/HomeDomotica.log") 2>&1
date
echo "Starting Home Domotica processes"

source /home/homedomotica/environments/green/bin/activate

log_level=DEBUG

path_to_source_file=/home/homedomotica/environments/green/src
path_to_configuration_file=/home/homedomotica/environments/green/config

# Extract pi reference as the last character of the hostname
# example DomoticaPi1 => pi reference = 1
h=`hostname`
pi_reference=`echo -n $h|tail -c 1`

echo "Starting 'inputbutton' process"
python3  $path_to_source_file/rpi_inputbutton_pi$pi_reference.py -l $log_level -cfp $path_to_configuration_file &
echo "Starting 'outputrelay' process"
python3  $path_to_source_file/rpi_outputrelay_pi$pi_reference.py -l $log_level -cfp $path_to_configuration_file &

deactivate
