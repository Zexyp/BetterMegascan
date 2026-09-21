import bpy
from bpy.props import BoolProperty, StringProperty

class BETTERMS_PG_bake_library_asset(bpy.types.PropertyGroup):
    selected: BoolProperty()
    id: StringProperty()
    name: StringProperty()
    type: StringProperty()

classes = [
    BETTERMS_PG_bake_library_asset,
]