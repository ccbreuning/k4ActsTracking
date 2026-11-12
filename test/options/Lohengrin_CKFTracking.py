#!/usr/bin/env python3
#
# Copyright (c) 2014-2024 Key4hep-Project.
#
# This file is part of Key4hep.
# See https://key4hep.github.io/key4hep-doc/ for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys

from Gaudi.Configuration import INFO, DEBUG
from Gaudi.Configurables import DDPlanarDigi, CKFTrackingAlg
from k4FWCore import ApplicationMgr, IOSvc

sys.path.insert(0, os.path.dirname(__file__))

from _ckf_helpers import (
    make_telescope_ckf_tracking,
    make_services,
    make_hit_mergers,
)
# Use the real DD4hep field so ACTS accounts for the localized Lohengrin magnet
svcList = make_services(use_dd4hep_field=True)
iosvc = IOSvc("IOSvc")

algList = []

# Lohengrin has a tag and a recoil tracker. This is the recoil tracking and digitization
algList.append(
    DDPlanarDigi(
        "TrackerDigitizer",
        SubDetectorName="RecoilTracker",
        IsStrip=False,
        ResolutionT=[20],
        ResolutionU=[0.055], # pitch / sqrt(12)
        ResolutionV=[0.055], # pitch / sqrt(12)
        # The readout of the sensors sits in the last 32 bits (x:32:-16,y:-16)
        CellIDBits=32,
        SimTrackHitCollectionName=["RecoilTrackerHits"],
        SimTrkHitRelCollection=["RecoilTrackerHitsRelations"],
        TrackerHitCollectionName=["RecoilTrackerHitsDigi"],
    )
)

hit_merger, hit_rel_merger = make_hit_mergers(
    hit_collections=["RecoilTrackerHitsDigi"],
    relation_collections=["RecoilTrackerHitsRelations"],
)
algList.extend([hit_merger, hit_rel_merger])

# Adding the CKF Tracker

OUT = INFO
N = -1

ckf_tracking = CKFTrackingAlg(
        "CKFTracking",
        RunCKF=True,
        CKF_Chi2CutOff=25,
        CKF_NumMeasurementsCutOff=1,
        SeedingSensorsCellIDs=["layer:1|2|3"],
        OutputTrackCollection="CKFTracks",
        OutputSeedCollection="CKFTrackSeeds",
        InputTrackerHitCollection=hit_merger.OutputCollection,
        InputTrackerHitRelationCollection=hit_rel_merger.OutputCollection,
        OutputLevel=OUT,
        SeedingMode="Telescope",
        Telescope_LayerZTolerance=1.0,
        Telescope_CollinearityCut=2.0,
        Telescope_NominalMomentum=3.2,
        Telescope_ReferenceZ=1900,
        InitialTrackError_Pos=0.1,
        # InitialTrackError_Phi=0.1,
        # InitialTrackError_Lambda=0.1,
        InitialTrackError_RelP=0.1
    )

algList.append(ckf_tracking)

ApplicationMgr(TopAlg=algList, ExtSvc=svcList, OutputLevel=OUT, EvtSel="NONE", EvtMax=N)
