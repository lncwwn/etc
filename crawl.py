#!/usr/bin/env python
# -*- encoding:  utf-8 -*-
# @Time    : 05/30/2019
# @Author  : nianchaoli@msn.cn
# @License : MIT

import requests
from lxml import html
import codecs

# store the urls to be crawled
url_list = []
# a basic province data
provinces = {
    u'北京市': '110000',
    u'天津市': '120000',
    u'河北省': '130000',
    u'山西省': '140000',
    u'内蒙古自治区': '150000',
    u'辽宁省': '210000',
    u'吉林省': '220000',
    u'黑龙江省': '230000',
    u'上海市': '310000',
    u'江苏省': '320000',
    u'浙江省': '330000',
    u'安徽省': '340000',
    u'福建省': '350000',
    u'江西省': '360000',
    u'山东省': '370000',
    u'河南省': '410000',
    u'湖北省': '420000',
    u'湖南省': '430000',
    u'广东省': '440000',
    u'广西壮族自治区': '450000',
    u'海南省': '460000',
    u'重庆市': '500000',
    u'四川省': '510000',
    u'贵州省': '520000',
    u'云南省': '530000',
    u'西藏自治区': '540000',
    u'陕西省': '610000',
    u'甘肃省': '620000',
    u'青海省': '630000',
    u'宁夏回族自治区': '640000',
    u'新疆维吾尔自治区': '650000'
}

version = '2018'
base_url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/%s/'%(version)

tsv_res = u'Source\tRevision\tCode\tName\n'
col_1 = 'stats'
col_2 = '201810'

def do_consume(url_obj):
    res = do_req(url_obj.get('url'), url_obj.get('depth'))
    do_parse(res)

def do_req(url, depth = 0):
    print 'crawling %s now...' % url
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        r.encoding = 'gbk'
        text = r.text.replace('charset=gb2312', 'charset=utf8')
        return {
            'doc': html.fromstring(text),
            'depth': depth
        }

def do_parse(res):
    """parses and get valid data from tree
    """
    doc = res.get('doc')
    depth = res.get('depth')
    # select all province nodes
    if depth < 1:
        _parse_provinces(doc, depth)
    elif depth < 2:
        _parse_cities(doc, depth)
    else:
        _parse_counties(doc, depth)

def _parse_provinces(doc, depth):
    """Parses html that includes provinces data
    """
    global tsv_res
    nodes = doc.xpath('//tr[@class="provincetr"]/td/a')
    for node in nodes:
        province_name = node.text_content()
        tsv_res += '%s\t%s\t%s\t%s\n'%(col_1, col_2, provinces.get(province_name), province_name)
        do_consume({
            'url': base_url + node.get('href'),
            'depth': depth + 1
        })

def _parse_cities(doc, depth):
    """Parse html that includes cities data
    """
    global tsv_res
    nodes = doc.xpath('//tr[@class="citytr"]/td/a')
    for node in nodes:
        i = nodes.index(node)
        text = node.text_content()
        if not i % 2:
            tsv_res += '%s\t%s\t%s\t'%(col_1, col_2, text[0:6])
        else:
            tsv_res += text + '\n'
            do_consume({
                'url': base_url + node.get('href'),
                'depth': depth + 1
            })

def _parse_counties(doc, depth):
    """Parse html that includes counties data
    """
    global tsv_res
    nodes = doc.xpath('//tr[@class="countytr"]/td')
    for node in nodes:
        i = nodes.index(node)
        text = node.text_content()
        if not i % 2:
            tsv_res += '%s\t%s\t%s\t'%(col_1, col_2, text[0:6])
        else:
            tsv_res += text + '\n'

def save_file(tsv_str):
    f = codecs.open('./201810.tsv', 'w', 'utf-8')
    f.write(tsv_str)
    f.close()

def do_others():
    global tsv_res
    others = {
        '710000': u'台湾省',
        '810000': u'香港特别行政区',
        '820000': u'澳门特别行政区'
    }
    for k, v in others.items():
        tsv_res += '%s\t%s\t%s\t%s\n'%(col_1, col_2, k, v)

def main(seed_url):
    """Crawls stats region data.
    """
    do_consume({
        'url': seed_url,
        'depth': 0
    })
    print 'crawls done'
    do_others()
    save_file(tsv_res)

if __name__ == '__main__':
    seed_url = base_url + 'index.html'
    main(seed_url)
