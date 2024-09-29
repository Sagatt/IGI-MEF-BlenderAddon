bl_info = {
    "name": "IGI2 model format",
    "author": "Rotari Artiom",
    "version": (0, 1, 1),
    "blender": (4, 2, 1),
    "location": "File > Import > Mef Model (.mef) ",
    "description": "Import IGI2 Mef models",
    "category": "Import-Export",
}

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

from io_mesh_igi2 import import_mef

# Reload support for development
if "bpy" in locals():
    import importlib
    if "import_mef" in locals():
        importlib.reload(import_mef)


class Mef(object):
    pass


class MefImporter(bpy.types.Operator, ImportHelper):
    """Load Raw triangle mesh data"""
    bl_idname = "import_mef_model.mef"
    bl_label = "Import Mef"
    bl_options = {'UNDO'}

    # Define the filepath property correctly
    filepath: StringProperty(
        name="File Path",
        description="Filepath used for importing the MEF file",
        subtype='FILE_PATH'
    ) # type: ignore

    filter_glob: StringProperty(
        default="*.mef",
        options={'HIDDEN'},
        maxlen=255
    ) # type: ignore

    def execute(self, context):
        from . import import_mef

        # Ensure the filepath is a string and passed correctly
        import_mef.load(self.filepath)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_import(self, context):
    self.layout.operator(MefImporter.bl_idname, text="Mef Model (.mef)")


def register():
    bpy.utils.register_class(MefImporter)
    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():
    bpy.utils.unregister_class(MefImporter)
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()
