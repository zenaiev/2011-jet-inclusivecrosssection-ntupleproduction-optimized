
# Forked from SMPJ Analysis Framework
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/SMPJAnalysisFW
# https://github.com/cms-smpj/SMPJ/tree/v1.0
# (further optimized to improve performance)


## Skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *
import FWCore.Utilities.FileUtils as FileUtils

process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

# True : when running in OpenData virtual machine
# False: when runing in lxplus 
runOnVM = True

# Local input
fileList = FileUtils.loadListFromFile('CMS_MonteCarlo2011_Summer11LegDR_QCD_Pt-80to120_TuneZ2_7TeV_pythia6_AODSIM_PU_S13_START53_LV6-v1_00000_file_index.txt')
process.source.fileNames = cms.untracked.vstring(*fileList)

if runOnVM:
    process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/START53_LV6A1.db')

# Global tag for Summer11LegDR-PU_S13_START53_LV6-v1
process.GlobalTag.globaltag = cms.string('START53_LV6A1::All')

# Select good vertices
process.goodOfflinePrimaryVertices = cms.EDFilter(
    "VertexSelector",
    filter = cms.bool(False),
    src = cms.InputTag("offlinePrimaryVertices"),
    cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.rho < 2")
    )

# -------- The Tracking failure filter ------#
from RecoMET.METFilters.trackingFailureFilter_cfi import trackingFailureFilter
process.trackingFailureFilter = trackingFailureFilter.clone()
process.trackingFailureFilter.VertexSource = cms.InputTag('goodOfflinePrimaryVertices')

# Load jet correction services for all jet algoritms
process.load("JetMETCorrections.Configuration.JetCorrectionServicesAllAlgos_cff")

################### EDAnalyzer ##############################3
process.ak5ak7 = cms.EDAnalyzer('OpenDataTreeProducerOptimized',
    ## jet collections ###########################
    pfak7jets       = cms.InputTag('ak7PFJets'),
    pfak5jets       = cms.InputTag('ak5PFJets'),
    ## MET collection ####
    pfmet           = cms.InputTag('pfMET7'),
    ## database entry for the uncertainties ######
    PFPayloadName   = cms.string('AK7PF'),

    ## set the conditions for good Vtx counting ##
    offlineVertices = cms.InputTag('goodOfflinePrimaryVertices'),
    goodVtxNdof     = cms.double(4), 
    goodVtxZ        = cms.double(24),
    ## rho #######################################
    srcPFRho        = cms.InputTag('kt6PFJets','rho'),
    ## preselection cuts #########################
    maxY            = cms.double(5.0), 
    minPFPt         = cms.double(30),
    minNPFJets      = cms.int32(1),
    minGenPt        = cms.untracked.double(30),
    minJJMass       = cms.double(-1),
    isMCarlo        = cms.untracked.bool(True),
    genjets         = cms.untracked.InputTag('ak7GenJets'),
    useGenInfo      = cms.untracked.bool(True),
    ## trigger ###################################
    printTriggerMenu = cms.untracked.bool(True),
    processName     = cms.string('HLT'),
    triggerNames    = cms.vstring(
                                'HLT_Jet30', 'HLT_Jet60', 'HLT_Jet80', 'HLT_Jet110', 
                                'HLT_Jet150','HLT_Jet190','HLT_Jet240','HLT_Jet370',
                                ),
    triggerResults  = cms.InputTag("TriggerResults","","HLT"),
    triggerEvent    = cms.InputTag("hltTriggerSummaryAOD","","HLT"),
    ## jet energy correction labels ##############
    jetCorr_ak5      = cms.string('ak5PFL1FastL2L3Residual'),
    jetCorr_ak7      = cms.string('ak7PFL1FastL2L3Residual'),
)

############# hlt filter #########################
process.hltFilter = cms.EDFilter('HLTHighLevel',
    TriggerResultsTag  = cms.InputTag('TriggerResults','','HLT'),
    HLTPaths           = cms.vstring('HLT_Jet*', 'HLT_DiJetAve*'),
    eventSetupPathsKey = cms.string(''),
    andOr              = cms.bool(True), #----- True = OR, False = AND between the HLTPaths
    throw              = cms.bool(False)
)


# Let it run
process.p = cms.Path(
    process.goodOfflinePrimaryVertices*
    process.hltFilter *
    process.trackingFailureFilter *
    process.ak5ak7
)


# Processing time on VM (2011 laptop)
# DATA: 50000 events / 4 hours
# MC:   50000 events / 5 hours

# Change number of events here:
process.maxEvents.input = 50000

process.MessageLogger.cerr.FwkReport.reportEvery = 500

# Output file
process.TFileService = cms.Service("TFileService", fileName = cms.string('OpenDataTree_mc.root'))

# To suppress long output at the end of the job
#process.options.wantSummary = False   

del process.outpath
