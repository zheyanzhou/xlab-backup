import uproot
import numpy as np
import ROOT
from math import acos

# 输入文件
input_file1 = uproot.open("tru_ele.root")
input_file2 = uproot.open("czt_rec.root")
input_file3 = uproot.open("init_pho.root")

# 输出文件
output_file = uproot.recreate("tel_para.root")

# 电子静止质量
e_rest_mass = 0.511  # MeV

# 获取真实的初始光子方向矢量
tx, ty, tz = 0, 0, -1  # 初始光子的真实方向

# 获取指定的Branch数据
e_ene = input_file1["ele_tru"]["energy"].array()
vertex_x = input_file1["ele_tru"]["vertex_x"].array()
vertex_y = input_file1["ele_tru"]["vertex_y"].array()
vertex_z = input_file1["ele_tru"]["vertex_z"].array()
e_x = input_file1["ele_tru"]["momentum_x"].array()
e_y = input_file1["ele_tru"]["momentum_y"].array()
e_z = input_file1["ele_tru"]["momentum_z"].array()

ene_rec = input_file2["czt_rec"]["ene_rec"].array()
rec_x = input_file2["czt_rec"]["rec_x"].array()
rec_y = input_file2["czt_rec"]["rec_y"].array()
rec_z = input_file2["czt_rec"]["rec_z"].array()

init_pho_x = input_file3["rec_init_pho"]["init_pho_x"].array()
init_pho_y = input_file3["rec_init_pho"]["init_pho_y"].array()
init_pho_z = input_file3["rec_init_pho"]["init_pho_z"].array()

# 初始化要填充的数组
phi_geo = []
phi_kin = []
delta_phi_arm = []
is_valid_rec = []
spd_values = []
psf_values = []

# ARM 和其他计算
for i in range(len(ene_rec)):
    if ene_rec[i] > 0 and e_ene[i]< 0.711:
        # 构造矢量
        g0 = np.array([tx, ty, tz])
        g1 = np.array([rec_x[i] - vertex_x[i], rec_y[i] - vertex_y[i], rec_z[i] - vertex_z[i]])
        
        # 计算 phi_geo
        cos_phi = np.dot(g0, g1) / (np.linalg.norm(g0) * np.linalg.norm(g1))
        phi_geo.append(np.arccos(np.clip(cos_phi, -1.0, 1.0)) * 180 / np.pi)
        
        # 计算 phi_kin
        phi_k = np.arccos(1 - e_rest_mass * (1 / ene_rec[i] - 1 / (ene_rec[i] + e_ene[i] - e_rest_mass))) * 180 / np.pi
        phi_kin.append(phi_k)

        # 计算 delta_phi_arm 和 SPD
        delta_phi_arm.append(phi_geo[-1] - phi_k)
        e_mom = np.array([e_x[i], e_y[i], e_z[i]])
        spd = np.arccos(np.clip(np.dot(np.cross(g1, g0), np.cross(g1, e_mom)) / 
                                (np.linalg.norm(np.cross(g1, g0)) * np.linalg.norm(np.cross(g1, e_mom))), -1.0, 1.0)) * 180 / np.pi
        spd_values.append(spd)
        is_valid_rec.append(1)

        # 计算 PSF
        rec_init_pho = np.array([init_pho_x[i], init_pho_y[i], init_pho_z[i]])
        psf = np.arccos(np.dot(rec_init_pho, g0) / (np.linalg.norm(rec_init_pho) * np.linalg.norm(g0))) * 180 / np.pi
        psf_values.append(psf)

    else:
        delta_phi_arm.append(0)
        is_valid_rec.append(0)
        spd_values.append(0)
        psf_values.append(0)

# 将数据写入 .root 文件
output_file["tel_par_tree"] = {
    "delta_phi_arm": delta_phi_arm,
    "is_valid_rec": is_valid_rec,
    "spd_values": spd_values,
    "psf_values": psf_values
}

output_file.close()

