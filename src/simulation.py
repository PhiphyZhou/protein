'''
MD simulation using OpenMM
Abandoned because of run time error "Particle coordinate is nan"
Use NAMD on Marcc instead. 
'''
import os
import mdtraj
import mdtraj.reporters

from simtk import unit
import simtk.openmm as mm
from simtk.openmm import app

import mdtraj.testing

# adjusting parameters
frame_num = 100 # how many frames do you want to simulate
step_size = 2.0 # integration step size in femtoseconds
rec_interval = 1000 # number of steps between two recoded frames

pdb = mdtraj.load(mdtraj.testing.get_fn('native.pdb'))
topology = pdb.topology.to_openmm()

forcefield = app.ForceField('amber99sbildn.xml', 'amber99_obc.xml')
system = forcefield.createSystem(topology, nonbondedMethod=app.CutoffNonPeriodic)
integrator = mm.LangevinIntegrator(330*unit.kelvin, 1.0/unit.picoseconds, step_size*unit.femtoseconds)
simulation = app.Simulation(topology, system, integrator)
simulation.context.setPositions(pdb.xyz[0])
simulation.context.setVelocitiesToTemperature(330*unit.kelvin)

if not os.path.exists('/output/alanine/ala.dcd'):
  simulation.reporters.append(mdtraj.reporters.DCDReporter('/output/alanine/ala.dcd', rec_interval))
  print "begin simulation"
  simulation.step(frame_num*rec_interval)
else:
  raise ValueError("data file /output/alanine/ala.dcd already exists")
