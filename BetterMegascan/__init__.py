bl_info = {
    "name": "BetterMegascan",
    "author": "Zexyp",
    "description": "Better import of Megascans",
    "blender": (3, 6, 0),
    "version": (0, 3, 0),
    "location": "File > Import",
    "warning": "",
    "category": "Import-Export",
    "tracker_url": "https://github.com/Zexyp/BetterMegascan/issues",
}

"""
Megascan? more like Mega Scam because it's such a pain to work with
"""
# TODO: geometry nodes lod setup + proxy thingy

import bpy

import logging
import os

log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s]: %(message)s", "%H:%M:%S"))
def spawn_logger(name) -> logging.Logger:
    logger = logging.Logger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)
    return logger

log = spawn_logger(__name__)

from . import operators
from . import panels
from . import menus

from . import icons
from . import parser
from .preferences import BETTERMS_AddonPreferences
from . import ui

parser.tmp_dir = os.path.join(bpy.app.tempdir, 'BetterMegascan')


classes = [
    *menus.classes,
    *operators.classes,
    *panels.classes,

    BETTERMS_AddonPreferences,
]

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    icons.register()

    register_classes()

    ui.register()

    log.debug("gm")


def unregister():
    icons.unregister()

    unregister_classes()

    ui.unregister()

    log.debug("gn")
