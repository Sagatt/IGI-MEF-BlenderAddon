import numpy as np

DTYPE_HSEM = np.dtype([
    ('_V',          np.float32),
    ('Date',       (np.uint32, 7)),
    ('model_type',  np.uint32),
    ('reserved_0', (np.uint32, 3)),
    ('vectors', (np.float32, 12)),
    ('num_r_faces',     np.uint32),
    ('num_r_verts',     np.uint32),
    ('num_r_buffer',    np.uint32),
    ('sum_c_faces',     np.uint32),
    ('sum_c_verts',     np.uint32),
    ('sum_c_buffer',    np.uint32),
    ('model_radius',    np.float32),
    ('num_mverts',      np.uint16),
    ('num_attachments', np.uint16),
    ('num_pverts',      np.uint16),
    ('num_pfaces',      np.uint16),
    ('num_portals',     np.uint16),
    ('num_bones',       np.uint16),
    ('num_glows',       np.uint16),
    ('rs',          (np.uint8, 38)),# (330_04_1,631_01_1,933_07_1)
    ])

DTYPE_ATTA = np.dtype([
    ('name',(np.string_, 16)),
    ('px',   np.float32),
    ('py',   np.float32),
    ('pz',   np.float32),
    ('_00',  np.float32),
    ('_01',  np.float32),
    ('_02',  np.float32),
    ('_03',  np.float32),
    ('_04',  np.float32),
    ('_05',  np.float32),
    ('_06',  np.float32),
    ('_07',  np.float32),
    ('_08',  np.float32),
    ('_09',  np.uint32),
    ('_an',  np.int32),  
    ])
    

DTYPE_XTVM = (np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ('_0', np.int32), 
    ]))

DTYPE_TROP = np.dtype([
    ('o_vertex', np.uint32),
    ('n_vertex', np.uint32),
    ('o_face',   np.uint32),
    ('n_face',   np.uint32),
    ('id',       np.uint32),
    ])

DTYPE_XVTP = np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ])

DTYPE_CFTP = np.dtype([
    ('a', np.uint32),
    ('b', np.uint32),
    ('c', np.uint32),
    ])

DTYPE_D3DR_0 = np.dtype([
    ('_4',        np.uint32),
    ('num_face',  np.uint32),
    ('num_mesh',  np.uint32),
    ('num_verts', np.uint32),
    ('reserved', (np.uint32,5)),
    ])
DTYPE_D3DR_1 = np.dtype([
    ('_4',        np.uint32),
    ('num_face',  np.uint32),
    ('num_mesh',  np.uint32),
    ('verts_0',   np.uint32),
    ('verts_1',   np.uint32),
    ('num_verts', np.uint32),
    ('reserved', (np.uint32,4)),
    ])
DTYPE_D3DR_3 = np.dtype([
    ('_4',        np.uint32),
    ('num_lmap',  np.uint32),
    ('num_face',  np.uint32),
    ('num_mesh',  np.uint32),
    ('num_verts', np.uint32),
    ('reserved', (np.uint32,6)),
    ])

DTYPE_ECAF = np.dtype([
    ('a', np.uint16),
    ('b', np.uint16),
    ('c', np.uint16),
    ])

DTYPE_DNER_0 = np.dtype([
    ('_opacity',      np.uint8),
    ('_mshine',       np.uint8),
    ('_Scolor',       np.uint8),
    ('_Opacitd',      np.uint8),     
    ('px',            np.float32),
    ('py',            np.float32),
    ('pz',            np.float32),
    ('offset_index',  np.uint16),
    ('num_face',      np.uint16),
    ('off_verts',     np.uint16),
    ('num_verts',     np.uint16),
    ('_td',           np.int16),
    ('_tb',           np.int16),
    ('_tr',           np.int16),    
    ('_trd',          np.uint8),
    ('_tbd',          np.uint8),
    ])
DTYPE_DNER_3 = np.dtype([
    ('_opacity',      np.uint8),
    ('_mshine',       np.uint8),
    ('_mcolor',       np.uint8),
    ('_Opacitd',      np.uint8), 
    ('px',            np.float32),
    ('py',            np.float32),
    ('pz',            np.float32),
    ('offset_index',  np.uint16),
    ('num_face',      np.uint16),
    ('off_verts',     np.uint16),
    ('num_verts',     np.uint16),
    ('_td',           np.int16),
    ('_lmap',         np.int16),    
    ])

DTYPE_XTRV_0 = np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ('nx', np.float32),
    ('ny', np.float32),
    ('nz', np.float32),
    ('u',  np.float32),
    ('v',  np.float32),
    ])
DTYPE_XTRV_1 = np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ('nx', np.float32),
    ('ny', np.float32),
    ('nz', np.float32),
    ('u',  np.float32),
    ('v',  np.float32),
    ('w',  np.float32),
    ('vn', np.uint16),
    ('bn', np.uint16),   
    ])
DTYPE_XTRV_2 = np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ('nx', np.float32),
    ('ny', np.float32),
    ('nz', np.float32),
    ('u',  np.float32),
    ('v',  np.float32),
    ('u1', np.float32),
    ('v1', np.float32),
    ])
DTYPE_XTRV_3 = np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ('u',  np.float32),
    ('v',  np.float32),
    ('u1', np.float32),
    ('v1', np.float32),
    ])

DTYPE_REIH_P1 = np.dtype([
    ('num_child', np.uint8),
    ])
DTYPE_REIH_P2 = np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ])

DTYPE_MANB = np.dtype([
    ('bone_name', (np.string_, 16)),
    ])

DTYPE_WOLG = np.dtype([
    ('px',  np.float32),
    ('py',  np.float32),
    ('pz',  np.float32),
    ('size',np.float32),
    ('R',   np.float32),
    ('G',   np.float32),
    ('B',   np.float32),
    ('_r0', np.uint32),
    ])

DTYPE_PMTL = np.dtype([
    ('_x', np.uint16),
    ('_y', np.uint16),
    ('_z', np.uint16),
    ('_w', np.uint16),
    ])

DTYPE_HSMC = np.dtype([
    ('num_face_0' ,   np.uint32),
    ('num_vertex_0' , np.uint32),
    ('num_material_0',np.uint32),
    ('num_sphere_0' , np.uint32), 
    ('_0',            np.uint32),
    ('_1',            np.uint32),
    ('_2',            np.uint32),
    ('_3',            np.uint32),
    ('num_face_1' ,   np.uint32),
    ('num_vertex_1' , np.uint32),
    ('num_material_1',np.uint32),
    ('num_sphere_1' , np.uint32),
    ('_4',            np.uint32),
    ('_5',            np.uint32),
    ('_6',            np.uint32),
    ('_7',            np.uint32),
    ])

DTYPE_XTVC_0 = np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ('r0', np.uint32),
    ('ry',np.float32),#Dep.
    ])
DTYPE_XTVC_1 = np.dtype([
    ('px',  np.float32),
    ('py',  np.float32),
    ('pz',  np.float32),
    ('bn',  np.uint32),
    ('r0',  np.uint32),
    ])
DTYPE_XTVC_3 = np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ('u1', np.float32),
    ('v1', np.float32),
    ])

DTYPE_ECFC = np.dtype([
    ('a',    np.uint16),
    ('b',    np.uint16),
    ('c',    np.uint16),
    ('_mat', np.uint16),
    ('_lmp', np.uint16),
    ('_Vrt', np.uint16),#Dep.
    ])

DTYPE_TAMC = np.dtype([
    ('opacity',     np.float32),
    ('portal',      np.uint16),
    ('diffuse',     np.int16),
    ('unknown0',    np.uint16),#???.
    ('unknown1',    np.uint16),#???.
    ('mat_id',      np.int16),
    ('unknown',     np.uint16),#Dep.
    ])

DTYPE_HPSC = np.dtype([
    ('px',   np.float32),
    ('py',   np.float32),
    ('pz',   np.float32),
    ('size', np.float32),
    ('_0',    np.uint16),
    ('_1',    np.uint16),
    ('_a',    np.uint16),
    ('_b',    np.uint16),
    ])

DTYPE_HPRM_P1 = np.dtype([
    ('count_00', np.uint32),
    ])
DTYPE_HPRM_P2 = np.dtype([
    ('_Vn', np.uint32),
    ('_px', np.float32),
    ('_py', np.float32),
    ('_pz', np.float32),
    ])

DTYPE_TXAN = np.dtype([
    ('_00', np.uint32),
    ('_01', np.uint32),       
    ])

DTYPE_SEMS = np.dtype([
    ('offset_sfaces', np.uint32),
    ('offset_sverts', np.uint32),
    ('offset_sedges', np.uint32),
    ('num_sfaces',    np.uint32),
    ('num_sverts',    np.uint32),
    ('num_sedges',    np.uint32),
    ('index_num',     np.int32),
    ])

DTYPE_XTVS = np.dtype([
    ('px', np.float32),
    ('py', np.float32),
    ('pz', np.float32),
    ])

DTYPE_CAFS = np.dtype([
    ('a',  np.uint32),
    ('b',  np.uint32),
    ('c',  np.uint32),
    ('_0', np.uint32),
    ('nx', np.float32),
    ('ny', np.float32),
    ('nz', np.float32),
    ])

DTYPE_CAF2 = np.dtype([
    ('a',  np.uint32),
    ('b',  np.uint32),
    ('c',  np.uint32),
    ])

DTYPE_EGDE = np.dtype([
    ('a', np.uint32),
    ('b', np.uint32),
    ])


def parse_hsem(hsem_bytes):
    return np.frombuffer(hsem_bytes, DTYPE_HSEM)

def parse_atta(atta_bytes):
    return np.frombuffer(atta_bytes, DTYPE_ATTA)

def parse_xtvm(xtvm_bytes):
    return np.frombuffer(xtvm_bytes, DTYPE_XTVM)

def parse_trop(trop_bytes):
    return np.frombuffer(trop_bytes, DTYPE_TROP)

def parse_xvtp(xvtp_bytes):
    return np.frombuffer(xvtp_bytes, DTYPE_XVTP)

def parse_cftp(cftp_bytes):
    return np.frombuffer(cftp_bytes, DTYPE_CFTP)

def parse_ecaf(ecaf_bytes):
    ecaf_data = np.frombuffer(ecaf_bytes, DTYPE_ECAF)
    
    faces = [(face['a'], face['b'], face['c']) for face in ecaf_data]
    
    return faces

def parse_d3dr(d3dr_bytes, model_type):
    if model_type == 0:
        return np.frombuffer(d3dr_bytes, DTYPE_D3DR_0)
    if model_type == 1:
        return np.frombuffer(d3dr_bytes, DTYPE_D3DR_1)
    if model_type == 3:
        return np.frombuffer(d3dr_bytes, DTYPE_D3DR_3)

def parse_dner(dner_bytes, model_type):
    if model_type == 0:
        return np.frombuffer(dner_bytes, DTYPE_DNER_0)
    if model_type == 1:
        return np.frombuffer(dner_bytes, DTYPE_DNER_0)
    if model_type == 3:
        return np.frombuffer(dner_bytes, DTYPE_DNER_3)

def parse_xtrv(xtrv_bytes, model_type):
    if model_type == 0:
        return np.frombuffer(xtrv_bytes, DTYPE_XTRV_0)
    if model_type == 1:
        return np.frombuffer(xtrv_bytes, DTYPE_XTRV_1)
    if model_type == 2:
        return np.frombuffer(xtrv_bytes, DTYPE_XTRV_2)
    if model_type == 3:
        return np.frombuffer(xtrv_bytes, DTYPE_XTRV_3)

def parse_xtvc(xtvc_bytes, model_type):
    if model_type == 0:
        return np.frombuffer(xtvc_bytes, DTYPE_XTVC_0)
    if model_type == 1:
        return np.frombuffer(xtvc_bytes, DTYPE_XTVC_1)
    if model_type == 3:
        return np.frombuffer(xtvc_bytes, DTYPE_XTVC_3)

def parse_reih(reih_bytes):
    count = len(reih_bytes) // 13
    align = len(reih_bytes) % 13

    p1 = np.frombuffer(reih_bytes[:count], DTYPE_REIH_P1)
    p2 = np.frombuffer(reih_bytes[count+align:], DTYPE_REIH_P2)

    return p1, p2

def parse_manb(manb_bytes):
    return np.frombuffer(manb_bytes, DTYPE_MANB)

def parse_wolg(wolg_bytes):
    return np.frombuffer(wolg_bytes, DTYPE_WOLG)

def parse_pmtl(pmtl_bytes):
    return np.frombuffer(pmtl_bytes, DTYPE_PMTL)

def parse_hsmc(hsmc_bytes):
    return np.frombuffer(hsmc_bytes, DTYPE_HSMC)

def parse_ecfc(ecfc_bytes):
    return np.frombuffer(ecfc_bytes, DTYPE_ECFC)

def parse_tamc(tamc_bytes):
    return np.frombuffer(tamc_bytes, DTYPE_TAMC)

def parse_hpsc(hpsc_bytes):
    return np.frombuffer(hpsc_bytes, DTYPE_HPSC)

def parse_hprm(hprm_bytes):
    return (np.frombuffer(hprm_bytes[:64], DTYPE_HPRM_P1)), (np.frombuffer(hprm_bytes[64:], DTYPE_HPRM_P2))

def parse_txan(txan_bytes):
    return np.frombuffer(txan_bytes, DTYPE_TXAN)

def parse_sems(sems_bytes):
    return np.frombuffer(sems_bytes, DTYPE_SEMS)

def parse_xtvs(xtvs_bytes):
    return np.frombuffer(xtvs_bytes, DTYPE_XTVS)

def parse_cafs(cafs_bytes):
    return np.frombuffer(cafs_bytes, DTYPE_CAFS)

def parse_caf2(cafs_bytes):
    return np.frombuffer(cafs_bytes, DTYPE_CAF2)

def parse_egde(egde_bytes):
    return np.frombuffer(egde_bytes, DTYPE_EGDE)
    
