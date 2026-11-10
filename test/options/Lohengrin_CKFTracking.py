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
from Gaudi.Configurables import DDPlanarDigi
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
        ResolutionT=[0.03],
        ResolutionU=[0.007],
        ResolutionV=[0.007],
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
ckf_tracking = make_telescope_ckf_tracking(
    hit_merger,
    hit_rel_merger,
    # Use all 6 layers of the recoil tracker for seeding for now
    seeding_cellids=["layer:1|2|3|4|5|6"],
    nominal_momentum=3.2,
    reference_z=1900,
    layer_z_tolerance=1.0,
)
algList.append(ckf_tracking)

ApplicationMgr(TopAlg=algList, ExtSvc=svcList, OutputLevel=DEBUG, EvtSel="NONE", EvtMax=10)
