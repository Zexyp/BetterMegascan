bl_info = {
    "name": "BetterMegascan",
    "author": "Zexyp",
    "description": "Better import of Megascans",
    "blender": (2, 80, 0),
    "version": (0, 2, 0),
    "location": "File > Import",
    "warning": "",
    "category": "Import-Export",
    "tracker_url": "https://github.com/Zexyp/BetterMegascan/issues",
}

"""
Megascan? more like Mega Scan because it's such a pain to work with
"""

import bpy

import logging
import os

def spawn_logger(name) -> logging.Logger:
    logger = logging.Logger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s]: %(message)s", "%H:%M:%S"))
    logger.addHandler(handler)
    return logger

log = spawn_logger(__name__)

from . import operators
from . import panels
from . import menus

from . import icons
from . import parser
from .preferences import BETTERMS_AddonPreferences


parser.tmp_dir = os.path.join(bpy.app.tempdir, 'BetterMegascan')


def menu_func_import(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(operators.BETTERMS_OT_init_import_menu.bl_idname, icon_value=icons.icons["megascans"].icon_id)
    layout.operator(operators.BETTERMS_OT_bake_library.bl_idname, icon='ASSET_MANAGER')
    layout.separator()


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

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    log.debug("gm")


def unregister():
    icons.unregister()

    unregister_classes()

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    log.debug("gn")
