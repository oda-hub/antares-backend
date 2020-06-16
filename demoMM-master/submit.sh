#!/bin/bash


MYDIR=`pwd`
MYIMG=root-c7

## inputs from command line
dec=$1
ra=$2
gamma=$3
roi=$4

#run the docker image and execute the demonstrator program; output produced in the output folder in $PWD
sudo docker run -e DISPLAY=$DISPLAY --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --net=host --volume $MYDIR/:/mnt -it ${MYIMG}  bash -c "mnt/run.sh $dec $ra $gamma $roi"

#sudo docker run -e DISPLAY=$DISPLAY --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --net=host --volume $MYDIR/:/mnt -it ${MYIMG}     #just to run the container e.g. for compiling or coding
#sudo docker run --volume $MYDIR/:/mnt -it ${MYIMG}     #just to run the container e.g. for compiling or coding
