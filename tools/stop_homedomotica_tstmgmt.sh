#!/bin/bash

exec > >(tee -a "/var/log/homedomotica/HomeDomotica.log") 2>&1
date

if [[ $# -gt 0 ]]
then
    active_environment=$1
else
    active_environment=green
fi

echo "Stopping Home Domotica Management processes on $active_environment environment"

source /home/homedomotica/environments/$active_environment/bin/activate

path_to_source_files=/home/homedomotica/environments/$active_environment/src
pi_reference=TSTMGMT

echo "Stopping 'lightsimulator' process"
python3 $path_to_source_files/send_stop_req.py IQ_RPI_LIGHTSIMULATOR_$pi_reference

#echo "Stopping Portal"
#Port=8000
#pid=`ps ax | grep gunicorn | grep $Port | awk '{split($0,a," "); print a[1]}' | head -n 1`
#if [ -z "$pid" ]; then
#  echo "Nothing to stop, no gunicorn deamon running on port $Port"
#else
#  kill $pid
#  echo "Stopping gunicorn deamon on port $Port"
#fi

deactivate