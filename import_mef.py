import bpy
import numpy as np
import os
import io_mesh_igi2.reader_ilff as reader_ilff
from io_mesh_igi2.struct_mef import *

def parse_mesh_data(reader):
    # Read the binary chunks from the reader
    hsem_bytes = reader.read(b'HSEM')
    d3dr_bytes = reader.read(b'D3DR')
    dner_bytes = reader.read(b'DNER')
    ecaf_bytes = reader.read(b'ECAF')
    xtrv_bytes = reader.read(b'XTRV')

    # Ensure all required sections are present
    if not all((hsem_bytes, d3dr_bytes, dner_bytes, ecaf_bytes, xtrv_bytes)):
        raise ValueError("One or more required sections are missing from the file.")

    # Parse each section with its corresponding function
    hsem = parse_hsem(hsem_bytes)
    model_type = hsem['model_type'][0]  # Assume model_type is the same across all HSEM entries
    d3dr = parse_d3dr(d3dr_bytes, model_type)
    dner = parse_dner(dner_bytes, model_type)
    xtrv = parse_xtrv(xtrv_bytes, model_type)
    ecaf = parse_ecaf(ecaf_bytes)

    return hsem, d3dr, dner, xtrv, ecaf

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
    file_path = os.path.join(addon_directory, "textures")
    
    # Loop over objects and textures and assign accordingly
    for obj_index, obj in enumerate(object_list):
        if obj_index < len(textures):
            texture_name = textures[obj_index]
            if texture_name in file_path:
                # Create a new material
                material = bpy.data.materials.new(name=texture_name)
                material.use_nodes = True
                
                # Assign the texture to the material's shader node
                bsdf = material.node_tree.nodes.get("Principled BSDF")
                tex_image = material.node_tree.nodes.new('ShaderNodeTexImage')
                tex_image.image = bpy.data.images.load(f"{file_path}/{texture_name}.tga")  # Ensure texture path is correct
                
                # Link texture to the shader
                material.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])

                # Assign material to the object
                obj.data.materials.append(material)
            else:
                print(f"Image {texture_name} not found.")
        else:
            print(f"No texture available for object {obj.name}.")

def load_render_mesh(reader, objectname):
    hsem, d3dr, dner, xtrv, ecaf = parse_mesh_data(reader)  # Parse your data

    vertex_positions = xtrv[['px', 'py', 'pz']].tolist()
    triangle_indices = ecaf
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
        object_triangle_indices = triangle_indices[face_start:face_end]

        # Create the mesh data for this object
        mesh.from_pydata(vertex_positions, [], object_triangle_indices)

        # Extract UV coordinates (primary: u, v)
        primary_uv_coordinates = xtrv[['u', 'v']].tolist()
        flipped_primary_uv_coordinates = [(1.0 - u, 1.0 - v) for u, v in primary_uv_coordinates]

        # Create the primary UV map for the mesh
        if not mesh.uv_layers:
            mesh.uv_layers.new(name="PrimaryUVMap")

        primary_uv_layer = mesh.uv_layers.active.data
        for i, loop in enumerate(mesh.loops):
            primary_uv_layer[i].uv = flipped_primary_uv_coordinates[loop.vertex_index]

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
    filepath = args[0]
    name = bpy.path.display_name_from_filepath(filepath)

    reader = reader_ilff.open_ilff(str(filepath))

    # Find textures for the model
    textures = find_textures_for_model(name)

    # Load mesh objects based on face ranges
    objects = load_render_mesh(reader, name)

    # Assign textures to the objects
    assign_textures_to_objects(objects, textures)

    # Join objects into one and rename
    joined_object = join_objects_and_rename(objects, name)

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Select and activate the joined object
    joined_object.select_set(True)
    bpy.context.view_layer.objects.active = joined_object

    # Set the scale
    joined_object.scale = (0.0005, 0.0005, 0.0005)

def load(*args, **kwargs):
    load_mef(*args, **kwargs)
    return {'FINISHED'}