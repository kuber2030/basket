import logging
import sys

from core import engine
import notion
import transformer
import core.html_loader as hl

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


html_loader = hl.HtmlLoader()
text = html_loader.get_html("https://mp.weixin.qq.com/s/dnlxCXgAxHsfyVNYTDsewA")
# text = html_loader.get_html("https://blog.csdn.net/MeituanTech/article/details/140197400")
# text = html_loader.mock_get_html("https://blog.csdn.net/MeituanTech/article/details/140197400", "./test/test10.html")
print(text)
# engine_impl = engine.Engine.get_engine("csdn")(text, title=None)
engine_impl = engine.Engine.get_engine("wx")(text, title=None)
pageid = client.create_page(engine_impl.title, None, page_id="12d8289df06980afa989fe9acf337c3e")
# pageid = "17c8289df06981f2a5c2da9e07df0a8e"

def create_block(pageid, elements):
    if elements is None:
        return
    assert len(engine_impl.get_Elements()) > 0
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
# 设置栈递归的最大深度
sys.setrecursionlimit(200000)
create_block(pageid, engine_impl.get_Elements())