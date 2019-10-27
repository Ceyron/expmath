#!/bin/bash

# Loop over all old image ids and remove them
while :
do
    line=$(sudo docker images | grep -v expmath | grep -v ubuntu | \
        grep -v REPOSITORY)
    id=$(echo ${line} | cut -d " " -f3)

    if [[ ${id} != "" ]]
    then
        sudo docker image rm ${id}
    else
        break
    fi
done
