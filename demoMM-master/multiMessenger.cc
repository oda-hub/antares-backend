#include<iostream>
#include<fstream>
#include<cstdlib>
#include<vector>
#include<cmath>
#include<string>

#include "TVector3.h"
#include "TFeldmanCousins.h"
#include "TMath.h"



void usage()
{
  std::cerr <<  "\n  Usage: multiMessenger <Declination [deg]> <Right Ascension [deg]> <Spectral Index> <Region of Interest Radius [deg]> \n" 
	    <<  "    <Declination> runs from 50 to -80 \n"
	    <<  "    <Right Ascension> from 0 to 360 \n"
	    <<  "    <Spectral Index> from 1.5 to 3.0 \n"
	    <<  "    <Region of Interest Radius> from 0.1 to 2.5 degrees \n "<<std::endl;
}


double bkg_evaluation(double decl, double roi)
{
  // the background counting rate on the RoI is computed

  // parametrised background distribution from the cumulative taken from data
  const double p0 = 4419.54;
  const double p1 = 49.0835;
  const double p2 = -0.381878;
  const double p3 = -0.00057324;
  const double p4 = 3.50326e-05;
  const double p5 = -3.47092e-07;
  const double p6 = -3.15577e-09;

  // define the declination range of interest
  double dec_low = decl - roi;
  double dec_high = decl + roi;

  // compute the background rate over the full declination band
  double bkg_low = p0 + p1*dec_low + p2*dec_low*dec_low + p3*dec_low*dec_low*dec_low + p4*dec_low*dec_low*dec_low*dec_low + p5*dec_low*dec_low*dec_low*dec_low*dec_low + p6*dec_low*dec_low*dec_low*dec_low*dec_low*dec_low;
  double bkg_high = p0 + p1*dec_high + p2*dec_high*dec_high + p3*dec_high*dec_high*dec_high + p4*dec_high*dec_high*dec_high*dec_high + p5*dec_high*dec_high*dec_high*dec_high*dec_high + p6*dec_high*dec_high*dec_high*dec_high*dec_high*dec_high;
  double bkg_band = bkg_high - bkg_low;

  // compute the solid angle of the full declination band
  double solid_angle = std::abs (2 * 3.14159 * ( std::sin( dec_high * 3.14159/180) - std::sin( dec_low*3.14159/180 ) ) );
    
  // compute the background rate per unid solid angle
  double bkg_rate = bkg_band / solid_angle ;
    
  
  // compute the expected counts in the RoI
  double bkg_count = bkg_rate * 3.14159 * pow(roi * 3.14159/180, 2);
      
  return bkg_count;
}

double Sens(double nbkg)
{
  double CL=0.9; // set confidence level
  TFeldmanCousins FC(CL);
  FC.SetMuMax(200.0); // maximum value of signal to calculate the tables! 
                      // increase it for greater values of Nbackground!
  FC.SetMuStep(0.01);
  double PoisProb=0., mu90=0., ul=0.;  
  for (Int_t Nobserved=0; Nobserved<20; Nobserved++) 
    {
      ul = FC.CalculateUpperLimit(Nobserved, nbkg);
      PoisProb = TMath::Poisson(Nobserved,nbkg);
      mu90 = mu90 + (ul * PoisProb);
    }
  
  return mu90;
}


double UL(double nbkg, double nobs)
{

  double CL=0.9; // set confidence level (90%)
  TFeldmanCousins FC(CL);
  FC.SetMuMax(200.0); // maximum value of signal to calculate the tables!
  FC.SetMuStep(0.01);

  double ul;
  if (nobs <= int(nbkg)) ul = Sens(nbkg);   //if underfluctuation, UL set as the sensitivity
  else  ul = FC.CalculateUpperLimit(nobs, nbkg);		// else FeldmanCousins computation

  return ul;
}


double LL(double nbkg, double nobs)
{
  double CL=0.9; // set confidence level (90%)
  TFeldmanCousins FC(CL);
  FC.SetMuMax(200.0); // maximum value of signal to calculate the tables!

  FC.SetMuStep(0.01);
  double ll= FC.CalculateLowerLimit(nobs, nbkg);

  return ll;
}


int main(int argc, char *argv[] ) {

  //reading input parameters

  if ( argc != 5 )
    {
      usage();
      exit(6);
    }

  double dec, RA, Gamma, RoI;

  dec = std::stof(argv[1]);
  RA = std::stof(argv[2]);
  Gamma = std::stof(argv[3]);
  RoI = std::stof(argv[4]);

  int err = 0;
  
  if(dec < -80 || dec > 50) {
    std::cout << "Declination out of range" << std::endl;
    err = 11;
  }

  if(RA < 0 || RA > 360) {
    std::cout << "Right Ascension out of range" << std::endl;
    err = 11;
  }

  if(Gamma < 1.5 || Gamma > 3.0) {
    std::cout << "Spectral index out of range" << std::endl;
    err = 11;
  }

  if(RoI < 0.1 || RoI > 2.5) {
    std::cout << "Region of interest radius out of range" << std::endl;
    err = 11;
  }

  if (err != 0) exit(err);

 
  // read the ANTARES data tracks and store them in an array of vectors. beta, nhit and time not used for the moment


  ifstream data("ANTARES.data");
  if(!data.is_open()) {
    std::cerr << "ERROR opening input data from ANTARES" << std::endl;
    exit(20);
  }
    
  double ra, d, b, t;
  int h;

  int counter = 0;
  int nevents = 5920;

  TVector3 map_ev[nevents];


  while(counter <= nevents) {
    if (data) {
      data >> ra >> d >> h >> b >> t;
      map_ev[counter].SetXYZ(1,1,1);
      map_ev[counter].SetMag(1);
      map_ev[counter].SetTheta((d+90)*3.14159/180);
      map_ev[counter].SetPhi(ra*3.14169/180);
      counter++;
    }
    else
      {
	std::cerr << "problem reading the ANTARES data file" << std::endl;
	exit(22);
      }
  }


  // set the direction of the input source

  TVector3 dir(1,1,1);
  dir.SetMag(1);
  dir.SetTheta((dec+90)*3.14159/180);
  dir.SetPhi(RA*3.14159/180);

  // now we start doing the cut and count analysis

  double bkg = bkg_evaluation(dec, RoI);
  int obs = 0; // to count the observed events

  counter = 0;  // to loop over the events
  double angle;
  while(counter <= nevents) {
    angle = dir.Angle(map_ev[counter]);
    if (angle < RoI*3.14159/180) obs++;
    counter++;

  }

  std::cout << "estimated background: " << bkg << std::endl;
  std::cout << "number of observed events: " << obs << std::endl;

  double n_ul = UL(bkg, obs);
  double n_ll = LL(bkg, obs);

  
  // read the acceptance table

  ifstream acceptance("acc.txt");
  if(!acceptance.is_open()) {
    std::cerr << "ERROR opening input data for ANTARES effective areas" << std::endl;
    exit(21);
  }



  std::vector <double> vec_acc[16];
  double a;

  for (int j = 0; j < 16; j++) {	//spectral index
    for(int i = 0; i < 20; i++) {	//sin(decl) bin
      if(acceptance) {
	acceptance >> a;
	vec_acc[j].push_back(a);
      }
      else
	{
	  std::cerr << "problem reading the ANTARES effective area file " << std::endl;
	  exit(23);
	}
    }
  }

  // get the bin value from the input declination and spectral index
  int bin_a = (int) (std::sin(dec*3.14159/180)+1)*10;
  int bin_gamma = (int) (Gamma*10) - 15;


  double f_ul = n_ul/vec_acc[bin_gamma][bin_a]*1e-8;  // flux = n_ev/acceptance
  double f_ll = n_ll/vec_acc[bin_gamma][bin_a]*1e-8;

  std::cout << "flux UL (Norm. @1 GeV) " << f_ul << " [(GeV cm s)^-1]" << std::endl;
  std::cout << "flux LL (Norm. @1 GeV) " << f_ll << " [(GeV cm s)^-1]" <<  std::endl;

  std::cout << "flux UL (Norm. @100 TeV) " << f_ul*pow(1e-5, Gamma) << " [(GeV cm s)^-1]" << std::endl;
  std::cout << "flux LL (Norm. @100 TeV) " << f_ll*pow(1e-5, Gamma) << " [(GeV cm s)^-1]" <<  std::endl;


//  char e;
//  std::cout << "press any character to quit" << std::endl;
//  std::cin >> e;
  return 0;

}
