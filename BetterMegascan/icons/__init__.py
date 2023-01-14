import bpy.utils.previews
import os

from .. import spawn_logger

log = spawn_logger(__name__)


icons = {}


def register():
    global icons

    icons = bpy.utils.previews.new()

    icons_dir = os.path.dirname(__file__)

    for filepath in [p for p in os.listdir(icons_dir) if os.path.isfile(os.path.join(icons_dir, p)) and os.path.splitext(p)[1] == '.png']:
        log.debug(f"load icon '{os.path.splitext(filepath)[0]}' ({filepath})")
        icons.load(os.path.splitext(filepath)[0], os.path.join(icons_dir, filepath), 'IMAGE')

    log.debug("icons loaded")


def unregister():
    global icons

    bpy.utils.previews.remove(icons)

    log.debug("icons unloaded")
