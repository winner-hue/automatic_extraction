import re
from ae.utils import config
from lxml.html import HtmlElement
from ae.defaults import SOURCE_PATTERN


class SourceExtract:
    def __init__(self):
        self.source_pattern = SOURCE_PATTERN

    def extractor(self, element: HtmlElement, source_xpath=''):
        source_xpath = source_xpath or config.get('author', {}).get('xpath')
        if source_xpath:
            author = ''.join(element.xpath(source_xpath))
            return author
        text = ''.join(element.xpath('.//text()'))
        for pattern in self.source_pattern:
            author_obj = re.search(pattern, text)
            if author_obj:
                return author_obj.group(1)
        return ''
