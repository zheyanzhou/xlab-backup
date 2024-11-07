from podio import reading
import ROOT
from ROOT import TH1F
from ROOT import TFile, TTree, TArrayD
import megat
import math
from array import array

# 输入文件--
input_file = TFile("czt_clu.root", "READ")
input_tree = input_file.Get("czt_clu")

# 输出文件--
output_file = TFile("czt_rec.root", "RECREATE")
tree = TTree("czt_rec", "Tree for reconstructed data of czt")

# 定义存储的变量
ene_rec = array('d', [0])
rec_x = array('d', [0])
rec_y = array('d', [0])
rec_z = array('d', [0])

# 新建分支，存储CZT重建的能量位置信息
tree.Branch("ene_rec", ene_rec, "ene_rec/D")
tree.Branch("rec_x", rec_x, "rec_x/D")
tree.Branch("rec_y", rec_y, "rec_y/D")
tree.Branch("rec_z", rec_z, "rec_z/D")

# 定义 n_clusters 数组来存储簇的数量
n_clusters = array('i', [0])

# 获取事件数量
n_events = input_tree.GetEntries()

for i in range(n_events):
    print(f'{i} event:')
    input_tree.GetEntry(i)
    
    # 从树中获取簇的数量
    n_clusters[0] = getattr(input_tree, "n_clusters")
    #print(f"Number of clusters: {n_clusters}")
    
    # 获取所有簇的位置信息数组
    pos_clu_x_arr = getattr(input_tree, "pos_clu_x")
    pos_clu_y_arr = getattr(input_tree, "pos_clu_y")
    pos_clu_z_arr = getattr(input_tree, "pos_clu_z")

    # 计算所有簇的总能量
    total_energy = 0
    max_energy = 0
    max_cluster_index = -1
        
    # 遍历所有簇，计算总能量并找到能量最大的簇
    for j in range(n_clusters[0]):
        cluster_energy = getattr(input_tree, "ene_clu")[j]
        total_energy += cluster_energy
        #print(f"  Cluster {j}: Energy = {cluster_energy}, Position = ({pos_clu_x_arr[j]}, {pos_clu_y_arr[j]}, {pos_clu_z_arr[j]})")

        # 找到最大能量簇的索引
        if cluster_energy > max_energy:
            max_energy = cluster_energy
            max_cluster_index = j

    # 设置重建能量
    ene_rec[0] = total_energy
    #print(f"Total reconstructed energy: {ene_rec[0]}")

    # 如果有簇的能量大于0，设置重建位置
    if max_cluster_index != -1:
        rec_x[0] = pos_clu_x_arr[max_cluster_index]
        rec_y[0] = pos_clu_y_arr[max_cluster_index]
        rec_z[0] = pos_clu_z_arr[max_cluster_index]
        #print(f"Reconstructed position (max energy cluster): ({rec_x[0]}, {rec_y[0]}, {rec_z[0]})")
    else:
        # 如果没有簇，位置设为0
        rec_x[0] = 0
        rec_y[0] = 0
        rec_z[0] = 0
        #print("No clusters with positive energy. Reconstructed position set to (0, 0, 0)")
    # 填充树的数据
    tree.Fill()

# 写入并关闭文件
output_file.Write()
output_file.Close()
