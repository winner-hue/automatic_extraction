import json
import re
import numpy as np
from lxml.html import etree
from html import unescape

from ae.defaults import DEFAULT_IMAGES_EXCEPT_FLAG
from ae.utils import iter_node, pad_host_for_images, config, get_high_weight_keyword_pattern


class ContentExtract:
    def __init__(self, content_tag='p'):
        """

        :param content_tag: 正文内容在哪个标签里面
        """
        self.content_tag = content_tag
        self.node_info = {}
        self.high_weight_keyword_pattern = get_high_weight_keyword_pattern()
        self.punctuation = set('''！，。？、；：“”‘’《》%（）,.?:;'"!%()''')  # 常见的中英文标点符号
        self.element_text_cache = {}

    def extract(self, selector, host='', body_xpath='', with_body_html=False):
        body_xpath = body_xpath or config.get('body', {}).get('xpath', '')
        if body_xpath:
            body = selector.xpath(body_xpath)[0]
        else:
            body = selector.xpath('//body')[0]
        body = self.remove_list_relevant(body)
        for node in iter_node(body):
            density_info = self.calc_text_density(node)
            node_hash = hash(node)
            text_density = density_info['density']
            ti_text = density_info['ti_text']
            text_tag_count = self.count_text_tag(node, tag='p')
            sbdi = self.calc_sbdi(ti_text, density_info['ti'], density_info['lti'])
            images_list = node.xpath('.//img/@src')
            images_list = self.remove_img(images_list)
            host = host or config.get('host', '')
            if host:
                images_list = [pad_host_for_images(host, url) for url in images_list]
            node_info = {'ti': density_info['ti'],
                         'lti': density_info['lti'],
                         'tgi': density_info['tgi'],
                         'ltgi': density_info['ltgi'],
                         'node': node,
                         'body': body,
                         'density': text_density,
                         'text': ti_text,
                         'images': images_list,
                         'text_tag_count': text_tag_count,
                         'sbdi': sbdi}
            if with_body_html or config.get('with_body_html', False):
                body_source_code = unescape(etree.tostring(node, encoding='utf-8').decode())
                node_info['body_html'] = body_source_code
            self.node_info[node_hash] = node_info
        self.calc_new_score()
        result = sorted(self.node_info.items(), key=lambda x: x[1]['score'], reverse=True)
        return result

    def count_text_tag(self, element, tag='p'):
        return len(element.xpath(f'.//{tag}'))

    def get_all_text_of_element(self, element_list):
        if not isinstance(element_list, list):
            element_list = [element_list]

        text_list = []
        for element in element_list:
            element_flag = element.getroottree().getpath(element)
            if element_flag in self.element_text_cache:  # 直接读取缓存的数据，而不是再重复提取一次
                text_list = self.element_text_cache[element_flag]
            else:
                element_text_list = []
                for text in element.xpath('.//text()'):
                    text = text.strip()
                    if not text:
                        continue
                    clear_text = re.sub(' +', ' ', text, flags=re.S)
                    element_text_list.append(clear_text.replace('\n', ''))
                self.element_text_cache[element_flag] = element_text_list
                text_list.extend(element_text_list)
        return text_list

    def calc_text_density(self, element):
        """
        根据公式：
               Ti - LTi
        TDi = -----------
              TGi - LTGi
        Ti:节点 i 的字符串字数
        LTi：节点 i 的带链接的字符串字数
        TGi：节点 i 的标签数
        LTGi：节点 i 的带连接的标签数
        :return:

        原本gne的计算方式，如果节点 i 都是带链接的标签，会导致分母很小，进而增大文本密度
        故修改计算方式为：
                         Ti /(tgi + 1)
                 TDi = -------------------
                        (lti/(ltgi+1))+1

        另外在计算文本密度时，detail 页面中的相关详情簇等会对正文的提取有影响，故先将其剔除
        """
        ti_text = '\n'.join(self.get_all_text_of_element(element))
        ti = len(ti_text)
        ti = self.increase_tag_weight(ti, element)
        lti = len(''.join(self.get_all_text_of_element(element.xpath('.//a'))))
        tgi = len(element.xpath('.//*'))
        ltgi = len(element.xpath('.//a'))
        if (tgi - ltgi) == 0:
            return {'density': 0, 'ti_text': ti_text, 'ti': ti, 'lti': lti, 'tgi': tgi, 'ltgi': ltgi}
        density = (ti / (tgi + 1)) / ((lti / (ltgi + 1)) + 1)
        if tgi <= 2:
            density = density / 2
        return {'density': density, 'ti_text': ti_text, 'ti': ti, 'lti': lti, 'tgi': tgi, 'ltgi': ltgi}

    def increase_tag_weight(self, ti, element):
        tag_class = element.get('class', '')
        if self.high_weight_keyword_pattern.search(tag_class):
            return 2 * ti
        return ti

    def calc_sbdi(self, text, ti, lti):
        """
                Ti - LTi
        SbDi = --------------
                 Sbi + 1

        SbDi: 符号密度
        Sbi：符号数量

        :return:
        """
        sbi = self.count_punctuation_num(text)
        # 修改计算方式为：
        sbdi = (ti - lti) / (sbi + 1)
        return sbdi or 1  # sbdi 不能为0，否则会导致求对数时报错。

    def count_punctuation_num(self, text):
        count = 0
        for char in text:
            if char in self.punctuation:
                count += 1
        return count

    def calc_new_score(self):
        """
        score = 1 * ndi * log10(text_tag_count + 2) * log(sbdi)

        1：在论文里面，这里使用的是 log(std)，但是每一个密度都乘以相同的对数，他们的相对大小是不会改变的，所以我们没有必要计算
        ndi：节点 i 的文本密度
        text_tag_count: 正文所在标签数。例如正文在<p></p>标签里面，这里就是 p 标签数，如果正文在<div></div>标签，这里就是 div 标签数
        sbdi：节点 i 的符号密度
        :param std:
        :return:
        """
        for node_hash, node_info in self.node_info.items():
            score = node_info['density'] * np.log10(node_info['text_tag_count'] + 2) * np.log(
                node_info['sbdi'])
            self.node_info[node_hash]['score'] = score

    def remove_list_relevant(self, element):
        """
        删除噪音节点， 判断方式：

                    a_tags_text
        radio = -------------------
                    all_tags_text

        a_tags_text: a 标签下字符的总量
        all_tags_text: 当前标签下的字符总量
        radio: a 标签字符总量占 当前标签字符总量的比率

        :param element:
        :return:
        """
        for node in iter_node(element):
            if "div".__eq__(node.tag):
                all_tags_text = len(''.join([value.strip() for value in node.xpath(".//text()")]))
                a_tags_text = len(''.join([value.strip() for value in node.xpath(".//a//text()")]))
                if all_tags_text:
                    if a_tags_text / all_tags_text > 0.8:
                        temp_node = node.getparent()
                        if temp_node is not None:
                            temp_node.remove(node)
        else:
            return element

    def remove_img(self, image_list):
        result_list = []
        flag = False
        for img in image_list:
            for except_flag in DEFAULT_IMAGES_EXCEPT_FLAG:
                if img.__contains__(except_flag):
                    flag = True
                    break
            if not flag:
                result_list.append(img)
        return result_list
