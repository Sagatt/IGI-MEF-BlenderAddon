import bpy
import numpy as np
import os
import sys

addon_dir = os.path.dirname(__file__)
sys.path.append(addon_dir)

import reader_ilff as reader_ilff
from struct_mef import *

class Rigid:
    def __init__(self, reader, objectname):
        self.reader = reader
        self.objectname = objectname
        self.hsem = None
        self.ecaf = None
        self.d3dr = None
        self.dner = None
        self.xtrv = None
        self.xtvc = None
        self.ecfc = None
        self.xtvm = None
        self.objects = []

    def load_bytes(self):
        """Reads the necessary bytes for the mesh sections."""
        self.hsem_bytes = self.reader.read(b'HSEM')
        self.d3dr_bytes = self.reader.read(b'D3DR')
        self.dner_bytes = self.reader.read(b'DNER')
        self.ecaf_bytes = self.reader.read(b'ECAF')
        self.xtrv_bytes = self.reader.read(b'XTRV')
        self.xtvc_bytes = self.reader.read(b'XTVC')
        self.ecfc_bytes = self.reader.read(b'ECFC')
        self.xtvm_bytes = self.reader.read(b'XTVM')

        if not all((self.hsem_bytes, self.d3dr_bytes, self.dner_bytes, self.ecaf_bytes, self.xtrv_bytes, self.xtvc_bytes, self.ecfc_bytes, self.xtvm_bytes)):
            raise ValueError("One or more required sections are missing from the file.")

    def parse_bytes(self):
        """Parses the bytes into NumPy arrays."""
        self.hsem = np.frombuffer(self.hsem_bytes, DTYPE_HSEM)
        self.ecaf = np.frombuffer(self.ecaf_bytes, DTYPE_ECAF)
        self.ecfc = np.frombuffer(self.ecfc_bytes, DTYPE_ECFC)
        self.xtvm = np.frombuffer(self.xtvm_bytes, DTYPE_XTVM)

        model_type = self.hsem['model_type'][0]
        if model_type == 0:
            self.d3dr = np.frombuffer(self.d3dr_bytes, DTYPE_D3DR_0)
            self.dner = np.frombuffer(self.dner_bytes, DTYPE_DNER_0)
            self.xtrv = np.frombuffer(self.xtrv_bytes, DTYPE_XTRV_0)
            self.xtvc = np.frombuffer(self.xtvc_bytes, DTYPE_XTVC_0)
        elif model_type == 1:
            self.d3dr = np.frombuffer(self.d3dr_bytes, DTYPE_D3DR_1)
            self.dner = np.frombuffer(self.dner_bytes, DTYPE_DNER_1)
            self.xtrv = np.frombuffer(self.xtrv_bytes, DTYPE_XTRV_1)
            self.xtvc = np.frombuffer(self.xtvc_bytes, DTYPE_XTVC_1)
        elif model_type == 3:
            self.d3dr = np.frombuffer(self.d3dr_bytes, DTYPE_D3DR_3)
            self.dner = np.frombuffer(self.dner_bytes, DTYPE_DNER_3)
            self.xtrv = np.frombuffer(self.xtrv_bytes, DTYPE_XTRV_3)
            self.xtvc = np.frombuffer(self.xtvc_bytes, DTYPE_XTVC_3)

    def create_render(self):
        """Creates Render objects from the parsed data."""
        vertex_positions = self.xtrv[['px', 'py', 'pz']].tolist()
        vertex_normals = self.xtrv[['nx', 'ny', 'nz']].tolist()
        triangle_indices = self.ecaf[['c', 'b', 'a']]
        faces_per_object = self.dner['num_face'].tolist()

        face_start = 0

        for object_index, num_faces in enumerate(faces_per_object):
            face_end = face_start + num_faces
            object_triangle_indices = triangle_indices[face_start:face_end].tolist()

            object_name = f"{self.objectname}_{object_index}"
            mesh = bpy.data.meshes.new(object_name)

            if not isinstance(object_triangle_indices[0], (list, tuple)):
                raise ValueError("Triangle indices are not in the correct format.")

            mesh.from_pydata(vertex_positions, [], object_triangle_indices)

            if len(vertex_normals) == len(mesh.vertices):
                mesh.normals_split_custom_set_from_vertices(vertex_normals)
            else:
                raise RuntimeError("Number of vertex normals does not match the number of vertices.")

            self.apply_uv_maps(mesh)

            mesh.update()
            mesh.validate()

            mesh_object = bpy.data.objects.new(object_name, mesh)
            bpy.context.collection.objects.link(mesh_object)     

            self.objects.append(mesh_object)

            face_start = face_end
            
            mesh_object.scale = (0.0005, 0.0005, 0.0005)
                    
    def create_collision(self):
        """Creates Collision mesh object from the parsed data."""
        vertex_positions = self.xtvc[['px', 'py', 'pz']].tolist()
        triangle_indices = self.ecfc[['c', 'b', 'a']].tolist()

        mesh = bpy.data.meshes.new("collision_mesh")

        mesh.from_pydata(vertex_positions, [], triangle_indices)

        mesh.update()
        mesh.validate()

        mesh_object = bpy.data.objects.new(f"{self.objectname}_collision", mesh)
        bpy.context.collection.objects.link(mesh_object)
        
        bpy.ops.object.select_all(action='DESELECT')
        
        mesh_object.select_set(True)
        bpy.context.view_layer.objects.active = mesh_object
        
        mesh_object.scale = (0.0005, 0.0005, 0.0005)
     
    def create_magic(self):
        """Creates Magic verts."""
        vertex_positions = self.xtvm[['px', 'py', 'pz']].tolist()

        mesh = bpy.data.meshes.new("magic_mesh")
        
        mesh.from_pydata(vertex_positions, [], [])
        
        mesh.update()
        mesh.validate()

        mesh_object = bpy.data.objects.new(f"{self.objectname}_magic", mesh)
        bpy.context.collection.objects.link(mesh_object)

        bpy.ops.object.select_all(action='DESELECT')

        mesh_object.select_set(True)
        bpy.context.view_layer.objects.active = mesh_object
        
        mesh_object.scale = (0.0005, 0.0005, 0.0005)  
            

    def apply_uv_maps(self, mesh):
        """Applies UV maps to the mesh."""
        primary_uv_coordinates = self.xtrv[['u', 'v']].tolist()
        secondary_uv_coordinates = []
        if 'u1' in self.xtrv.dtype.names and 'v1' in self.xtrv.dtype.names:
            secondary_uv_coordinates = self.xtrv[['u1', 'v1']].tolist()

        flipped_primary_uv_coordinates = [(1.0 - u, 1.0 - v) for u, v in primary_uv_coordinates]
        flipped_secondary_uv_coordinates = [(1.0 - u1, 1.0 - v1) for u1, v1 in secondary_uv_coordinates]

        if not mesh.uv_layers:
            mesh.uv_layers.new(name="PrimaryUVMap")

        primary_uv_layer = mesh.uv_layers.active.data
        for i, loop in enumerate(mesh.loops):
            primary_uv_layer[i].uv = flipped_primary_uv_coordinates[loop.vertex_index]

        if len(flipped_secondary_uv_coordinates) > 0:
            secondary_uv_layer = mesh.uv_layers.new(name="SecondaryUVMap")
            for i, loop in enumerate(mesh.loops):
                secondary_uv_layer.data[i].uv = flipped_secondary_uv_coordinates[loop.vertex_index]

    def load(self):
        """Main method to load and create the mesh."""
        self.load_bytes()
        self.parse_bytes()
        self.create_render()
        #self.create_collision()
        self.create_magic()
        self.create_spheres()           
        return self.objects

class Shadow:
    def __init__(self, reader, objectname):
        self.reader = reader
        self.objectname = objectname
        self.sems = None
        self.xtvs = None
        self.cafs = None
        self.egde = None
        self.objects = []

    def load_bytes(self):
        """Reads the necessary bytes for the mesh sections."""
        self.sems_bytes = self.reader.read(b'SEMS')
        self.xtvs_bytes = self.reader.read(b'XTVS')
        self.cafs_bytes = self.reader.read(b'CAFS')
        self.egde_bytes = self.reader.read(b'EGDE')

        if not all((self.sems_bytes, self.xtvs_bytes, self.cafs_bytes, self.egde_bytes)):
            raise ValueError("One or more required sections are missing from the file.")

    def parse_bytes(self):
        """Parses the bytes into NumPy arrays."""
        self.sems = np.frombuffer(self.sems_bytes, DTYPE_SEMS)
        self.xtvs = np.frombuffer(self.xtvs_bytes, DTYPE_XTVS)
        self.cafs = np.frombuffer(self.cafs_bytes, DTYPE_CAFS)
        self.egde = np.frombuffer(self.egde_bytes, DTYPE_EGDE)

    def create_shadow(self):
        """Creates Render objects from the parsed data."""
        positions = self.xtvs.tolist()
        triangles_indices = self.cafs[['a', 'b', 'c']].tolist()
        triangles_normals = self.cafs[['nz', 'ny', 'nx']].tolist()
        edges = self.egde.tolist()
        
        mesh = bpy.data.meshes.new('shadow_mesh')
        mesh.from_pydata(positions, edges, triangles_indices)

        mesh.update()
        mesh.validate()

        mesh_object = bpy.data.objects.new(self.objectname, mesh)
        bpy.context.collection.objects.link(mesh_object)
        
        bpy.ops.object.select_all(action='DESELECT')
            
        mesh_object.scale = (0.0005, 0.0005, 0.0005)
                    
    def load(self):
        """Main method to load and create the mesh."""
        self.load_bytes()
        self.parse_bytes()
        self.create_shadow()           
        return self.objects


def load_mef(*args, **kwargs):
    name = bpy.path.display_name_from_filepath(args[0])
    reader = reader_ilff.open_ilff(str(args[0]))
    
    if reader.find(b'HSEM'):
        rigidLoader = Rigid(reader, name)
        rigidLoader.load()
    elif reader.find(b'SEMS'):
        shadowLoader = Shadow(reader, name)
        shadowLoader.load()

def load(*args, **kwargs):
    load_mef(*args, **kwargs)
    return {'FINISHED'}