from lxml import etree
from lxml.html import fromstring
from StringIO import StringIO

import csv 
import os
import sys

def get_text_from_html(htmlpath):
    """
    Simply get all the text from the html into a string
    """
    textstring = ''
    f = open(htmlpath)
    xml = f.read()
    f.close()
    doc = fromstring(xml)
    for section in doc.find_class('section'):
        secstring = section.text_content().encode('utf-8')
        #secstring = secstring.replace('\n', '')
        textstring += secstring
    return textstring

def normalize(raw_textstr):
    """
    If you print the text from get_text_from_html, it's not really organized into paragraph by the line breaker,
    let's normalize it in this function
    """
    norm_text = ''
    curr_para = ''
    
    while '\n' in raw_textstr:
        idx = raw_textstr.find('\n')

        line_content = raw_textstr[:idx].strip()
        if len(line_content) == 0:
            #this is a true line breaker
            norm_text += curr_para + '\n\n'
            curr_para = ''
        else:
            #not a true line breaker
            curr_para += line_content + ' '

        raw_textstr = raw_textstr[idx+1:]
    #end while
    
    print norm_text

if __name__ == "__main__":
    text = get_text_from_html(sys.argv[1])
    normalize(text)
