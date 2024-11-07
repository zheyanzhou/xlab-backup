#include "CaloHitSmearAlg.h"

// Gaudi
#include "GaudiKernel/IRndmEngine.h"
#include <GaudiKernel/MsgStream.h>
#include <cmath>

// edm4hep
#include "SimKernel/Units.h"
#include "edm4hep/SimCalorimeterHitCollection.h"

using namespace megat;

DECLARE_COMPONENT( CaloHitSmearAlg )

CaloHitSmearAlg::CaloHitSmearAlg( const std::string& aName, ISvcLocator* aSvcLoc )
    : GaudiAlgorithm( aName, aSvcLoc ) {
  declareProperty( "inHits", m_inHits, "Segmented Hit Collection of Calorimeter" );
  declareProperty( "outHits", m_outHits, "Smeared Hit Collection" );
}
CaloHitSmearAlg::~CaloHitSmearAlg() {}

StatusCode CaloHitSmearAlg::initialize() {
  /// mandatory
  if ( GaudiAlgorithm::initialize().isFailure() ) return StatusCode::FAILURE;

  // unit conversion
  fEnergyRef = fEnergyRef * CLHEP::keV / edmdefault::energy;
    
  // Initialize the random number generator
  auto sc = m_sigmaGenE.initialize( randSvc(), Rndm::Gauss( 0.0, 1.0 ) );
  if ( !sc.isSuccess() ) { return StatusCode::FAILURE; }

  return StatusCode::SUCCESS;
}

StatusCode CaloHitSmearAlg::execute() {
  /// input
  const auto in_hits = m_inHits.get();

  /// output
  auto out_hits = m_outHits.createAndPut();
    
  //  loop input hits
  for ( const auto& hit : *in_hits ) {
    auto new_hit = hit.clone();

    // smearing energy
    auto old_e = hit.getEnergy();
    double eDep = old_e;
    double eRes = fResolutionAtERef * sqrt(fEnergyRef / eDep) / 2.35 / 100;
    double gain = m_sigmaGenE() * eRes + 1.0;    
    new_hit.setEnergy( old_e * gain );

    // add new hit to output collection
    out_hits->push_back( new_hit );
  }

  return StatusCode::SUCCESS;
}

StatusCode CaloHitSmearAlg::finalize() { return GaudiAlgorithm::finalize(); }