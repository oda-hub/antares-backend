#!/bin/bash

dec=$1
ra=$2
gamma=$3
roi=$4

cd /mnt

./multiMessenger $dec $ra $gamma $roi > output/source_at_${ra}_${dec}_gamma${gamma}_roi${roi}.txt

exit
