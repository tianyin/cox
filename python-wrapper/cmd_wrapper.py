import os
import shutil
import subprocess

#javac -d bin/ -sourcepath src -cp lib/lucene-core-4.7.1.jar:lib/lucene-analyzers-common-4.7.1.jar:lib/lucene-queryparser-4.7.1.jar:lib/lucene-queries-4.7.1.jar:lib/commons-cli-1.2.jar:lib/commons-cli-1.2-javadoc.jar src/iconfigure/SearchFiles.java

cur_dir = os.path.dirname(os.path.abspath(__file__))
poj_dir = os.path.dirname(cur_dir)

def get_classpath():
    classpath = ''
    lib_dir = os.path.join(poj_dir, 'lib/')

    #add the libs    
    jarlist = os.listdir(lib_dir)
    for jar in jarlist:
        classpath += os.path.join(lib_dir, jar) + ':'

    #add the cox jar
    classpath += os.path.join(poj_dir, 'cox.jar')
    return classpath

def execute_index(index_path, dst_dir, popularity_file, only_pname=False):
#java -cp bin/:lib/lucene-core-4.7.1.jar:lib/lucene-analyzers-common-4.7.1.jar:lib/lucene-queryparser-4.7.1.jar:lib/lucene-queries-4.7.1.jar:lib/commons-cli-1.2.jar:lib/commons-cli-1.2-javadoc.jar iconfigure.SearchFiles
    cmds = ['java',
            '-cp', get_classpath(),
            #'-cp', os.path.join(poj_dir, 'bin/') + 'cox.jar',
            'IndexManualPages']
    cmds += ['-i', index_path]
    cmds += ['-d', dst_dir]
    if not popularity_file is None:
        cmds += ['-p', popularity_file]
    if only_pname == True:
        cmds += ['-m', 'onlyname']    

    if not os.path.exists(index_path):
        os.mkdir(index_path)

    subprocess.call(cmds)

def extract_search_outputfile(output_file):
    fh = open(output_file, 'r')
    res = {}
    for line in fh:
        lns = [x.strip() for x in line.split('|')]
        #lns = [x.replace("log_slow_queries", "slow_query_log") for x in lns]
        name = lns[0]
        opts = lns[1:]
        res[name] = opts

    return res

def execute_search(index_path, input_file, output_file, filter_file, optimization=True, strict_mode=False):
    cmds = ['java',
            #'-cp', os.path.join(poj_dir, 'bin/') + ':' + classpath_for_java(),
            '-cp', get_classpath(),
            'Navigator']
    cmds += ['-i', index_path]
    cmds += ['-f', input_file]
    cmds += ['-o', output_file]
    
    if filter_file:
        cmds += ['-x', filter_file]
    if optimization:
        cmds += ['-a']
    if strict_mode:
        cmds += ['-s']

    subprocess.call(cmds)
    return extract_search_outputfile(output_file)
