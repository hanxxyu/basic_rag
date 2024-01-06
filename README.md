# rag_framework
basic framework for rag(retrieval augment generation)


data  # 存放检索的原始数据json + 后续会生成保存的向量索引文件
script # 必要脚本 build_vec_index.py 离线构造索引的脚本
src #项目源码（模型、搜索、服务器）
    - models(有不同的模型)
    - searcher （重写搜索系统，向量、字面、数字、经纬度索引、根据不同的数据拆分不同的库、 searcher.py 对外，  vec_searcher 对内
    - server 包裹服务，tornado ， handler（差分若干个自服务就写几个handler）main_service_online.py 启动脚本

## 服务分拆

两个方案：
1. 向量模型和索引拆开成两个服务： 
2. 向量模型和索引合成一个： 放在一个服务内


## models

simcse_model是核心模型：模型和推理

model.py 包裹模型，给出模型预测的特定功能，推理向量，服务化转化，计算相似度

## 检索模块

提供向量索引的解决方案：

VecIndex