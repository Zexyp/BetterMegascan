bl_info = {
    "name": "BetterMegascan",
    "author": "Zexyp",
    "description": "Better import of Megascans",
    "blender": (2, 80, 0),
    "version": (0, 1, 0),
    "location": "",
    "warning": "",
    "category": "Import-Export"
}

import bpy

import logging
import os

log = logging.Logger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s]: %(message)s", "%H:%M:%S"))
log.addHandler(handler)

from .operators import *
from .panels import *
from .menus import *
from . import icons
from . import parser
from .preferences import BETTERMS_AddonPreferences


parser.tmp_dir = os.path.join(bpy.app.tempdir, 'BetterMegascan')


def menu_func_import(self, context):
    self.layout.operator(BETTERMS_OT_init_import_menu.bl_idname, icon_value=icons.icons["megascans"].icon_id)


classes = (
    BETTERMS_MT_import,

    BETTERMS_OT_init_import_menu,
    BETTERMS_OT_import_3dasset,
    BETTERMS_OT_import_surface,

    BETTERMS_PT_import_collections,
    BETTERMS_PT_import_filetypes,
    BETTERMS_PT_import_lods,
    BETTERMS_PT_import_textures,

    BETTERMS_AddonPreferences,
)

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
