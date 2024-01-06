# coding=utf-8
# Filename:    main_service_online.py
# Author:      ZENGGUANRONG
# Date:        2023-09-10
# description: tornado服务启动核心脚本

import sys
from loguru import logger

import tornado.ioloop
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
from tornado.options import options, define
from multiprocessing import Process


from  searcher.searcher import Searcher
from  models.vec_model.vec_model import VectorizeModel
from  models.llm.llm_model import LlmModel
from  dm.dialogue_manager import DialogueManager

from  server.handlers.search_handler import SearcherHandler,StartSearcherHandler
# from  server.handlers.vec_model_handler import VecModelHandler,StartVecModelHandler
from  server.handlers.llm_handler import LlmModel,StartLlmHandler
from  server.handlers.dialogue_manager_handler import DialogueManagerHandler, StartDialogueManagerHandler

def launch_service(config, model_mode):
    if model_mode == "llm_model":
        # 解决windows下多进程使用pt会导致pickle序列化失败的问题，https://blog.csdn.net/qq_21774161/article/details/127145749
        llm_model = LlmModel(config["process_llm_model"]["model_path"], config["process_llm_model"]["model_config"])
        StartLlmHandler(config["process_llm_model"], llm_model)
        # processes = [process_llm_model]
        # for process in processes:
        #     process.start()
        # for process in processes:
        #     process.join()
    elif model_mode == "searcher":
        searcher = Searcher(config["process_searcher"]["VEC_MODEL_PATH"], config["process_searcher"]["VEC_INDEX_DATA"])
        process_searcher = Process(target=StartSearcherHandler, args=(config["process_searcher"], searcher))

        dialogue_manager = DialogueManager(config["process_dialogue_manager"])
        process_dialogue_manager = Process(target=StartDialogueManagerHandler, args=(config["process_dialogue_manager"], dialogue_manager))
        # vec_model = VectorizeModel(config["process_vec_model"]["VEC_MODEL_PATH"])
        # process_vec_model = Process(target=StartVecModelHandler, args=(config["process_vec_model"], vec_model))

        # processes = [process_searcher]
        processes = [process_searcher, process_dialogue_manager]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
    else:
        logger.info("init service error")


if __name__ == "__main__":
    config = {"process_searcher":{"port":9090, 
                                      "url_suffix":"/searcher", 
                                      "VEC_MODEL_PATH":"K:\model\simcse-chinese-roberta-wwm-ext",
                                      "VEC_INDEX_DATA":"vec_index_test2023121301_20w"},
             "process_vec_model":{"port":9091, 
                                      "url_suffix":"/vec_model", 
                                      "VEC_MODEL_PATH":"K:\model\simcse-chinese-roberta-wwm-ext"},
             "process_llm_model":{"port":9092, 
                                      "url_suffix":"/llm_model", 
                                      "model_path":"C:\\work\\tool\\chatglm2-6b",
                                      "model_config":{}},
             "process_dialogue_manager":{"port":9093, 
                                      "url_suffix":"/dialogue_manager",
                                      "config":{"search_url":"http://127.0.0.1:9090/searcher",
                                                "llm_url":"http://127.0.0.1:9092/llm_model"}}
    }
    launch_service(config, sys.argv[1])