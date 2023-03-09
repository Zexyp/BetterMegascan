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

def group(layout, operator):
    col = layout.column(heading="Group", align=True)
    col.prop(operator, "group_by_model", text="Asset")
    col.prop(operator, "group_by_lod", text="LODs")


def lods(layout, operator):
    layout.prop(operator, "apply_transform")

    col = layout.column(heading="LODs", align=True)
    col.prop(operator, "use_lods", index=0, text=str(lod_options[0]))
    row = layout.row()
    for i in range(1, 5):
        row.prop(operator, "use_lods", index=i, text=str(lod_options[i]))
    row = layout.row()
    for i in range(5, 9):
        row.prop(operator, "use_lods", index=i, text=str(lod_options[i]))


def maps(layout, operator):
    col = layout.column(heading="Maps", align=True)
    for i, omap in enumerate(map_options):
        col.prop(operator, "use_maps", index=i, text=omap)


def filetype_lods(layout, operator):
    layout.prop(operator, "use_filetype_lods")


def filetype_maps(layout, operator):
    layout.prop(operator, "use_filetype_maps")
