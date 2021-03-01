# automatic extraction

#### 安装

> pip install automatic_extraction

#### 使用

```python
from ae import AutomaticExtract
ae = AutomaticExtract()

import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}
url = "http://news.sdchina.com/show/4588837.html"
r = requests.get(url, headers=headers)
print(ae.extract(r.content.decode("utf-8"), host=url))
```

#### 参考

GeneralNewsExtractor   项目地址：https://github.com/kingname/GeneralNewsExtractor

GerapyAutoExtractor     项目地址：https://github.com/Gerapy/GerapyAutoExtractor

#### 原理

1. 去除噪音：

   为了方便正文的提取，首先将正文的噪音节点剔除，即列表簇 （灵感来自GerapyAutoExtractor列表页判断）

   判断方法：

   ​	 判断 div 标签下面 a 标签的数量， 若 a标签的文字数量/所有标签的文字数量 > 0.8， 则删除该节点

2. 提取内容：

   内容的提取修改了GNE的密度公式，将其改为：

   ```
                    Ti /(tgi + 1)
             TDi = ----------------
                   (lti/(ltgi+1))+1
             
             Ti:节点 i 的字符串字数
             LTi：节点 i 的带链接的字符串字数
             TGi：节点 i 的标签数
             LTGi：节点 i 的带连接的标签数
   ```

3. 提取标题

   标题的获取首先是根据GNE中webtitle和标题标签的比对，之后是修改了GNE的extract_by_htag方法，在其中通过正文标签节点的位置，来判断标题标签的大概位置，然后通过标题在正文的最长公共子串，来确定标题的内容

4. 提取时间

   在时间的提取上，引入了dateparser包，对正则匹配后的时间做出进一步的处理。此处将使用正则对全文内容进行时间匹配，并选取小于当前时间但最大的时间来作为发布时间

5. 提取作者、来源

   作者、来源的提取上面同GNE一样，只是改动了很少的正则

#### 备注

&emsp;本项目是在GeneralNewsExtractor项目上修改而来，项目基本结构同GNE相同，只是对其中的提取方法做了一些修改，在此由衷的感谢大佬开源GeneralNewsExtractor项目，欢迎大家对GNE star, fork

&emsp;本项目也参照了GerapyAutoExtractor 项目，非常欢迎大家对GerapyAutoExtractor  star, fork

&emsp;该项目不一定持续更新，所以希望大家更多关注GNE和GerapyAutoExtractor项目。但也希望大家star, fork

