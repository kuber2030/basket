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

response = requests.get("https://kangll.blog.csdn.net/article/details/135519763")
text = ""
with open("./test/test.html", 'r', encoding='utf-8') as f:
    lines = f.readlines()
    text = "".join(lines)
csdnEngine = engine.CSDNEngine("csdn", text, title="测试engine")
assert len(csdnEngine.get_Elements()) > 0
# print(csdnEngine.get_Elements())

# createdPage = self.client.create_page(csdnEngine.title, None, page_id="0351ec24-452c-472c-8183-2be67af3720b",)
# print(createdPage.text)
# if createdPage.status_code != 200:
#     return
# pageid = createdPage.json().get("id")
pageid = "11a8289d-f069-81f0-a37b-fd8a492dc147"

def create_block(pageid, elements):
    if elements is None:
        return
    for element in elements:
        notionEle = transformer.transformElement(element)
        # TODO 暂时先过滤不支持的元素
        if not notionEle:
            continue
        # 这里约定，如果返回的是列表，则约定没有子元素了，不需要递归了
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