import os
import json
import csv
import sys
from config import EvalConfig
from evaluator import eval_wrapper

def run_bench(suffix=''):
    appname  = 'httpd'
    parpath  = '../dataset/httpd/parameters'+suffix
    poppath  = '../benchmarks/data/apache_popularity.csv' 
    p2mmaps  = '../benchmarks/data/apache_modules.csv'
    filtpath = '/home/tixu/Cox/benchmarks/data/apache_must_set_parameters.lst'
    testcase = '../benchmarks/data/apache_tc_icon.csv' 
    base_dir = '../benchmarks/data/' + appname
    #config = EvalConfig(appname, parpath, poppath, p2mmaps, None, filtpath, testcase, base_dir)
    config = EvalConfig(appname, parpath, poppath, p2mmaps, None, None, testcase, base_dir)
    eval_wrapper(config)

    appname  = 'hadoop'
    parpath  = '../dataset/hadoop/parameters'+suffix
    poppath  = '../benchmarks/data/hadoop_popularity.csv' 
    p2mmaps  = None
    rnmmaps  = '../benchmarks/data/hadoop_rename.txt'
    testcase = '../benchmarks/data/hadoop_tc_icon.csv' 
    base_dir = '../benchmarks/data/' + appname
    config = EvalConfig(appname, parpath, poppath, p2mmaps, rnmmaps, None, testcase, base_dir)
    eval_wrapper(config)

    appname  = 'mysql'
    parpath  = '../dataset/mysql/parameters'+suffix
    poppath  = '../benchmarks/data/mysql_popularity.csv' 
    p2mmaps  = None
    testcase = '../benchmarks/data/mysql_tc_icon.csv' 
    base_dir = '../benchmarks/data/' + appname
    config = EvalConfig(appname, parpath, poppath, p2mmaps, None, None, testcase, base_dir)
    eval_wrapper(config)

if __name__ == '__main__':
    #run_bench()
    run_bench('_opn')
