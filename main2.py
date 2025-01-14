import logging
import sys

import requests

import engine
import notion
import transformer

handler = logging.StreamHandler()

# 配置日志记录器
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(handler)
# 防止日志传播到根 logger，避免重复输出
logger.propagate = False

client = notion.Client("secret_TFChRbHM6JBd7zd41OpgfXWkGRxA8PbR3cI8g51AQ8g",
                       # proxy={"https": "https://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
                       )
headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Connection': 'keep-alive',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"'
}
response = requests.get("https://blog.csdn.net/yuzheh521/article/details/135452889", headers=headers)
text = response.text
print(text)
# with open("./test/test10.html", 'r', encoding='utf-8') as f:
#     lines = f.readlines()
#     text = "".join(lines)
csdnEngine = engine.CSDNEngine("csdn", text)
assert len(csdnEngine.get_Elements()) > 0
# print(csdnEngine.get_Elements())

# createdPage = client.create_page(csdnEngine.title, None, page_id="12d8289df06980afa989fe9acf337c3e",)
# print(createdPage.text)
# if createdPage.status_code != 200:
#     sys.exit(-1)
# pageid = createdPage.json().get("id")
pageid = "17b8289df06981139345c234d9d68536"

def create_block(pageid, elements):
    if elements is None:
        return
    for element in elements:
        notionEle = transformer.transformElement(element)
        # TODO 暂时先过滤不支持的元素
        if not notionEle:
            continue
        # 这里约定，如果返回的是列表，则约定没有子元素了，不需要递归了，目前只有<ul>和<ol>元素是这样的
        if isinstance(notionEle, list):
            for ele in notionEle:
                resp = client.append_block(pageid, [ele])
                if resp.status_code != 200:
                    logger.error("创建block失败 %s, %s", element, resp.text)
                    sys.exit(-1)
                else:
                    logger.debug(resp.text)
                    blockid = resp.json().get("results")[0].get("id")
        else:
            resp = client.append_block(pageid, [notionEle])
            if resp.status_code != 200:
                logger.error("创建block失败 %s, %s", element, resp.text)
                sys.exit(-1)
            else:
                logger.debug(resp.text)
                blockid = resp.json().get("results")[0].get("id")
                create_block(blockid, element.children)

create_block(pageid, csdnEngine.get_Elements())