import re

from lxml.html import HtmlElement

from ae.defaults import TITLE_SPLIT_CHAR_PATTERN
from ae.utils import config, get_longest_common_sub_string


class TitleExtract:
    def extract_by_xpath(self, element, title_xpath):
        if title_xpath:
            title_list = element.xpath(title_xpath)
            if title_list:
                return title_list[0]
            else:
                return ''
        return ''

    def extract_by_title(self, element):
        title_list = element.xpath('//title/text()')
        if not title_list:
            return ''
        title = re.split(TITLE_SPLIT_CHAR_PATTERN, title_list[0])
        if title:
            if len(title[0]) >= 4:
                return title[0]
            return title_list[0]
        else:
            return ''

    def extract_by_htag(self, element, content_element, content):
        """
        提取标题

        找到离content最近的标题：即兄弟节点和其父节点的兄弟节点，并且其父节点不是body

        :param element:
        :param content_element:
        :param content:
        :return:
        """
        title_result = ''
        preceding_node = content_element.xpath(".//preceding-sibling::*")
        for node in preceding_node:
            text = "".join(node.xpath(".//text()"))
            loc = get_longest_common_sub_string(text, content)
            if len(loc) > len(title_result):
                title_result = loc
        self_parent = content_element.getparent()
        if not "body".__eq__(self_parent.tag):
            self_parent_preceding_node = self_parent.xpath(".//preceding-sibling::*")
            for node in self_parent_preceding_node:
                text = "".join(node.xpath(".//text()"))
                loc = get_longest_common_sub_string(text, content)
                if len(loc) > len(title_result):
                    title_result = loc
        return title_result

    def extract_by_htag_and_title(self, element: HtmlElement) -> str:
        """
        一般来说，我们可以认为 title 中包含新闻标题，但是可能也含有其他文字，例如：
        GNE 成为全球最好的新闻提取模块-今日头条
        新华网：GNE 成为全球最好的新闻提取模块

        同时，新闻的某个 <h>标签中也会包含这个新闻标题。

        因此，通过 h 标签与 title 的文字双向匹配，找到最适合作为新闻标题的字符串。
        但是，需要考虑到 title 与 h 标签中的文字可能均含有特殊符号，因此，不能直接通过
        判断 h 标签中的文字是否在 title 中来判断，这里需要中最长公共子串。
        :param element:
        :return:
        """
        h_tag_texts_list = element.xpath(
            '(//div[@class="title" or @class="tile"]//text() | //h1//text() | //h2//text() | //h3//text() | //h4//text() | //h5//text())')
        title_text = ''.join(element.xpath('//title/text()'))
        news_title = ''
        for h_tag_text in h_tag_texts_list:
            lcs = get_longest_common_sub_string(title_text, h_tag_text)
            if len(lcs) > len(news_title) and (len(h_tag_text) / (len(title_text) + 1) > 0.5):
                news_title = lcs
        return news_title if len(news_title) > 4 else ''

    def extract(self, content, content_element: HtmlElement, element: HtmlElement, title_xpath: str = '') -> str:
        title_xpath = title_xpath or config.get('title', {}).get('xpath')
        title = (self.extract_by_xpath(element, title_xpath)
                 or self.extract_by_htag_and_title(element)
                 or self.extract_by_htag(element, content_element, content)
                 or self.extract_by_title(element)
                 )
        return title.strip()
