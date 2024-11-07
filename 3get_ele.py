from podio import reading
import ROOT
from ROOT import TH1F
from ROOT import TFile, TTree, TArrayD
import megat
import math
from podio import reading
from array import array

#this file is used to get the information of the electron from the generator
#uesd while using the compton generator
#using the true information to replace the reconstruction of the e-

# 打开源文件以读取数据
reader = reading.get_reader('compton_hit_smear.root')
evts=reader.get('events')

# 创建一个新的ROOT文件以保存数据
output_file = TFile('tru_ele.root', 'RECREATE')
tree = TTree('ele_tru', 'True Electron Data Tree')

# 创建变量以存储每个事件的数据
vertex_x = array('d', [0])
vertex_y = array('d', [0])
vertex_z = array('d', [0])
energy = array('d', [0])
momentum_x = array('d', [0])
momentum_y = array('d', [0])
momentum_z = array('d', [0])

# 创建树的分支
tree.Branch('vertex_x', vertex_x, 'vertex_x/D')  # 使用浮点数类型
tree.Branch('vertex_y', vertex_y, 'vertex_y/D')
tree.Branch('vertex_z', vertex_z, 'vertex_z/D')
tree.Branch('energy', energy, 'energy/D')
tree.Branch('momentum_x', momentum_x, 'momentum_x/D')
tree.Branch('momentum_y', momentum_y, 'momentum_y/D')
tree.Branch('momentum_z', momentum_z, 'momentum_z/D')

# 读取每个事件并提取电子信息
for evt in evts:
    pri = evt.get('PrimaryParticles')
    prie = pri[0]  # 选择第一个主粒子（电子）

    # 获取电子的顶点、能量和动量
    ver = prie.getVertex()
    e = prie.getEnergy()
    m = prie.getMomentum()

    # 存储数据
    vertex_x[0] = ver.x  # 直接将值赋给数组的第一个元素
    vertex_y[0] = ver.y
    vertex_z[0] = ver.z
    energy[0] = e
    momentum_x[0] = m.x
    momentum_y[0] = m.y
    momentum_z[0] = m.z

    # 填充树
    tree.Fill()

# 保存树并关闭文件
output_file.Write()
output_file.Close()
