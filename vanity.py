"""Parametric vanity & bathroom furniture module (Wall C).

Currently disabled (`config.ENABLE_VANITY = False`) while verifying the bare 3D room shell.
"""

import cadquery as cq

import config as cfg


def build_vanity() -> cq.Assembly | None:
    """Return the vanity assembly when enabled, or None when viewing the bare room."""
    if not cfg.ENABLE_VANITY:
        return None

    vanity = cq.Assembly(name="vanity")
    return vanity
