import bpy.utils.previews
import os
import logging


log = logging.Logger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s]: %(message)s", "%H:%M:%S"))
log.addHandler(handler)


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
