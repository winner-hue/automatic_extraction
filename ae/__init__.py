from ae.extraction.author_extract import AuthorExtract
from ae.extraction.content_extract import ContentExtract
from ae.extraction.list_page_extract import ListExtract
from ae.extraction.time_extract import TimeExtract
from ae.extraction.title_extract import TitleExtract
from ae.extraction.source_extract import SourceExtract
from .utils import pre_parse, remove_noise_node, config, html2element, normalize_text


class AutomaticExtract:
    def extract(self,
                html,
                title_xpath='',
                author_xpath='',
                publish_time_xpath='',
                host='',
                body_xpath='',
                source_xpath='',
                noise_node_list=None,
                with_body_html=False,
                auto_remove=True):
        # 对 HTML 进行预处理可能会破坏 HTML 原有的结构，导致根据原始 HTML 编写的 XPath 不可用
        # 因此，如果指定了 title_xpath/author_xpath/publish_time_xpath，那么需要先提取再进行
        # 预处理
        normal_html = normalize_text(html)
        element = html2element(normal_html)
        element = pre_parse(element)
        remove_noise_node(element, noise_node_list)
        author = AuthorExtract().extractor(element, author_xpath=author_xpath)
        source = SourceExtract().extractor(element, source_xpath=source_xpath)
        content = ContentExtract().extract(element,
                                           host=host,
                                           with_body_html=with_body_html,
                                           body_xpath=body_xpath)
        content_element = content[0][1]['node']
        title = TitleExtract().extract(content, content_element, element, title_xpath=title_xpath)
        publish_time = TimeExtract().extractor(content_element, element, publish_time_xpath=publish_time_xpath)

        result = {'title': title,
                  'author': author,
                  'source': source,
                  'publish_time': publish_time,
                  'content': content[0][1]['text'],
                  'images': content[0][1]['images']
                  }
        if with_body_html or config.get('with_body_html', False):
            result['body_html'] = content[0][1]['body_html']
        return result


class ListPageExtractor:
    def extract(self, html, feature):
        normalize_html = normalize_text(html)
        element = html2element(normalize_html)
        extractor = ListExtract()
        return extractor.extract(element, feature)
