import os
from lxml import etree
from io import StringIO, BytesIO

OUTPUT_DIR = './parameters/'

if not os.path.exists(OUTPUT_DIR):
   os.mkdir(OUTPUT_DIR) 

tree = etree.parse(open('./manuals/hdfs-default.xml'))
ppts = tree.xpath('//property')
for ppt in ppts:
    #name
    n = ppt.xpath('./name')
    for x in n: name = x.text.strip()
    #value
    v = ppt.xpath('./value')
    for y in v: value = y.text
    #desc
    d = ppt.xpath('./description')
    for z in d: desc = z.text
    #print
    #print name, value, desc
    pfname = OUTPUT_DIR + name
    pf = open(pfname, 'w')
    if value != None:
        pf.write(value.strip() + '\n')
    if desc != None:
        pf.write(desc.strip()  + '\n')
    pf.close()
