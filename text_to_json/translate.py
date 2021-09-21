import re

def get_dota_data_from_vpk(base_txt, ffile1, ffile2):
    this_string = ffile1.read().decode('utf8')
    alltext = re.finditer('"(.*?)".*?"(.*?)"', this_string)
    for i in alltext:
        name = i.group(1)
        if name not in base_txt:
            base_txt[name]={}
        base_txt[name]['中文'] = i.group(2)
    this_string = ffile2.read().decode('utf8')
    alltext = re.finditer('"(.*?)".*?"(.*?)"', this_string)
    for i in alltext:
        name = i.group(1)
        if name not in base_txt:
            base_txt[name]={}
        base_txt[name]['英文'] = i.group(2)