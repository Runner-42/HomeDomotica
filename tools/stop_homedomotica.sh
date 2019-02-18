#!/bin/bash

exec > >(tee -a "/var/log/homedomotica/HomeDomotica.log") 2>&1
date
echo "Stopping Home Domotica processes"

source /home/homedomotica/environments/green/bin/activate

path_to_tool_files=/home/homedomotica/environments/green/tools

h=`hostname`
pi_reference=`echo -n $h|tail -c 1`

echo "Stopping 'inputbutton' process"
python3 $path_to_tool_files/send_stop.py IQ_RPI_INPUTBUTTON_PI$pi_reference
echo "Stopping 'outputrelay' process"
python3 $path_to_tool_files/send_stop.py IQ_RPI_OUTPUTRELAY_PI$pi_reference
echo "Stopping 'outputlights' process"
python3 $path_to_tool_files/send_stop.py IQ_RPI_OUTPUTLIGHTS_PI$pi_reference

deactivate