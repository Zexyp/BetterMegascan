from .. import spawn_logger

log = spawn_logger(__name__)

from .import_model import BETTERMS_OT_import_model
from .import_surface import BETTERMS_OT_import_surface
from .import_brush import BETTERMS_OT_import_brush
from .init_menu import BETTERMS_OT_init_import_menu

from .bake_library import BETTERMS_OT_bake_library

classes = [
    BETTERMS_OT_import_model,
    BETTERMS_OT_import_surface,
    BETTERMS_OT_import_brush,
    BETTERMS_OT_init_import_menu,

    BETTERMS_OT_bake_library,
]