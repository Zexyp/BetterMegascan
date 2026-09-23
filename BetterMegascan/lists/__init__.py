import bpy

class BETTERMS_UL_bake_library_assets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)
        row = layout.row()
        row.enabled = False
        row.label(text=item.type)
        row.label(text=item.id)
        layout.prop(item, "selected", text='')

classes = [
    BETTERMS_UL_bake_library_assets,
]