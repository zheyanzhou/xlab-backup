#pragma once

// GAUDI
#include "GaudiAlg/GaudiAlgorithm.h"
#include "GaudiKernel/RndmGenerators.h"

// k4FWCore
#include "k4FWCore/DataHandle.h"

//
#include "SimKernel/Units.h"
#include <cmath>
#include <edm4hep/SimCalorimeterHit.h>

/** @class CaloHitSmearAlg
 *  
 *  The energy resolution will follow a root square law with the energy
 *  using the `energyReference` and the `resolutionReference` as a pivoting
 *  point.
 *
 *
 *  Energy smearing with Gaussian:
 *  - two options for energy
 *    1. fixed sigma (param: m_eSigma)
 *    2. fix the fano factor and variant energy sigma based on edep (param: m_fano)
 *
 *  Input: SimCalorimeterHit from Geant4 output
 *
 *  Output: Clone of the input except smeared energy
 *
 *  @author Yong Zhou
 */

namespace edm4hep {
  class SimCalorimeterHitCollection;
} // namespace edm4hep

class CaloHitSmearAlg : public GaudiAlgorithm {
public:
  explicit CaloHitSmearAlg( const std::string&, ISvcLocator* );
  virtual ~CaloHitSmearAlg();
  /**  Initialize.
   *   @return status code
   */
  virtual StatusCode initialize() final;
  /**  Fills the histograms.
   *   @return status code
   */
  virtual StatusCode execute() final;
  /**  Finalize.
   *   @return status code
   */
  virtual StatusCode finalize() final;

private:
  /// Random number generators
  Rndm::Numbers m_sigmaGenE;

  /// Handle to EDM collection
  DataHandle<edm4hep::SimCalorimeterHitCollection> m_inHits{ "CztHits", Gaudi::DataHandle::Reader, this };
  DataHandle<edm4hep::SimCalorimeterHitCollection> m_outHits{ "CztSmearedHits", Gaudi::DataHandle::Writer, this };

  /// Properties
  Gaudi::Property<double> fEnergyRef{ this, "energy_reference", 250,
                                    "[keV] Energy value for reference" };
  Gaudi::Property<double> fResolutionAtERef{ this, "resolution_reference", 15,
                                    "Relative energy resolution at Energy of reference" };

};