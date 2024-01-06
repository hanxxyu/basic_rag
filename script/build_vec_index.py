# coding=utf-8
# Filename:    build_vec_index.py
# Author:      ZENGGUANRONG
# Date:        2023-12-12
# description: 构造向量索引
import sys
sys.path.insert(0, '../src')
import json,torch,copy
from tqdm import tqdm
from loguru import logger
from multiprocessing import Process,Queue
from multiprocessing import set_start_method
from models.vec_model.vec_model import VectorizeModel
from searcher.vec_searcher.vec_searcher import VecSearcher 

if __name__ == "__main__":
    # 0. 必要配置
    VEC_MODEL_PATH = r"K:\model\simcse-chinese-roberta-wwm-ext"
    SOURCE_INDEX_DATA_PATH = r"K:\data\baike_qa\baike_qa_train.json"
    VEC_INDEX_DATA = "vec_index_test2023121301_20w"
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else "cpu")
    PROCESS_NUM = 2
    # logger.info("load model done")

    # 1. 加载数据、模型
    vec_model = VectorizeModel(VEC_MODEL_PATH, DEVICE)
    index_dim = len(VectorizeModel(VEC_MODEL_PATH, DEVICE).predict_vec("你好啊")[0])
    source_index_data = []
    with open(SOURCE_INDEX_DATA_PATH, encoding="utf8") as f:
        for line in f:
            ll = json.loads(line.strip())
            if len(ll["title"]) >= 2:
                source_index_data.append([ll["title"], ll])
            if len(ll["desc"]) >= 2:
                source_index_data.append([ll["desc"], ll])
            # if len(source_index_data) > 2000:
            #     break
    # logger.info("load data done: {}".format(len(source_index_data)))
    print("load data done: {}".format(len(source_index_data)))
    # 节省空间，只取前N条
    source_index_data = source_index_data[:200]

    # 2. 创建索引并灌入数据
    # 2.1 构造索引
    vec_searcher = VecSearcher()
    vec_searcher.build(index_dim, VEC_INDEX_DATA)

    # 2.2 推理向量
    vectorize_result = []
    for q in tqdm(source_index_data):
        vec = vec_model.predict_vec(q[0]).cpu().numpy()
        tmp_result = copy.deepcopy(q)
        tmp_result.append(vec)
        vectorize_result.append(copy.deepcopy(tmp_result))

    # 2.3 开始存入
    for idx in tqdm(range(len(vectorize_result))):
        vec_searcher.insert(vectorize_result[idx][2], vectorize_result[idx][:2])

    # 3. 保存
    vec_searcher.save()