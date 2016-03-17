'''
MD simulation using OpenMM
'''
import os
import mdtraj
import mdtraj.reporters

from simtk import unit
import simtk.openmm as mm
from simtk.openmm import app

import mdtraj.testing

frame_num = 1000 # how many frames do you want to simulate

pdb = mdtraj.load(mdtraj.testing.get_fn('native.pdb'))
topology = pdb.topology.to_openmm()

forcefield = app.ForceField('amber99sbildn.xml', 'amber99_obc.xml')
system = forcefield.createSystem(topology, nonbondedMethod=app.CutoffNonPeriodic)
# the integration step is 0.25 pico-seconds
integrator = mm.LangevinIntegrator(330*unit.kelvin, 1.0/unit.picoseconds, 250.0*unit.femtoseconds)
simulation = app.Simulation(topology, system, integrator)
simulation.context.setPositions(pdb.xyz[0])
simulation.context.setVelocitiesToTemperature(330*unit.kelvin)

if not os.path.exists('/output/alanine/ala.dcd'):
    # the frame interval is 0.25 nano-seconds
    simulation.reporters.append(mdtraj.reporters.DCDReporter('/output/alanine/ala.dcd', 1000))
    simulation.step(frame_num*1000)
else:
    raise ValueError("data file /output/alanine/ala.dcd already exists")
