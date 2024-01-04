#!/usr/bin/env python

import sys
from geant4_pybind import *
import math 

#Detector construction
class ExamDetectorConstruction(G4VUserDetectorConstruction):
 
   def __init__(self):
      super().__init__()
      self.fScoringVolume = None
 
   def Construct(self):
      nist = G4NistManager.Instance()

      envelop_x = 60*cm
      envelop_y = 60*cm
      envelop_z = 60*cm

      envelop_mat = nist.FindOrBuildMaterial("G4_AIR")

      zTrans = G4Transform3D(G4RotationMatrix(), G4ThreeVector(0.1*envelop_x, 0, 0.05*envelop_z))

#.....Leg
      mat_leg = nist.FindOrBuildMaterial("G4_TISSUE_SOFT_ICRP")
      
#.....Prosthesis
      mat_p = nist.FindOrBuildMaterial("G4_Ti")

#.....Check for Overlaps
      checkOverlaps = True

#.....World creating 
      world_x = 1*envelop_x
      world_y = 1*envelop_y
      world_z = 1.2*envelop_z

      sWorld = G4Box("World", 0.5*world_x, 0.5*world_y, 0.5*world_z)
 
      lWorld = G4LogicalVolume(sWorld, envelop_mat, "World")
 
      pWorld = G4PVPlacement(None, G4ThreeVector(), lWorld, "World", None, False, 0, checkOverlaps)

#.....Geometry volume creating

      sLeg = G4Tubs("Leg", 0, 0.3*envelop_x, 0.5*envelop_y, 2*math.pi, 2*math.pi)
      sProsthesis = G4Tubs("Prosthesis", 0, 0.05*envelop_x, 0.5*envelop_y, 2*math.pi, 2*math.pi)
      sCut = G4SubtractionSolid("Cut", sProsthesis, sLeg, zTrans)

#.....Logical volume creating

      lLeg = G4LogicalVolume(sLeg, mat_leg, "Leg")
      lProsthesis = G4LogicalVolume(sProsthesis, mat_p, "Prosthesis")

#.....Physical volume creating

      G4PVPlacement(None, G4ThreeVector(), lLeg, "Leg", lWorld, True, 0, checkOverlaps)
      G4PVPlacement(None, G4ThreeVector(0.1*envelop_x, 0.05*envelop_y, 0), lProsthesis, "Prosthesis", lLeg, True, 0, checkOverlaps)

      self.fScoringVolume = lLeg

      return pWorld
#End of detector construction

#..........

#Primary Generator
class ExamPrimaryGeneratorAction(G4VUserPrimaryGeneratorAction):
    def __init__(self):
        super().__init__()
        self.fEnvelopeBox = None
        self.fParticleGun = G4ParticleGun(1)

        particleTable = G4ParticleTable.GetParticleTable()
        particle = particleTable.FindParticle("neutron")
        self.fParticleGun.SetParticleDefinition(particle)
        self.fParticleGun.SetParticleMomentumDirection(G4ThreeVector(1, 0, 0))
        self.fParticleGun.SetParticleEnergy(10*MeV)

    def GeneratePrimaries(self, anEvent):
        envSizeX = 0
        envSizeY = 0
        envSizeZ = 0
    
        if self.fEnvelopeBox == None:
            envLV = G4LogicalVolumeStore.GetInstance().GetVolume("World")

            if envLV != None:
                self.fEnvelopeBox = envLV.GetSolid()
          
            if self.fEnvelopeBox != None:
                envSizeX = self.fEnvelopeBox.GetXHalfLength()*2
                envSizeY = self.fEnvelopeBox.GetYHalfLength()*2
                envSizeZ = self.fEnvelopeBox.GetZHalfLength()*2
            else:
                msg = "Envelope volume of box shape not found.\n"
                msg += "Perhaps you have changed geometry.\n"
                msg += "The gun will be place at the center."
                G4Exception("ExamPrimaryGeneratorAction::GeneratePrimaries()", "MyCode0002", G4ExceptionSeverity.JustWarning, msg)

            x0 = -0.5 * envSizeX
            y0 = 0
            z0 = 0
            self.fParticleGun.SetParticlePosition(G4ThreeVector(x0, y0, z0))
            self.fParticleGun.GeneratePrimaryVertex(anEvent)
#End of primary generator

#..........

#Action Initialization

class ExamActionInitialization(G4VUserActionInitialization):
    
    def Build(self) -> None:
        self.SetUserAction(ExamPrimaryGeneratorAction())
#End of Action Initialization


ui = None
if len(sys.argv) == 1:
  ui = G4UIExecutive(len(sys.argv), sys.argv)

# Optionally: choose a different Random engine...
# G4Random.setTheEngine(MTwistEngine())

runManager = G4RunManagerFactory.CreateRunManager(G4RunManagerType.Serial)

runManager.SetUserInitialization(ExamDetectorConstruction())

# Physics list
physicsList = QBBC()
physicsList.SetVerboseLevel(1)

runManager.SetUserInitialization(physicsList)

# User action initialization
runManager.SetUserInitialization(ExamActionInitialization())

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
