import logging

log = logging.Logger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s]: %(message)s", "%H:%M:%S"))
log.addHandler(handler)

from .import_3dasset import BETTERMS_OT_import_3dasset
from .import_surface import BETTERMS_OT_import_surface
from .init_menu import BETTERMS_OT_init_import_menu
