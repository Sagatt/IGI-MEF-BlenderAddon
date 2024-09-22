import bpy
import numpy as np
import io_mesh_igi2.reader_ilff as reader_ilff
from io_mesh_igi2.struct_mef import *
    
    
def load_render_mesh(reader):
    hsem, d3dr, dner, xtrv, ecaf = parse_mesh_data(reader)  # Parse your data

    vertex_positions = xtrv[['px', 'py', 'pz']].tolist()
    triangle_indices = ecaf.tolist()

    # Create the mesh
    mesh = bpy.data.meshes.new('render_mesh')
    mesh.from_pydata(vertex_positions, [], triangle_indices)

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

    # Create the object
    render_mesh_object = bpy.data.objects.new('render_mesh_object', mesh)
    
    print_data_chunks(hsem, d3dr, dner, xtrv, ecaf)
    
    return [render_mesh_object]  # Returning the mesh object to link in load_mef

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

def print_data_chunks(hsem, d3dr, dner, xtrv, ecaf):
    """
    Print details of each data chunk for debugging purposes.
    """
    print("HSEM Data Chunk:")
    print_chunk_details(hsem)
    
    print("\nD3DR Data Chunk:")
    print_chunk_details(d3dr)
    
    print("\nDNER Data Chunk:")
    print_chunk_details(dner)
    
    print("\nXTRV Data Chunk:")
    print_chunk_details(xtrv)
    
    print("\nECAF Data Chunk:")
    print_chunk_details(ecaf)

def print_chunk_details(chunk):
    """
    Print details of a given data chunk.
    """
    if isinstance(chunk, list):
        for i, item in enumerate(chunk):
            print(f"Item {i}: {item}")
    elif isinstance(chunk, dict):
        for key, value in chunk.items():
            print(f"{key}: {value}")
    elif hasattr(chunk, 'dtype') and hasattr(chunk, 'tolist'):
        # Assuming it's a numpy structured array or similar
        for name in chunk.dtype.names:
            print(f"{name}: {chunk[name].tolist()}")
    else:
        print(chunk)


def load_collision_mesh(reader):
    NotImplemented

"""#Shadow Models
def load_shadow_mesh(reader):
    sems_bytes = reader.read(b'SEMS')
    xtvs_bytes = reader.read(b'XTVS')
    cafs_bytes = reader.read(b'CAFS')
    egde_bytes = reader.read(b'EGDE')

    sems = np.frombuffer(sems_bytes, DTYPE_SEMS)
    xtvs = np.frombuffer(xtvs_bytes, DTYPE_XTVS)
    cafs = np.frombuffer(cafs_bytes, DTYPE_CAFS)
    egde = np.frombuffer(egde_bytes, DTYPE_EGDE)

    positions = xtvs.tolist()

    triangles_indices = cafs[['a', 'b', 'c']].tolist()
    triangles_normals = cafs[['nx', 'ny', 'nz']].tolist()

    edges = egde.tolist()

    mesh = bpy.data.meshes.new('shadow_mesh')
    mesh.from_pydata(positions, edges, triangles_indices)
    mesh.update()
    mesh.validate()

    meshobject = bpy.data.objects.new('shadow_mesh_object', mesh)
    print("Did we use this?")
    return meshobject"""


def load_mef(*args, **kwargs):
    filepath = args[0]
    name = bpy.path.display_name_from_filepath(filepath)

    mainobject = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(mainobject)

    reader = reader_ilff.open_ilff(str(filepath))

    if reader.find(b'HSEM'):
        render_mesh_objects = load_render_mesh(reader)
        
        if not render_mesh_objects:
            return
        
        for render_mesh_object in render_mesh_objects:
            render_mesh_object.parent = mainobject
            bpy.context.collection.objects.link(render_mesh_object)

    elif reader.find(b'SEMS'):
        shadow_mesh_object = load_shadow_mesh(reader)
        shadow_mesh_object.parent = mainobject
        bpy.context.collection.objects.link(shadow_mesh_object)

    # Correctly deselect all objects
    for scene_object in bpy.context.scene.objects:
        scene_object.select_set(False)

    # Select the main object
    mainobject.select_set(True)

    # Set the active object correctly
    view_layer = bpy.context.view_layer
    if view_layer.objects.active is None or view_layer.objects.active.mode == 'OBJECT':
        view_layer.objects.active = mainobject

    mainobject.scale = (0.0005, 0.0005, 0.0005)



def load(*args, **kwargs):
    load_mef(*args, **kwargs)

    return {'FINISHED'}