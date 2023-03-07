from .. import spawn_logger

log = spawn_logger(__name__)

from .import_3dasset import BETTERMS_OT_import_3dasset
from .import_surface import BETTERMS_OT_import_surface
from .import_brush import BETTERMS_OT_import_brush
from .init_menu import BETTERMS_OT_init_import_menu

from .bake_library import BETTERMS_OT_bake_library, BETTERMS_OT_bake_library_helper

classes = [
    BETTERMS_OT_import_3dasset,
    BETTERMS_OT_import_surface,
    BETTERMS_OT_import_brush,
    BETTERMS_OT_init_import_menu,

    BETTERMS_OT_bake_library,
    BETTERMS_OT_bake_library_helper,
]