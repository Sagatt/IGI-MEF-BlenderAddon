import bpy
import numpy as np
import os
import sys

# Add the current directory to sys.path
addon_dir = os.path.dirname(__file__)
sys.path.append(addon_dir)

import reader_ilff as reader_ilff
from struct_mef import *

def find_textures_for_model(model_name):
    # Get the path to the Blender's addon directory
    blender_version = "4.2"
    appdata_path = os.getenv('APPDATA')
    addon_directory = os.path.join(appdata_path, "Blender Foundation", "Blender", blender_version, "scripts", "addons", "io_mesh_igi2")
    file_path = os.path.join(addon_directory, "common.dat")

    # Initialize variables
    textures = []

    # Open the file and read its content
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                line = line.strip()  # Remove leading/trailing whitespace
                if line == model_name:  # Check for the model name
                    # Read the amount of textures
                    amount_of_textures = int(lines[i + 1].strip())
                    # Read texture names
                    for j in range(amount_of_textures):
                        texture_name = lines[i + 2 + j].strip()
                        textures.append(texture_name)
                    break  # Exit the loop once the model is found
    except FileNotFoundError:
        print(f"Error: common.dat was not found in '{addon_directory}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return textures

def assign_textures_to_objects(object_list, textures):
    blender_version = "4.2"
    appdata_path = os.getenv('APPDATA')
    addon_directory = os.path.join(appdata_path, "Blender Foundation", "Blender", blender_version, "scripts", "addons", "io_mesh_igi2")
    textures_directory = os.path.join(addon_directory, "textures")
    
    # Supported texture formats
    supported_extensions = ['.tga', '.png', '.jpg', '.jpeg']
    
    # Loop over objects and textures and assign accordingly
    for obj_index, obj in enumerate(object_list):
        if obj_index < len(textures):
            texture_name = textures[obj_index]
            texture_path = None

            # Check if texture exists with any supported extension
            for ext in supported_extensions:
                potential_texture_path = os.path.join(textures_directory, texture_name + ext)
                if os.path.exists(potential_texture_path):
                    texture_path = potential_texture_path
                    break
            
            if texture_path:
                # Create a new material
                material = bpy.data.materials.new(name=texture_name)
                material.use_nodes = True

                # Assign the texture to the material's shader node
                bsdf = material.node_tree.nodes.get("Principled BSDF")
                tex_image = material.node_tree.nodes.new('ShaderNodeTexImage')
                tex_image.image = bpy.data.images.load(texture_path)  # Load the texture

                # Link texture to the shader
                material.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])

                # Assign material to the object
                obj.data.materials.append(material)
            else:
                print(f"Image {texture_name} not found in {textures_directory}.")
        else:
            print(f"No texture available for object {obj.name}.")

def load_render_mesh(reader, objectname):
    hsem_bytes = reader.read(b'HSEM')
    d3dr_bytes = reader.read(b'D3DR')
    dner_bytes = reader.read(b'DNER')
    ecaf_bytes = reader.read(b'ECAF')
    xtrv_bytes = reader.read(b'XTRV')

    # Ensure all required sections are present
    if not all((hsem_bytes, d3dr_bytes, dner_bytes, ecaf_bytes, xtrv_bytes)):
        raise ValueError("One or more required sections are missing from the file.")

    hsem = np.frombuffer(hsem_bytes, DTYPE_HSEM)
    ecaf = np.frombuffer(ecaf_bytes, DTYPE_ECAF)

    if hsem['model_type'] == 0:
        d3dr = np.frombuffer(d3dr_bytes, DTYPE_D3DR_0)
        dner = np.frombuffer(dner_bytes, DTYPE_DNER_0)
        xtrv = np.frombuffer(xtrv_bytes, DTYPE_XTRV_0)

    elif hsem['model_type'] == 1:
        d3dr = np.frombuffer(d3dr_bytes, DTYPE_D3DR_1)
        dner = np.frombuffer(dner_bytes, DTYPE_DNER_1)
        xtrv = np.frombuffer(xtrv_bytes, DTYPE_XTRV_1)

    elif hsem['model_type'] == 3:
        d3dr = np.frombuffer(d3dr_bytes, DTYPE_D3DR_3)
        dner = np.frombuffer(dner_bytes, DTYPE_DNER_3)
        xtrv = np.frombuffer(xtrv_bytes, DTYPE_XTRV_3)

    vertex_positions = xtrv[['px', 'py', 'pz']].tolist()  # Ensure this is a list of tuples/lists
    vertex_normals = xtrv[['nx', 'ny', 'nz']].tolist()    # Ensure this is a list of tuples/lists
    triangle_indices = ecaf[['c', 'b', 'a']]

    faces_per_object = list()

    # Store the number of faces per object from the dner data
    for i in dner['num_face']:
        faces_per_object.append(i)
    
    # Loop over the face ranges to create separate objects
    face_start = 0
    objects = []
    
    for obj_index, num_faces in enumerate(faces_per_object):
        face_end = face_start + num_faces

        # Create the mesh for this object
        object_name = f"{objectname}_{obj_index}"
        mesh = bpy.data.meshes.new(object_name)

        # Use only the face range for this object
        object_triangle_indices = triangle_indices[face_start:face_end].tolist()  # Convert to list of tuples

        # Ensure that object_triangle_indices is a list of tuples
        if not isinstance(object_triangle_indices[0], (list, tuple)):
            raise ValueError("Triangle indices are not in the correct format.")
        
        # Create the mesh data for this object
        mesh.from_pydata(vertex_positions, [], object_triangle_indices)

        # Apply the custom vertex normals
        if len(vertex_normals) == len(mesh.vertices):
            mesh.normals_split_custom_set_from_vertices(vertex_normals)
        else:
            raise RuntimeError("Number of vertex normals does not match the number of vertices.")

        # Extract UV coordinates (primary: u, v) and (secondary: u1, v1)
        primary_uv_coordinates = xtrv[['u', 'v']].tolist()
        secondary_uv_coordinates = []
        if 'u1' in xtrv.dtype.names and 'v1' in xtrv.dtype.names:
            secondary_uv_coordinates = xtrv[['u1', 'v1']].tolist()
        else:
            print("Warning: UV coordinates 'u1' and 'v1' not found in XTRV.")

        # Flip UV coordinates on both X and Y axes
        flipped_primary_uv_coordinates = [(1.0 - u, 1.0 - v) for u, v in primary_uv_coordinates]
        flipped_secondary_uv_coordinates = [(1.0 - u1, 1.0 - v1) for u1, v1 in secondary_uv_coordinates]

        # Create the primary UV map for the mesh
        if not mesh.uv_layers:
            mesh.uv_layers.new(name="PrimaryUVMap")

        primary_uv_layer = mesh.uv_layers.active.data
        for i, loop in enumerate(mesh.loops):
            primary_uv_layer[i].uv = flipped_primary_uv_coordinates[loop.vertex_index]

        # Optionally, create the secondary UV map
        if len(flipped_secondary_uv_coordinates) > 0:
            secondary_uv_layer = mesh.uv_layers.new(name="SecondaryUVMap")
            for i, loop in enumerate(mesh.loops):
                secondary_uv_layer.data[i].uv = flipped_secondary_uv_coordinates[loop.vertex_index]

        # Update and validate the mesh
        mesh.update()
        mesh.validate()

        # Create the object and link it to the scene collection
        render_mesh_object = bpy.data.objects.new(object_name, mesh)
        bpy.context.collection.objects.link(render_mesh_object)
        
        # Append the object to the list
        objects.append(render_mesh_object)

        # Move the face_start index to the next face range
        face_start = face_end

    return objects  # Return a list of objects to link in load_mef


def load_shadow_mesh(reader, objectname):
    sems_bytes = reader.read(b'SEMS')
    xtvs_bytes = reader.read(b'XTVS')
    cafs_bytes = reader.read(b'CAFS')
    egde_bytes = reader.read(b'EGDE')

    sems = np.frombuffer(sems_bytes, DTYPE_SEMS)
    xtvs = np.frombuffer(xtvs_bytes, DTYPE_XTVS)
    cafs = np.frombuffer(cafs_bytes, DTYPE_CAFS)
    egde = np.frombuffer(egde_bytes, DTYPE_EGDE)
    
    # Ensure all required sections are present
    if not all((sems_bytes, xtvs_bytes, cafs_bytes, egde_bytes)):
        raise ValueError("One or more required sections are missing from the file.")
    
    positions = xtvs.tolist()
    triangles_indices = cafs[['a', 'b', 'c']].tolist()
    triangles_normals = cafs[['nz', 'ny', 'nx']].tolist()
    edges = egde.tolist()

    # Create the mesh
    mesh = bpy.data.meshes.new('shadow_mesh')
    mesh.from_pydata(positions, edges, triangles_indices)

    # Update and validate the mesh
    mesh.update()
    mesh.validate()

    # Create the object and link it to the scene collection
    shadow_mesh_object = bpy.data.objects.new(objectname, mesh)
    bpy.context.collection.objects.link(shadow_mesh_object)

    return shadow_mesh_object

def join_objects_and_rename(objects, base_name):
    # Select all objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)

    # Set the first object as the active one
    bpy.context.view_layer.objects.active = objects[0]

    # Join all the selected objects into one
    bpy.ops.object.join()

    # Rename the joined object by removing the _indexnumber
    joined_object = bpy.context.view_layer.objects.active
    joined_object.name = base_name

    return joined_object

def load_mef(*args, **kwargs):
    filepath = args[0] # Define filepath of the opened file
    name = bpy.path.display_name_from_filepath(filepath) # e.g 100_01_1.mef
    reader = reader_ilff.open_ilff(str(filepath)) # Get the ILFF reader ready
    
    if reader.find(b'HSEM'):
        # Find textures for the model
        textures = find_textures_for_model(name)

        # Load mesh objects based on face ranges
        objects = load_render_mesh(reader, name)

        # Assign textures to the objects
        assign_textures_to_objects(objects, textures)

        # Join objects into one and rename
        object = join_objects_and_rename(objects, name)

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

    elif reader.find(b'SEMS'):
        object = load_shadow_mesh(reader, name)

    #Select and activate the object
    object.select_set(True)
    bpy.context.view_layer.objects.active = object
    
    # Set the scale
    object.scale = (0.0005, 0.0005, 0.0005)

def load(*args, **kwargs):
    load_mef(*args, **kwargs)
    return {'FINISHED'}