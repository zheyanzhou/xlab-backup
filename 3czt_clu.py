from podio import reading
import megat
from ROOT import TFile, TTree
from array import array

# 定义通过 cellID 获取全局坐标的函数
def get_global_position(hit, idconverter):
    cellid = hit.getCellID()  # 获取当前 hit 的 cellID
    global_position = idconverter.position(cellid)  # 使用 idconverter 获取全局坐标
    return global_position  # 返回坐标

# 从文件中读取数据
try:
    reader = reading.get_reader('compton_hit_smear.root')  # 创建一个读取器
    evts = reader.get('events')  # 提取事件数据
except Exception as e:
    print(f"Error reading the file: {e}")
    exit(1)

# 新建一个czt_clu.root文件
output_file = TFile("czt_clu.root", "RECREATE")  # 创建输出文件
tree = TTree("czt_clu", "Tree for czt clustered data")  # 新建一个树

# 定义存储多个cluster的变量 (动态数组)
MAX_CLUSTERS = 10
ene_clu = array('d', [0] * MAX_CLUSTERS)
pos_clu_x = array('d', [0] * MAX_CLUSTERS)
pos_clu_y = array('d', [0] * MAX_CLUSTERS)
pos_clu_z = array('d', [0] * MAX_CLUSTERS)
cluster_size = array('i', [0] * MAX_CLUSTERS)
n_clusters = array('i', [0])

# 创建分支
tree.Branch("n_clusters", n_clusters, "n_clusters/I")
tree.Branch("ene_clu", ene_clu, "ene_clu[n_clusters]/D")
tree.Branch("pos_clu_x", pos_clu_x, "pos_clu_x[n_clusters]/D")
tree.Branch("pos_clu_y", pos_clu_y, "pos_clu_y[n_clusters]/D")
tree.Branch("pos_clu_z", pos_clu_z, "pos_clu_z[n_clusters]/D")
tree.Branch("cluster_size", cluster_size, "cluster_size[n_clusters]/I")

# 初始化 decoder 用于解码cellID
decoder = megat.getCztDecoder()
idconverter = megat.getIdConverter('CztHits') 

# 遍历每一个事件
for i, evt in enumerate(evts):
    print(f'{i} event:')
    calo_hits = evt.get('CaloHits')

    if len(calo_hits) == 0:  # 如果当前事件没有任何hit
        # 直接将所有相关变量设为0
        n_clusters[0] = 0
        for j in range(MAX_CLUSTERS):
            ene_clu[j] = 0
            pos_clu_x[j] = 0
            pos_clu_y[j] = 0
            pos_clu_z[j] = 0
            cluster_size[j] = 0
    else:
        # 只保留能量大于等于0.1的hit
        filtered_hits = [hit for hit in calo_hits if hit.getEnergy() >= 0.1]#电子学阈值
        
        unclustered_hits = set(filtered_hits)
        cluster_count = 0

        while unclustered_hits and cluster_count < MAX_CLUSTERS:
            current_cluster = []
            to_check = [unclustered_hits.pop()]

            total_energy = 0
            weighted_x = 0
            weighted_y = 0
            weighted_z = 0

            while to_check:
                current_hit = to_check.pop()
                
                # 使用封装的函数获取全局坐标
                current_pos = get_global_position(current_hit, idconverter)
                current_cluster.append(current_hit)

                ene = current_hit.getEnergy()
                total_energy += ene
                weighted_x += ene * current_pos.x
                weighted_y += ene * current_pos.y
                weighted_z += ene * current_pos.z

                current_cellid = current_hit.getCellID()
                current_system = decoder.get(current_cellid, "system")
                current_section = decoder.get(current_cellid, "section")
                current_layer = decoder.get(current_cellid, "layer")
                current_row = decoder.get(current_cellid, "row")
                current_column = decoder.get(current_cellid, "column")
                current_x = decoder.get(current_cellid, "x")
                current_y = decoder.get(current_cellid, "y")

                for hit in list(unclustered_hits):  # 遍历未聚类的hit
                    hit_cellid = hit.getCellID()

                    hit_system = decoder.get(hit_cellid, "system")
                    hit_section = decoder.get(hit_cellid, "section")
                    hit_layer = decoder.get(hit_cellid, "layer")
                    hit_row = decoder.get(hit_cellid, "row")
                    hit_column = decoder.get(hit_cellid, "column")
                    hit_x = decoder.get(hit_cellid, "x")
                    hit_y = decoder.get(hit_cellid, "y")

                    # 判断是否相邻
                    if (
                        current_system == hit_system and  # system相同
                        current_section == hit_section and  # section相同
                        abs(current_layer - hit_layer) <= 1 and  # layer差距小于等于1
                        current_row == hit_row and  # row相同
                        current_column == hit_column and  # column相同
                        abs(current_x - hit_x) <= 1 and  # x差距小于等于1
                        abs(current_y - hit_y) <= 1  # y差距小于等于1
                    ):
                        to_check.append(hit)  # 将该hit加入to_check列表
                        unclustered_hits.remove(hit)  # 从未被聚类的集合中移除

            # 保存当前cluster的结果
            ene_clu[cluster_count] = total_energy
            pos_clu_x[cluster_count] = weighted_x / total_energy
            pos_clu_y[cluster_count] = weighted_y / total_energy
            pos_clu_z[cluster_count] = weighted_z / total_energy
            cluster_size[cluster_count] = len(current_cluster)

            cluster_count += 1

        n_clusters[0] = cluster_count

    # 填充树的数据
    tree.Fill()

# 写入数据并关闭文件
output_file.Write()
output_file.Close()

