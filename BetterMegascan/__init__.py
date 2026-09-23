"""
Megascan? more like Mega Scam because it's such a pain to work with
"""

# TODO: geometry nodes lod setup + proxy thingy

_needs_reload = "bpy" in locals()

import bpy

import logging
import os

import logging

class BetterMegascanHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        marker = "better_megascan"
        if marker in record.name:
            record.name = record.name[record.name.index(marker):]
        record.msg = f"\033[36m{record.msg}\033[0m" # fuck nt users
        super().emit(record)


log = logging.getLogger(__name__)
log_handler = BetterMegascanHandler()
log_handler.setFormatter(logging.Formatter(
                fmt="[%(levelname)s][%(asctime)s][%(name)s]: %(message)s",
                datefmt="%Y.%m.%d-%H:%M:%S"
            ))
log.handlers.clear()
log.addHandler(log_handler)
log.setLevel(logging.DEBUG)

from . import operators
from . import panels
from . import menus
from . import groups
from . import lists

from . import icons
from . import parser
from . import preferences
from . import ui
from . import loader

if _needs_reload:
    log.debug(f"reloading")

    import importlib
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(menus)
    importlib.reload(groups)
    importlib.reload(lists)

    importlib.reload(icons)
    importlib.reload(parser)
    importlib.reload(preferences)
    importlib.reload(ui)
    importlib.reload(loader)

parser.tmp_dir = os.path.join(bpy.app.tempdir, 'BetterMegascan')


classes = [
    *groups.classes,
    *lists.classes,
    *menus.classes,
    *operators.classes,
    *panels.classes,

    preferences.BETTERMS_AddonPreferences,
]

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    log.debug("good morning ^.^")

    icons.register()

    register_classes()

    ui.register()

    log.debug("ready")


def unregister():
    log.debug("feeling eepy")

    icons.unregister()

    unregister_classes()

    ui.unregister()

    log.debug("good night >.<")
