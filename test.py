from ae import AutomaticExtract

ae = AutomaticExtract()

import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}
url = "http://news.sdchina.com/show/4588837.html"
r = requests.get(url, headers=headers)
print(ae.extract(r.content.decode("utf-8"), host=url))
