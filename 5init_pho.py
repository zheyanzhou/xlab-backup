import uproot
import numpy as np

# 打开 .root 文件并提取树和分支
file1, file2 = uproot.open("czt_rec.root"), uproot.open("tru_ele.root")
pho_tree, ele_tree = file1["czt_rec"], file2["ele_tru"]

# 定义分支并加载数据
pho_data = {key: pho_tree[branch].array(library="np") for key, branch in {
    "energy": "ene_rec", "rec_x": "rec_x", "rec_y": "rec_y", "rec_z": "rec_z"}.items()}

ele_data = {key: ele_tree[branch].array(library="np") for key, branch in {
    "energy": "energy", "momentum_x": "momentum_x", "momentum_y": "momentum_y", 
    "momentum_z": "momentum_z", "vertex_x": "vertex_x", "vertex_y": "vertex_y", 
    "vertex_z": "vertex_z"}.items()}

# 计算入射光子的方向矢量并归一化
sca_dir = np.array([pho_data["rec_x"] - ele_data["vertex_x"],
                    pho_data["rec_y"] - ele_data["vertex_y"],
                    pho_data["rec_z"] - ele_data["vertex_z"]])
magnitude = np.linalg.norm(sca_dir, axis=0)
norm_sca_dir = sca_dir / magnitude

# 计算初始光子的能量和动量
init_pho_ene = pho_data["energy"] + ele_data["energy"] - 0.511  # 电子静质量
init_pho_momentum = pho_data["energy"] * norm_sca_dir + np.array([ele_data["momentum_x"], 
                                                                  ele_data["momentum_y"], 
                                                                  ele_data["momentum_z"]])

# 保存结果到新的 .root 文件
with uproot.recreate("init_pho.root") as f:
    f["rec_init_pho"] = {
        "init_pho_ene": init_pho_ene,
        "init_pho_x": init_pho_momentum[0],
        "init_pho_y": init_pho_momentum[1],
        "init_pho_z": init_pho_momentum[2]
    }

print("Data has been written to init_pho.root")
