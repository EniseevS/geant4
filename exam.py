#!/usr/bin/env python

import sys
from geant4_pybind import *
import math 

class X5DetectorConstruction(G4VUserDetectorConstruction):
   """
   Simple model: a sphere with water in the box with air.
   """
 
   def __init__(self):
     super().__init__()
     self.fScoringVolume = None
 
   def Construct(self):
     nist = G4NistManager.Instance()

     envelop_x = 60*cm
     envelop_y = 60*cm
     envelop_z = 60*cm

     envelop_mat = nist.FindOrBuildMaterial("G4_AIR")

#....Leg
     
