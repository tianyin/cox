import os
import subprocess

#javac -d bin/ -sourcepath src -cp lib/lucene-core-4.7.1.jar:lib/lucene-analyzers-common-4.7.1.jar:lib/lucene-queryparser-4.7.1.jar:lib/lucene-queries-4.7.1.jar:lib/commons-cli-1.2.jar:lib/commons-cli-1.2-javadoc.jar src/iconfigure/SearchFiles.java

cur_dir = os.path.dirname(os.path.abspath(__file__))
poj_dir = os.path.dirname(cur_dir)

def classpath_for_java():
    lib_dir = os.path.join(poj_dir, 'lib/')
    libs = ['lucene-core-4.7.1.jar', 'lucene-analyzers-common-4.7.1.jar', 'lucene-queryparser-4.7.1.jar',
            'lucene-queries-4.7.1.jar', 'commons-cli-1.2.jar', 'commons-cli-1.2-javadoc.jar']
    cps1 = ''
    for x in libs:
        cps1 += os.path.join(lib_dir, x) + ':'
    cps1 = cps1.strip(':')
    return cps1

def compile():
    cps1 = classpath_for_java()

    bin_dir = os.path.join(poj_dir, 'bin/')
    if not os.path.exists(bin_dir):
        os.mkdir(bin_dir)
    src_dir = os.path.join(poj_dir, 'src/')
    srcs = ['IndexFiles', 'SearchFiles']
    build_cmds = ["javac",
            '-d', bin_dir,
            '-sourcepath', os.path.join(poj_dir, 'src'),
            '-cp', cps1]
    for src in srcs:
        s = os.path.join(src_dir, src + '.java')
        cmd = build_cmds + [s]
        rs = ''
        for c in cmd:
            rs += c + ' '
        #print rs
        subprocess.call(cmd)

    jar_cmd = ['jar', 
            'cf', 'cox.jar',
            bin_dir]
    subprocess.call(jar_cmd)

def execute_index(index_path, dst_dir, popularity_file):
#java -cp bin/:lib/lucene-core-4.7.1.jar:lib/lucene-analyzers-common-4.7.1.jar:lib/lucene-queryparser-4.7.1.jar:lib/lucene-queries-4.7.1.jar:lib/commons-cli-1.2.jar:lib/commons-cli-1.2-javadoc.jar iconfigure.SearchFiles
    cmds = ['java',
            '-cp', os.path.join(poj_dir, 'bin/') + ':' + classpath_for_java(),
            'IndexFiles']
    cmds += ['-i', index_path]
    cmds += ['-d', dst_dir]
    if not popularity_file is None:
        cmds += ['-p', popularity_file]

    if not os.path.exists(index_path):
        os.mkdir(index_path)
    subprocess.call(cmds)

def extract_search_outputfile(output_file):
    fh = open(output_file, 'r')
    res = {}
    for line in fh:
        lns = [x.strip() for x in line.split('|')]
        lns = [x.replace("log_slow_queries", "slow_query_log") for x in lns]
        name = lns[0]
        opts = lns[1:]
        res[name] = opts

    return res

def execute_search(index_path, input_file, output_file, use_improve):
    cmds = ['java',
            '-cp', os.path.join(poj_dir, 'bin/') + ':' + classpath_for_java(),
            'SearchFiles']
    cmds += ['-i', index_path]
    cmds += ['-f', input_file]
    cmds += ['-o', output_file]
    if use_improve:
        cmds += ['-a']
    subprocess.call(cmds)
    return extract_search_outputfile(output_file)

