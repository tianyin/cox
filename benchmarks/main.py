import os
import json
import csv
import sys
from config import EvalConfig
from evaluator import eval_wrap

if __name__ == '__main__':
    appname  = 'httpd'
    parpath  = '/home/tianyin/Cox/dataset/httpd/parameters'
    poppath  = '/home/tianyin/Cox/benchmarks/data/apache_popularity.csv' 
    p2mmaps  = '/home/tianyin/Cox/benchmarks/data/apache_modules.csv'
    testcase = '/home/tianyin/Cox/benchmarks/data/apache_tc_icon.csv' 
    base_dir = '/home/tianyin/Cox/benchmarks/data/' + appname
    config = EvalConfig(appname, parpath, poppath, p2mmaps, None, testcase, base_dir)
    eval_wrap(config)

    appname  = 'hadoop'
    parpath  = '/home/tianyin/Cox/dataset/hadoop/parameters'
    poppath  = '/home/tianyin/Cox/benchmarks/data/hadoop_popularity.csv' 
    p2mmaps  = None
    rnmmaps  = '/home/tianyin/Cox/benchmarks/data/hadoop_rename.txt'
    testcase = '/home/tianyin/Cox/benchmarks/data/hadoop_tc_icon.csv' 
    base_dir = '/home/tianyin/Cox/benchmarks/data/' + appname
    config = EvalConfig(appname, parpath, poppath, p2mmaps, rnmmaps, testcase, base_dir)
    #eval_wrap(config)

    appname  = 'mysql'
    parpath  = '/home/tianyin/Cox/dataset/mysql/parameters'
    poppath  = '/home/tianyin/Cox/benchmarks/data/mysql_popularity.csv' 
    p2mmaps  = None
    testcase = '/home/tianyin/Cox/benchmarks/data/mysql_tc_icon.csv' 
    base_dir = '/home/tianyin/Cox/benchmarks/data/' + appname
    config = EvalConfig(appname, parpath, poppath, p2mmaps, None, testcase, base_dir)
    #eval_wrap(config)

