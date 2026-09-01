# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition
from .fleetwave import FLEETWAVE_LAB
from .goldenace import GOLDENACE_LAB
from .humanbank import HUMANBANK_LAB
from .limelight import LIMELIGHT_LAB
from .mediacrate import MEDIACRATE_LAB
from .medihuman import MEDIHUMAN_LAB
from .netpulse import NETPULSE_LAB
from .rewindrange import REWINDRANGE_LAB
from .smartgridops import SMARTGRIDOPS_LAB
from .subverse import SUBVERSE_LAB
from .tradefloor import TRADEFLOOR_LAB
from .vaultsync import VAULTSYNC_LAB
from .waveform import WAVEFORM_LAB

WORLD_LABS: list[LabDefinition] = [  # type: ignore[assignment]
    REWINDRANGE_LAB,
    TRADEFLOOR_LAB,
    GOLDENACE_LAB,
    HUMANBANK_LAB,
    MEDIHUMAN_LAB,
    NETPULSE_LAB,
    LIMELIGHT_LAB,
    SUBVERSE_LAB,
    SMARTGRIDOPS_LAB,
    VAULTSYNC_LAB,
    MEDIACRATE_LAB,
    FLEETWAVE_LAB,
    WAVEFORM_LAB,
]
