import os
import json
import csv
import sys
from config import EvalConfig
from evaluator import eval_wrap

if __name__ == '__main__':
    appname  = 'httpd'
    parpath  = '../dataset/httpd/parameters'
    poppath  = '../benchmarks/data/apache_popularity.csv' 
    p2mmaps  = '../benchmarks/data/apache_modules.csv'
    testcase = '../benchmarks/data/apache_tc_icon.csv' 
    base_dir = '../benchmarks/data/' + appname
    config = EvalConfig(appname, parpath, poppath, p2mmaps, None, testcase, base_dir)
    eval_wrap(config)

    appname  = 'hadoop'
    parpath  = '../dataset/hadoop/parameters'
    poppath  = '../benchmarks/data/hadoop_popularity.csv' 
    p2mmaps  = None
    rnmmaps  = '../benchmarks/data/hadoop_rename.txt'
    testcase = '../benchmarks/data/hadoop_tc_icon.csv' 
    base_dir = '../benchmarks/data/' + appname
    config = EvalConfig(appname, parpath, poppath, p2mmaps, rnmmaps, testcase, base_dir)
    #eval_wrap(config)

    appname  = 'mysql'
    parpath  = '../dataset/mysql/parameters'
    poppath  = '../benchmarks/data/mysql_popularity.csv' 
    p2mmaps  = None
    testcase = '../benchmarks/data/mysql_tc_icon.csv' 
    base_dir = '../benchmarks/data/' + appname
    config = EvalConfig(appname, parpath, poppath, p2mmaps, None, testcase, base_dir)
    #eval_wrap(config)

