import datetime
import re
import dateparser
from ae.utils import config
from lxml.html import HtmlElement
from ae.defaults import DATETIME_PATTERN, PUBLISH_TIME_META


class TimeExtract:
    def __init__(self):
        self.time_pattern = DATETIME_PATTERN

    def resolve_time(self, publish_time):
        if isinstance(publish_time, str):
            publish_time = publish_time.replace("年", "-").replace("月", "-").replace("日", "-")
            temp_date = dateparser.parse(publish_time)
            temp_date = temp_date.strftime("%Y%m%d%H%M%S")
            return temp_date
        if isinstance(publish_time, list):
            result_temp_date = None
            for publish_time_temp in publish_time:
                publish_time_temp = publish_time_temp.replace("年", "-").replace("月", "-").replace("日", "")
                # 同时满足 \\d+年\\d+月\\d+日这种格式，并且满足\\d+年只有两位，则对其进行补充年份
                try:
                    try:
                        length = re.search("(\\d+)-", publish_time_temp).group(1)
                    except:
                        length = ''
                    if len(length) == 2 and re.search("\\d+-\\d+-\\d+", publish_time_temp):
                        _year = str(datetime.datetime.now().year)[0:2]
                        publish_time_temp = _year + publish_time_temp

                    temp_date = dateparser.parse(publish_time_temp)
                    if temp_date > datetime.datetime.now():
                        continue
                    if result_temp_date:
                        result_temp_date = result_temp_date if result_temp_date > temp_date else temp_date  # 取最大时间作为发布时间
                    else:
                        result_temp_date = temp_date
                except:
                    pass
            return result_temp_date.strftime("%Y%m%d%H%M%S")

    def extractor(self, content_element: HtmlElement, element: HtmlElement, publish_time_xpath: str = '') -> str:
        publish_time_xpath = publish_time_xpath or config.get('publish_time', {}).get('xpath')
        publish_time = (self.extract_from_user_xpath(publish_time_xpath, element)  # 用户指定的 Xpath 是第一优先级
                        or self.extract_from_meta(element)  # 第二优先级从 Meta 中提取
                        or self.extract_from_text(element))  # 最坏的情况从正文中提取
        try:
            publish_time = self.resolve_time(publish_time)
        except:
            return ''
        return publish_time

    def extract_from_user_xpath(self, publish_time_xpath: str, element: HtmlElement) -> str:
        if publish_time_xpath:
            publish_time = ''.join(element.xpath(publish_time_xpath))
            return publish_time
        return ''

    def extract_from_text(self, element: HtmlElement) -> list:
        time_list = []
        text = ''.join(element.xpath('.//text()'))
        for dt in self.time_pattern:
            dt_obj = re.search(dt, text)
            if dt_obj:
                time_list.append(dt_obj.group(1))
        else:
            return time_list

    def extract_from_meta(self, element: HtmlElement) -> list:
        """
        一些很规范的新闻网站，会把新闻的发布时间放在 META 中，因此应该优先检查 META 数据
        :param element: 网页源代码对应的Dom 树
        :return: str
        """
        publish_time_list = []
        for xpath in PUBLISH_TIME_META:
            publish_time = element.xpath(xpath)
            if publish_time:
                publish_time_list.append(''.join(publish_time))
        return publish_time_list
