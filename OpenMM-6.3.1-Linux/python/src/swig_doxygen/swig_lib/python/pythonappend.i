%pythonappend OpenMM::Integrator::getStepSize() const %{
   val=unit.Quantity(val, unit.picosecond)
%}

%pythonappend OpenMM::LangevinIntegrator::getTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::LangevinIntegrator::getFriction() const %{
   val=unit.Quantity(val, 1/unit.picosecond)
%}

%pythonappend OpenMM::CustomGBForce::getCutoffDistance() const %{
   val=unit.Quantity(val, unit.nanometers)
%}

%pythonappend OpenMM::CustomGBForce::addTabulatedFunction(const std::string & name, TabulatedFunction * function) %{
   args[1].thisown=0
%}

%pythonappend OpenMM::CustomNonbondedForce::getCutoffDistance() const %{
   val=unit.Quantity(val, unit.nanometers)
%}

%pythonappend OpenMM::CustomNonbondedForce::getSwitchingDistance() const %{
   val=unit.Quantity(val, unit.nanometers)
%}

%pythonappend OpenMM::CustomNonbondedForce::addTabulatedFunction(const std::string & name, TabulatedFunction * function) %{
   args[1].thisown=0
%}

%pythonappend OpenMM::VariableLangevinIntegrator::getTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::VariableLangevinIntegrator::getFriction() const %{
   val=unit.Quantity(val, 1/unit.picosecond)
%}

%pythonappend OpenMM::AmoebaWcaDispersionForce::getParticleParameters(int particleIndex, double & radius, double & epsilon) const %{
   val[0]=unit.Quantity(val[0], unit.nanometer)
   val[1]=unit.Quantity(val[1], unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::AmoebaWcaDispersionForce::getEpso() const %{
   val=unit.Quantity(val, unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::AmoebaWcaDispersionForce::getEpsh() const %{
   val=unit.Quantity(val, unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::AmoebaWcaDispersionForce::getRmino() const %{
   val=unit.Quantity(val, unit.nanometer)
%}

%pythonappend OpenMM::AmoebaWcaDispersionForce::getRminh() const %{
   val=unit.Quantity(val, unit.nanometer)
%}

%pythonappend OpenMM::AmoebaWcaDispersionForce::getAwater() const %{
   val=unit.Quantity(val, 1/(unit.nanometer*unit.nanometer*unit.nanometer))
%}

%pythonappend OpenMM::AmoebaWcaDispersionForce::getDispoff() const %{
   val=unit.Quantity(val, unit.nanometer)
%}

%pythonappend OpenMM::RPMDIntegrator::getTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::RPMDIntegrator::getFriction() const %{
   val=unit.Quantity(val, 1/unit.picosecond)
%}

%pythonappend OpenMM::RPMDIntegrator::getTotalEnergy() %{
   val=unit.Quantity(val, unit.kilojoules_per_mole)
%}

%pythonappend OpenMM::AmoebaInPlaneAngleForce::getAngleParameters(int index, int & particle1, int & particle2, int & particle3, int & particle4, double & length, double & quadraticK) const %{
   val[4]=unit.Quantity(val[4], unit.radian)
   val[5]=unit.Quantity(val[5], unit.kilojoule_per_mole/(unit.radian*unit.radian))
%}

%pythonappend OpenMM::Platform::registerPlatform(Platform * platform) %{
   args[0].thisown=0
%}

%pythonappend OpenMM::DrudeSCFIntegrator::getMinimizationErrorTolerance() const %{
   val=unit.Quantity(val, unit.kilojoules_per_mole/unit.nanometer)
%}

%pythonappend OpenMM::MonteCarloMembraneBarostat::getDefaultPressure() const %{
   val=unit.Quantity(val, unit.bar)
%}

%pythonappend OpenMM::MonteCarloMembraneBarostat::getDefaultSurfaceTension() const %{
   val=unit.Quantity(val, unit.bar*unit.nanometer)
%}

%pythonappend OpenMM::MonteCarloMembraneBarostat::getTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::MonteCarloBarostat::getDefaultPressure() const %{
   val=unit.Quantity(val, unit.bar)
%}

%pythonappend OpenMM::MonteCarloBarostat::getTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::AmoebaBondForce::getBondParameters(int index, int & particle1, int & particle2, double & length, double & quadraticK) const %{
   val[2]=unit.Quantity(val[2], unit.nanometer)
   val[3]=unit.Quantity(val[3], unit.kilojoule_per_mole/(unit.nanometer*unit.nanometer))
%}

%pythonappend OpenMM::AmoebaPiTorsionForce::getPiTorsionParameters(int index, int & particle1, int & particle2, int & particle3, int & particle4, int & particle5, int & particle6, double & k) const %{
   val[6]=unit.Quantity(val[6], unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::CustomCompoundBondForce::addTabulatedFunction(const std::string & name, TabulatedFunction * function) %{
   args[1].thisown=0
%}

%pythonappend OpenMM::CustomManyParticleForce::getCutoffDistance() const %{
   val=unit.Quantity(val, unit.nanometers)
%}

%pythonappend OpenMM::CustomManyParticleForce::addTabulatedFunction(const std::string & name, TabulatedFunction * function) %{
   args[1].thisown=0
%}

%pythonappend OpenMM::GBVIForce::getParticleParameters(int index, double & charge, double & radius, double & gamma) const %{
   val[0]=unit.Quantity(val[0], unit.elementary_charge)
   val[1]=unit.Quantity(val[1], unit.nanometer)
   val[2]=unit.Quantity(val[2], unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::GBVIForce::getBondParameters(int index, int & particle1, int & particle2, double & distance) const %{
   val[2]=unit.Quantity(val[2], unit.nanometer)
%}

%pythonappend OpenMM::GBVIForce::getCutoffDistance() const %{
   val=unit.Quantity(val, unit.nanometers)
%}

%pythonappend OpenMM::GBVIForce::getQuinticUpperBornRadiusLimit() const %{
   val=unit.Quantity(val, unit.nanometer)
%}

%pythonappend OpenMM::GBSAOBCForce::getParticleParameters(int index, double & charge, double & radius, double & scalingFactor) const %{
   val[0]=unit.Quantity(val[0], unit.elementary_charge)
   val[1]=unit.Quantity(val[1], unit.nanometer)
%}

%pythonappend OpenMM::GBSAOBCForce::getSurfaceAreaEnergy() const %{
   val=unit.Quantity(val, unit.kilojoule_per_mole/unit.nanometer/unit.nanometer)
%}

%pythonappend OpenMM::GBSAOBCForce::getCutoffDistance() const %{
   val=unit.Quantity(val, unit.nanometers)
%}

%pythonappend OpenMM::NonbondedForce::getCutoffDistance() const %{
   val=unit.Quantity(val, unit.nanometers)
%}

%pythonappend OpenMM::NonbondedForce::getSwitchingDistance() const %{
   val=unit.Quantity(val, unit.nanometers)
%}

%pythonappend OpenMM::NonbondedForce::getPMEParameters(double & alpha, int & nx, int & ny, int & nz) const %{
   val[0]=unit.Quantity(val[0], 1/unit.nanometer)
%}

%pythonappend OpenMM::NonbondedForce::getParticleParameters(int index, double & charge, double & sigma, double & epsilon) const %{
   val[0]=unit.Quantity(val[0], unit.elementary_charge)
   val[1]=unit.Quantity(val[1], unit.nanometer)
   val[2]=unit.Quantity(val[2], unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::NonbondedForce::getExceptionParameters(int index, int & particle1, int & particle2, double & chargeProd, double & sigma, double & epsilon) const %{
   val[2]=unit.Quantity(val[2], unit.elementary_charge*unit.elementary_charge)
   val[3]=unit.Quantity(val[3], unit.nanometer)
   val[4]=unit.Quantity(val[4], unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::AmoebaGeneralizedKirkwoodForce::getParticleParameters(int index, double & charge, double & radius, double & scalingFactor) const %{
   val[0]=unit.Quantity(val[0], unit.elementary_charge)
   val[1]=unit.Quantity(val[1], unit.nanometer)
%}

%pythonappend OpenMM::AmoebaGeneralizedKirkwoodForce::getProbeRadius() const %{
   val=unit.Quantity(val, unit.nanometer)
%}

%pythonappend OpenMM::AmoebaGeneralizedKirkwoodForce::getSurfaceAreaFactor() const %{
   val=unit.Quantity(val, (unit.nanometer*unit.nanometer)/unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::BrownianIntegrator::getTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::BrownianIntegrator::getFriction() const %{
   val=unit.Quantity(val, 1/unit.picosecond)
%}

%pythonappend OpenMM::LocalCoordinatesSite::getLocalPosition() const %{
   val=unit.Quantity(val, unit.nanometer)
%}

%pythonappend OpenMM::RBTorsionForce::getTorsionParameters(int index, int & particle1, int & particle2, int & particle3, int & particle4, double & c0, double & c1, double & c2, double & c3, double & c4, double & c5) const %{
   val[4]=unit.Quantity(val[4], unit.kilojoules_per_mole)
   val[5]=unit.Quantity(val[5], unit.kilojoules_per_mole)
   val[6]=unit.Quantity(val[6], unit.kilojoules_per_mole)
   val[7]=unit.Quantity(val[7], unit.kilojoules_per_mole)
   val[8]=unit.Quantity(val[8], unit.kilojoules_per_mole)
   val[9]=unit.Quantity(val[9], unit.kilojoules_per_mole)
%}

%pythonappend OpenMM::RPMDMonteCarloBarostat::getDefaultPressure() const %{
   val=unit.Quantity(val, unit.bar)
%}

%pythonappend OpenMM::MonteCarloAnisotropicBarostat::getDefaultPressure() const %{
   val=unit.Quantity(val, unit.bar)
%}

%pythonappend OpenMM::MonteCarloAnisotropicBarostat::getTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::AmoebaOutOfPlaneBendForce::getOutOfPlaneBendParameters(int index, int & particle1, int & particle2, int & particle3, int & particle4, double & k) const %{
   val[4]=unit.Quantity(val[4], unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::CustomHbondForce::getCutoffDistance() const %{
   val=unit.Quantity(val, unit.nanometers)
%}

%pythonappend OpenMM::CustomHbondForce::addTabulatedFunction(const std::string & name, TabulatedFunction * function) %{
   args[1].thisown=0
%}

%pythonappend OpenMM::System::getParticleMass(int index) const %{
   val=unit.Quantity(val, unit.amu)
%}

%pythonappend OpenMM::System::setVirtualSite(int index, VirtualSite * virtualSite) %{
   args[1].thisown=0
%}

%pythonappend OpenMM::System::getConstraintParameters(int index, int & particle1, int & particle2, double & distance) const %{
   val[2]=unit.Quantity(val[2], unit.nanometer)
%}

%pythonappend OpenMM::System::addForce(Force * force) %{
   args[0].thisown=0
%}

%pythonappend OpenMM::System::getDefaultPeriodicBoxVectors(Vec3 & a, Vec3 & b, Vec3 & c) const %{
   val[0]=unit.Quantity(val[0], unit.nanometer)
   val[1]=unit.Quantity(val[1], unit.nanometer)
   val[2]=unit.Quantity(val[2], unit.nanometer)
%}

%pythonappend OpenMM::HarmonicAngleForce::getAngleParameters(int index, int & particle1, int & particle2, int & particle3, double & angle, double & k) const %{
   val[3]=unit.Quantity(val[3], unit.radian)
   val[4]=unit.Quantity(val[4], unit.kilojoule_per_mole/(unit.radian*unit.radian))
%}

%pythonappend OpenMM::AmoebaMultipoleForce::getCutoffDistance() const %{
   val=unit.Quantity(val, unit.nanometer)
%}

%pythonappend OpenMM::AmoebaMultipoleForce::getAEwald() const %{
   val=unit.Quantity(val, 1/unit.nanometer)
%}

%pythonappend OpenMM::AmoebaAngleForce::getAngleParameters(int index, int & particle1, int & particle2, int & particle3, double & length, double & quadraticK) const %{
   val[3]=unit.Quantity(val[3], unit.radian)
   val[4]=unit.Quantity(val[4], unit.kilojoule_per_mole/(unit.radian*unit.radian))
%}

%pythonappend OpenMM::AmoebaVdwForce::getParticleParameters(int particleIndex, int & parentIndex, double & sigma, double & epsilon, double & reductionFactor) const %{
   val[1]=unit.Quantity(val[1], unit.nanometer)
   val[2]=unit.Quantity(val[2], unit.kilojoule_per_mole)
%}

%pythonappend OpenMM::AmoebaVdwForce::getCutoff() const %{
   val=unit.Quantity(val, unit.nanometer)
%}

%pythonappend OpenMM::DrudeLangevinIntegrator::getTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::DrudeLangevinIntegrator::getFriction() const %{
   val=unit.Quantity(val, 1/unit.picosecond)
%}

%pythonappend OpenMM::DrudeLangevinIntegrator::getDrudeTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::DrudeLangevinIntegrator::getDrudeFriction() const %{
   val=unit.Quantity(val, 1/unit.picosecond)
%}

%pythonappend OpenMM::AndersenThermostat::getDefaultTemperature() const %{
   val=unit.Quantity(val, unit.kelvin)
%}

%pythonappend OpenMM::AndersenThermostat::getDefaultCollisionFrequency() const %{
   val=unit.Quantity(val, 1/unit.picosecond)
%}

%pythonappend OpenMM::HarmonicBondForce::getBondParameters(int index, int & particle1, int & particle2, double & length, double & k) const %{
   val[2]=unit.Quantity(val[2], unit.nanometer)
   val[3]=unit.Quantity(val[3], unit.kilojoule_per_mole/(unit.nanometer*unit.nanometer))
%}

%pythonappend OpenMM::AmoebaStretchBendForce::getStretchBendParameters(int index, int & particle1, int & particle2, int & particle3, double & lengthAB, double & lengthCB, double & angle, double & k1, double & k2) const %{
   val[3]=unit.Quantity(val[3], unit.nanometer)
   val[4]=unit.Quantity(val[4], unit.nanometer)
   val[5]=unit.Quantity(val[5], unit.radian)
   val[6]=unit.Quantity(val[6], unit.kilojoule_per_mole/unit.nanometer/unit.degree)
   val[7]=unit.Quantity(val[7], unit.kilojoule_per_mole/unit.nanometer/unit.degree)
%}

%pythonappend OpenMM::PeriodicTorsionForce::getTorsionParameters(int index, int & particle1, int & particle2, int & particle3, int & particle4, int & periodicity, double & phase, double & k) const %{
   val[5]=unit.Quantity(val[5], unit.radian)
   val[6]=unit.Quantity(val[6], unit.kilojoule_per_mole)
%}

