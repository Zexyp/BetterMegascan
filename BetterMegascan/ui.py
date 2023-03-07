lod_options = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
]

map_options = [
    "albedo",
    "cavity",
    "curvature",
    "gloss",
    "normal",
    "displacement",
    "bump",
    "ao",
    "metalness",
    "diffuse",
    "roughness",
    "specular",
    "fuzz",
    "translucency",
    "thickness",
    "opacity",
    "brush",
    "mask",
    "transmission",
]

def collections(layout, operator):
    layout.prop(operator, "group_by_model")
    layout.prop(operator, "group_by_lod")

def lods(layout, operator):
    col = layout.column(heading="LODs", align=True)
    col.prop(operator, "use_lods", index=0, text=str(lod_options[0]))
    row = layout.row()
    for i in range(1, 5):
        row.prop(operator, "use_lods", index=i, text=str(lod_options[i]))
    row = layout.row()
    for i in range(5, 9):
        row.prop(operator, "use_lods", index=i, text=str(lod_options[i]))

    layout.prop(operator, "apply_transform")

def maps(layout, operator):
    col = layout.column(heading="Maps", align=True)
    for i, omap in enumerate(map_options):
        col.prop(operator, "use_maps", index=i, text=omap)

def filetype_lods(layout, operator):
    pass

def filetype_maps(layout, operator):
    pass
