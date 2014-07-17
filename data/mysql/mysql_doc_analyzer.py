from lxml import etree
from lxml.html import fromstring
import lxml.html as lh
from StringIO import StringIO

import csv
import os


all_versions = []
all_version_pset = {}


def norm(pstr):
    """
    pstr is a parameter string
    """
    par = pstr
    if par.startswith('--'):
        par = par[2:]
    par = par.replace('-', '_')
    if par.find('=') != -1:
        par = par[:par.find('=')]
    if par.find('[') != -1:
        par = par[:par.find('[')]
    return  par.strip()

def getParameterSetByVersion(v):
    pset = []
    base_dir = '/home/tixu/software/mysql-doc-online/MySQL-Parameter-List-All - XXX.csv'
    ppath = base_dir.replace('XXX', v)

    f = open(ppath, 'rb')
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        p = norm(row[0])
        pset.append(p)
    return pset      


def getVersionPSet(vpre):
    vset = []
    vdict = getReleaseDict()
    if vpre == '4.1':
        for v in vdict:
            if v.startswith('4') or v.startswith('3'):
                vset.append(v)
    else:
        for v in vdict:
            if v.startswith(vpre):
                vset.append(v)
    #print vset
    vpset  = getParameterSetByVersion(vpre)
    vpdict = {}
    for v in vset:
        vpdict[v] = getParameterSetByVersion(vpre)
    #print len(vpdict)
    pset = []
    base_dir = '/home/tixu/software/mysql-doc-online/' + vpre + '/'
    mplist   = os.listdir(base_dir)
    for mp in mplist:
        mppath = base_dir + mp
        f = open(mppath)
        xml = f.read()
        f.close()
        doc = fromstring(xml)
        for item in doc.find_class('listitem'):
            #get the option name
            opname = None
            for pb in item.iter('p'):
                for option in pb.find_class('option'):
                    opname = norm(option.text_content())
                    break
                if opname == None:
                    for option in pb.find_class('literal'):
                        opname = norm(option.text_content())
                        break
                break
            if opname != None:
                if opname not in vpset:
                    continue
                else:
                    if opname not in pset:
                        pset.append(opname)
            else: 
                continue
            #Here we have a opname
            itxt = item.text_content()
            #get added version number
            addVersion = getVersionFromItem(itxt, 'added in')
            if len(addVersion) > 0:
                if addVersion in vset:
                    idx = vset.index(addVersion)
                    #print 'Adding', opname, addVersion, idx
                    for v in range(idx+1, len(vset)):
                        if opname in vpdict[vset[v]]:
                            vpdict[vset[v]].remove(opname)
            #get removed version number
            rmvVersion = getVersionFromItem(itxt, 'removed in')
            if len(rmvVersion) > 0:
                if rmvVersion in vset:
                    idx = vset.index(rmvVersion)
                    #print 'Removing', opname, rmvVersion, idx
                    for v in range(0, idx+1):
                        if opname in vpdict[vset[v]]:
                            vpdict[vset[v]].remove(opname)

    for i in range(0, len(vset)):
        print vset[i], len(vpdict[vset[i]])
        #put into a global data structure
        all_versions.append(vset[i])
        all_version_pset[vset[i]] = vpdict[vset[i]]
    #print 'pset', len(pset)
    

def getAllParameterDesc(page_dir):   
    option_list = []
    option_desc = {}
    """
    Step 1. Collect all the paraemters
    This is used for filter out incorrect parsing results
    """
    flist = os.listdir(page_dir)
    for fp in flist:
        #print path + fp
        opl = getParameterList(page_dir + fp)
        for o in opl:
            if o not in option_list:
                option_list.append(o)
    print 'Number of options', len(option_list)
    """
    Step 2. Get all the description 
    """
    for fp in flist:
        opdesc = getParameterDesc(page_dir + fp, option_list)
        for opd in opdesc:
            if opd not in option_desc:
                option_desc[opd] = opdesc[opd]
            else:
                if option_desc[opd].find(opdesc[opd]) == -1:
                    option_desc[opd] = opdesc[opd] + ' ' + option_desc[opd]
            option_desc[opd] = option_desc[opd].replace('\n', ' ').replace('-', '')
    print len(option_desc) 
    """
    Step 3. print to file
    """
    for op in option_desc:
        desc = option_desc[op]
        f = open('/home/tixu/test/' + op, 'wb')
        desc = desc.encode('utf-8')
        f.write(desc)
        f.close()


def getParameterList(path):
    f = open(path)
    xml = f.read()
    f.close()
    doc = fromstring(xml)
    oplist = []
    for table in doc.find_class('table-contents'):
        for tbody in table.iter('tbody'):
            for tr in tbody.iter('tr'):
                for td in tr.iter('td'):
                    opname = td.text_content()
                    if opname.find(':') != -1:
                        opname = opname[opname.find(':')+1:]
                    opname = opname.strip()
                    if opname not in oplist:
                        oplist.append(opname)
                    break
    return oplist  
 
def getParameterDesc(path, oplist):
    f = open(path)
    xml = f.read()
    f.close()
    doc = fromstring(xml)
    opdesc = {}
    for item in doc.find_class('listitem'):
        #get the option name
        opname = None
        for pb in item.iter('p'):
            for option in pb.find_class('option'):
                opname = norm(option.text_content())
                break
            if opname == None:
                for option in pb.find_class('literal'):
                    opname = norm(option.text_content())
                    break
                break
        if opname in oplist:
            #we want to skip the informaltable
            itxt = ''
            for p in item.iter('p'):
                itxt = p.text_content().strip() + ' '
            if opname in opdesc:
                if opdesc[opname].find(itxt) == -1:
                    opdesc[opname] = opdesc[opname] + ' ' + itxt
            else:
                opdesc[opname] = itxt
    return opdesc 


def getReleaseDict():
    vs = []
    f = open('mysql-release-in-order')
    for v in f:
        vs.append(v.strip())
    return vs

def getAllPageNames():
    pn = []
    base_dir = '/home/tixu/software/mysql-doc-online/'
    xl = os.listdir(base_dir) 
    for x in xl:
        if os.path.isdir(base_dir+x):
            xdir = base_dir+x
            mpl = os.listdir(xdir)
            for mp in mpl:
                if mp not in pn:
                    pn.append(mp)
    for p in pn:
        print p    

def getAllVersions():
    vset = []
    base_dir = '/home/tixu/software/mysql-doc-online/'
    xl = os.listdir(base_dir) 
    for x in xl:
        if os.path.isdir(base_dir+x):
            xdir = base_dir+x
            mpl = os.listdir(xdir)
            for mp in mpl:
                vs = getVersions(xdir + '/' + mp)
                for v in vs:
                    if v not in vset:
                        vset.append(v)
    vdict = getReleaseDict()
    for v in vset:
        if v not in vdict:
            print v
    print len(vset)
    return vset

"""
Get the parameters associated with 'add' and 'remove'
"""
def getVersions(path):
    vset = []
    adds = getVersionsHTML(path, 'added in')
    rmvs = getVersionsHTML(path, 'removed in')
    for p in adds:
        if p not in vset:
            vset.append(p)
    for p in rmvs:
        if p not in vset:
            vset.append(p)
    #print len(vset)
    #for v in vset:
    #    print v
    return vset

"""
Do the real work by parsing the html page
"""
def getVersionsHTML(path, prefix):
    f = open(path)
    xml = f.read()
    f.close()
    doc = fromstring(xml)
    
    versions = []
    for item in doc.find_class('listitem'):
        alltxt = item.text_content()
        addidx = alltxt.find(prefix)
        if addidx != -1:
            addtxt = alltxt[addidx+len(prefix):].strip()
            xtxt = addtxt
            if addtxt.startswith('a future'):
                continue

            if addtxt.startswith('MySQL'):
                addtxt = addtxt.replace('MySQL', '')
            addtxt = addtxt.replace('version', '')
            addtxt = addtxt.strip()
            if addtxt.find(' ') != -1:
                addtxt = addtxt[:addtxt.find(' ')].strip()
            if addtxt.find('\n') != -1:
                addtxt = addtxt[:addtxt.find('\n')]
            if addtxt.endswith('.'):
                addtxt = addtxt[:-1]
            elif addtxt.endswith(','):
                addtxt = addtxt[:-1]
            #print addtxt
            if addtxt == 'Cluster' or addtxt == 'these' or addtxt == 'a':
                continue
            
            if addtxt == '5.5' or addtxt == '5.6' or addtxt == '5.1' or addtxt == '4.1':
                addtxt = addtxt + '.0'
            if addtxt == 'a':
                print '======>', addtxt
                print '------>', prefix, xtxt
            if addtxt not in versions:
                versions.append(addtxt)
    #print len(versions)
    return versions 


def getVersionFromItem(item_text, prefix):
    addidx = item_text.find(prefix)
    if addidx != -1:
        addtxt = item_text[addidx+len(prefix):].strip()
        xtxt = addtxt
        if addtxt.startswith('a future'):
            return ''

        if addtxt.startswith('MySQL'):
            addtxt = addtxt.replace('MySQL', '')
        addtxt = addtxt.replace('version', '')
        addtxt = addtxt.strip()
        if addtxt.find(' ') != -1:
            addtxt = addtxt[:addtxt.find(' ')].strip()
        if addtxt.find('\n') != -1:
            addtxt = addtxt[:addtxt.find('\n')]
        if addtxt.endswith('.'):
            addtxt = addtxt[:-1]
        elif addtxt.endswith(','):
            addtxt = addtxt[:-1]
        #print addtxt
        if addtxt == 'Cluster' or addtxt == 'these' or addtxt == 'a':
            return ''
        if addtxt == '5.5' or addtxt == '5.6' or addtxt == '5.1' or addtxt == '4.1':
            addtxt = addtxt + '.0'
        return addtxt
    else:
        return ''
   

def downloadManPages(vid):
    entry = '/home/tixu/software/mysql-doc-online/server-system-variables-' + vid + '.html'
    bsurl = 'http://dev.mysql.com/doc/refman/' + vid + '/en/'
    ls = getLinks(entry, bsurl)
    
    dirp = '/home/tixu/software/mysql-doc-online/' + vid
    os.system('mkdir ' + dirp)
    for l in ls:
        os.system('wget -O ' + dirp + '/' + l[l.rfind('/'):] + ' ' + l)

def getLinks(path, base_url):
    f = open(path)
    xml = f.read()
    f.close()
    doc = fromstring(xml)
    doc.make_links_absolute(base_url)
    
    links = []
    for table in doc.find_class('table-contents'):
        for tr in table.iter('tr'):
            for link in tr.find_class('link'):
                for url in link.iterlinks():
                    page = url[2][:url[2].find('#')]
                    if page not in links:
                        links.append(page)
    print len(links)
    return links
              
"""
def getAllParameters(path):
    f = open(path, 'rb')
    reader = csv.reader(f, delimiter=',')
    pset = [] 
    for row in reader:
        p = row[0]
        if p not in pset:
            pset.append(p)
    return pset
"""

def psetDiff(old_set, new_set):
    diff_set = []
    for p in new_set:
        if p not in old_set:
            #print '+', p
            diff_set.append('+,' + p)
    for p in old_set:
        if p not in new_set:
            #print '-', p
            diff_set.append('-,' + p)
    return diff_set


def releaseDate(path):
    f = open(path, 'rb')
    for line in f:
        if line.find('Enterprise') != -1:
            continue
        if line.find('Community Server') != -1:
            line = line.replace('Community Server', '')
        line = line[line.find('in')+len('in'):].strip()
        line = line[line.find(' '):].strip()
        line = line.replace(' (', '\",')
        line = line.replace(')', '')
        print '\"'+line 

"""
Get the parameter difference
"""
def psetDiff(old_set, new_set):
    diff_set = []
    for p in new_set:
        if p not in old_set:
            #print '+', p
            diff_set.append('+,' + p)
    for p in old_set:
        if p not in new_set:
            #print '-', p
            diff_set.append('-,' + p)
    return diff_set



getVersionPSet('5.7')
getVersionPSet('5.6')
getVersionPSet('5.5')
getVersionPSet('5.1')
getVersionPSet('5.0')
getVersionPSet('4.1')


print len(all_versions)
print len(all_version_pset)

#for v in all_versions:
#    print v

f = open('/home/tixu/Music/all_v', 'r')
fst = True
prev_pset = []
for line in f:
    v = line[:line.find(' ')].strip()
    curr_pset = all_version_pset[v]
    ds = psetDiff(prev_pset, curr_pset)
    for d in ds:
        print d + "," + v
    prev_pset = curr_pset
f.close()

#getAllVersions()

#getLinks('4.1')
#getLinks('5.0')
#getLinks('5.5')
#getLinks('5.6')
#getLinks('5.7')

#releaseDate('mysql-release-date')

#getAllParameterDesc('/home/tixu/software/mysql-doc-online/5.6/')
#getParameterDesc('/home/tixu/software/mysql-doc-online/5.6/innodb-parameters.html')

#getVersions('/home/tixu/software/mysql-doc-online/'+'server-system-variables-4.1.html')
#getVersions('/home/tixu/software/mysql-doc-online/'+'server-system-variables-5.0.html')
#getVersions('/home/tixu/software/mysql-doc-online/'+'server-system-variables-5.1.html')
#getVersions('/home/tixu/software/mysql-doc-online/'+'server-system-variables-5.5.html')
#getVersions('/home/tixu/software/mysql-doc-online/'+'server-system-variables-5.6.html')
#getVersions('/home/tixu/software/mysql-doc-online/'+'server-system-variables-5.7.html')

#s1 = getAllParameters('/home/tixu/software/mysql-doc-online/'+'MySQL-Parameter-List-All - 5.6.csv')
#s2 = getAllParameters('/home/tixu/software/mysql-doc-online/'+'MySQL-Parameter-List-All - 5.7.csv')
#ds = psetDiff(s1, s2)
#for d in ds:
#    print d
