#!/usr/bin/env python

import sys
from geant4_pybind import *

class XXDetectorConstruction(G4VUserDetectorConstruction):
   """
   Simple model: a sphere with water in the box with air.
   """
 
   def __init__(self):
     super().__init__()
     self.fScoringVolume = None
 
   def Construct(self):
     nist = G4NistManager.Instance()
 
     envelop_x = 10*cm
     envelop_y = 10*cm
     envelop_z = 10*cm
 
     envelop_mat = nist.FindOrBuildMaterial("G4_AIR")

#....Skull
     sphere_rad = 7*cm
     mat1 = nist.FindOrBuildMaterial("G4_B-100_BONE")

#....Water orb
     orb_rad = 6*cm
     mat2 = nist.FindOrBuildMaterial("G4_WATER")

#....Mozg
     xSemiAxis1 = 3*cm
     ySemiAxis1 = 2.5*cm
     zSemiAxis1 = 5*cm
     mat3 = nist.FindOrBuildMaterial("G4_Benzene")
     #1.0 = (envelop_x/xSemiAxis1)**2 + (envelop_y/ySemiAxis1)**2 + (envelop_z/zSemiAxis1)**2

     xSemiAxis2 = 2*cm
     ySemiAxis2 = 4*cm
     zSemiAxis2 = 2.5*cm
     mat4 = nist.FindOrBuildMaterial("G4_Acetone")
     #1.0 = (envelop_x/xSemiAxis2)**2 + (envelop_y/ySemiAxis2)**2 + (envelop_z/zSemiAxis2)**2

#....Check for Overlaps
     checkOverlaps = True
 
#....World creating 
     world_x = 1.4*envelop_x
     world_y = 1.4*envelop_y
     world_z = 1.4*envelop_z
 
     sWorld = G4Box("World", 0.5*world_x, 0.5*world_y,
                    0.5*world_z)
 
     lWorld = G4LogicalVolume(sWorld, envelop_mat, "World")
 
     pWorld = G4PVPlacement(None, G4ThreeVector(),
                            lWorld, "World", None, False,
                            0, checkOverlaps)
 
#....Geometry volume creating 
     sSphere = G4Sphere("Skull", sphere_rad)
     sOrb = G4Orb("Blood", orb_rad)
     sBrain1 = G4Ellipsoid("Brain1", xSemiAxis1, ySemiAxis1, zSemiAxis1, 0, 0)
     sBrain2 = G4Ellipsoid("Brain2", xSemiAxis2, ySemiAxis2, zSemiAxis2, 0, 0)

#....Logical volume creating
     lSphere = G4LogicalVolume(sSphere, mat1, "Skull")
     lOrb = G4LogicalVolume(sOrb, mat2, "Blood")
     lBrain1 = G4LogicalVolume(sBrain1, mat3, "Brain1")
     lBrain2 = G4LogicalVolume(sBrain2, mat4, "Brain2")

#....Physical volume creating
     G4PVPlacement(None, G4ThreeVector(), lSphere,
                   "Skull", lWorld, True, 0, checkOverlaps)
     G4PVPlacement(None, G4ThreeVector(), lOrb,
                   "Blood", lSphere, True, 0, checkOverlaps)
     G4PVPlacement(None, G4ThreeVector(0, 0.3*orb_rad, 0), lBrain1,
                   "Brain1", lOrb, True, 0, checkOverlaps)
     G4PVPlacement(None, G4ThreeVector(0.3*orb_rad, 0.15*orb_rad, 0), lBrain2, 
                   "Brain2", lOrb, True, 0, checkOverlaps)

     self.fScoringVolume = lSphere
 

     return pWorld


ui = None
if len(sys.argv) == 1:
  ui = G4UIExecutive(len(sys.argv), sys.argv)

# Optionally: choose a different Random engine...
# G4Random.setTheEngine(MTwistEngine())

runManager = G4RunManagerFactory.CreateRunManager(G4RunManagerType.Serial)

runManager.SetUserInitialization(XXDetectorConstruction())

# Physics list
physicsList = QBBC()
physicsList.SetVerboseLevel(1)

runManager.SetUserInitialization(physicsList)

# User action initialization
#runManager.SetUserInitialization(XXActionInitialization())

visManager = G4VisExecutive()
# G4VisExecutive can take a verbosity argument - see /vis/verbose guidance.
# visManager = G4VisExecutive("Quiet")
visManager.Initialize()

# Get the User Interface manager
UImanager = G4UImanager.GetUIpointer()

# # Process macro or start UI session
if ui == None:
  # batch mode
  command = "/control/execute "
  fileName = sys.argv[1]
  UImanager.ApplyCommand(command + fileName)
else:
  # interactive mode
  UImanager.ApplyCommand("/control/execute init_vis.mac")
  ui.SessionStart()