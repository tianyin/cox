import os
import urllib2
from lxml import etree
from lxml import html

def delete(string):
    index = 0
    while string.find('<', index) > -1 :
        start_index = string.find('<', index)
        end_index = string.find('>', start_index + 1)
        second_index = string.find('<', start_index + 1)
        if end_index == -1:
            break
        if second_index == -1 or second_index > end_index:
            string = string.replace(string[start_index:end_index+1], ' ')
        if second_index > -1 and second_index < end_index:
            string = string.replace(string[second_index:end_index+1], ' ')
            index = start_index

    string = string.replace('&lt;', '< ')
    string = string.replace('&gt;', ' >')
    return string

def parse():
    mod_name = open('mod.list', 'r')
    total_count = 0

    cur_path = os.getcwd()
    os.mkdir(cur_path + '/parameters')
    mod_path = cur_path + '/parameters' 

    for mod in mod_name:
        mod = mod.replace('\n', '')
        url = "http://httpd.apache.org/docs/current/mod/" + mod + ".html"
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req)
        content = resp.read()
        html = etree.HTML(content)

        directives = html.xpath("//div[@class='directive-section']")

        for directive in directives:
            os.chdir(mod_path)
            name = directive.find("h2")
            print name[0].text
            out = open(name[0].text, 'w')
            out.write(name[0].text)
            out.write('\n\n')

            table = directive.find("table")
            for index in range(len(table)):
                out.write((table[index].find("th"))[0].text)
                out.write(' ')
                out.write(delete(etree.tostring((table[index].find("td")))) + '\n')

            out.write('\n')
            out.write(delete(etree.tostring(directive)[etree.tostring(directive).find('<p>'):len(etree.tostring(directive))-1]))

        total_count += 1
        os.chdir(cur_path)

    print 'All', total_count, 'modules have been parsed.'

if __name__ == "__main__":
    parse()
