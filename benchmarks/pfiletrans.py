import json
import os

def generate_content_by_name(pname):
    content = pname
    content = content.replace('<', '').replace('>', '')
    content = content.replace('.', ' ')
    content = content.replace('_', ' ')
    content = content.replace('-', ' ')
    res = ''
    prev = 'l'
    for i in range(0, len(content)):
        #print i, content[i], content[i].isupper()
        if content[i].isupper():
            if prev == 'l':
                res += (' ' + content[i].lower())
            else:
                res += content[i].lower()
            prev = 'u'
        else:
            res += content[i]
            prev = 'l'
    res = res.strip()
    return res

def generate_pname_files(plist, outdir):
    for p in plist:
        content = generate_content_by_name(p)
        print p, '|', content
        fpath = os.path.join(outdir, p)
        f = open(fpath, 'w')
        f.write(content)
        f.close() 

def generate_pfiles(indir, outdir):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    flist = os.listdir(indir)
    generate_pname_files(flist, outdir)

generate_pfiles('../dataset/httpd/parameters',  '../dataset/httpd/parameters_opn')
generate_pfiles('../dataset/hadoop/parameters', '../dataset/hadoop/parameters_opn')
generate_pfiles('../dataset/mysql/parameters',  '../dataset/mysql/parameters_opn')
#print generate_content_by_name('LogLevel')
#print generate_content_by_name('dfs.dfs.dfs.dfs')
