demonstrator for a point-source search using ANTARES public data

Dockerfile

creates a docker image for a centos7 machine with root and basic c++ compiler

docker build -t root-c7 .

multiMessenger.cc

runs a quick counting analysis based on Feldman & Cousins evaluation of Upper Limits
using the public ANTARES data set
from the counting statistics, the flux limit is computed using ANTARES acceptances (tabulated in
acc.txt -- provided by the ANTARES collaboration for different spectral indexes)

(see http://antares.in2p3.fr/publicdata2012.html for more details on the data set)

should be compiled "with make.sh" within the container

  Usage: multiMessenger <Declination [deg]> <Right Ascension [deg]> <Spectral Index> <Region of Interest Radius [deg]> 
    <Declination> runs from 50 to -80 
    <Right Ascension> from 0 to 360 
    <Spectral Index> from 1.5 to 3.0 
    <Region of Interest Radius> from 0.1 to 2.5 degrees 


./submit.sh  dec  ra  gamma  roi

produces in the output folder a txt with the result from that source 
(UL and LL at 1 GeV or 100 TeV normalisation)
