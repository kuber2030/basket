import json
import re

import requests
from lxml import etree
import notion
import logging

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[96m',  # Cyan
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[1;91m'  # Bold Red
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        # 这里我们手动组合每个部分并设置颜色
        formatted_msg = str(record.msg) % record.args
        formatted_message = f"{log_color}{self.formatTime(record)} - {record.name} - {record.levelname} - {formatted_msg}{self.RESET}"
        return formatted_message

handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 配置日志记录器
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(handler)
# 防止日志传播到根 logger，避免重复输出
logger.propagate = False
notion_children = []
"""
是否是目录
"""
def is_toc(p_node):
    style = p_node.get("style")
    if not style:
        return False, 0
    # print(style)
    match_obj = re.fullmatch("margin-left:(?:40|80|120|160|200)px;", style)
    if match_obj:
        margin_left = re.findall("margin-left:(\d+)px;", style,  re.S)
        return True, int(int(margin_left[0]) / 40)
    return False, 0


def visit_p(p_node:etree._Element):
    isToc, toc_levle = is_toc(p_node)
    if isToc:
        print(f"{toc_levle}级别标题:", p_node.xpath("a")[0].text)
        return
    # 富文本
    rich_texts = list()
    for p in p_node.getchildren():
        visit(p, rich_texts)
    # 富文本段落
    notion.append_paragraph(None, notion_children, rich_texts=rich_texts)

def visit(node: etree._Element, rich_texts:list):
    if node.tag == 'img':
        logger.debug('这是一张图片 %s', node.get("src"))
        notion.append_image(node.get("src"), notion_children)
    tail = ''
    if node.tail is not None:
        tail = node.tail
    if node.tag == 'span':
        if node.getchildren() is not None:
            children = node.getchildren()
            for child in children:
                if child.tag == 'strong':
                    logger.debug("这是一段加粗标签 %s", child.text)
                    notion.append_richtext(child.text + tail, False, 'red', False, rich_texts)
    if node.tag == 'strong':
        print("这是一段加粗文本", node.text, end='')
        notion.append_richtext(node.text + tail, True, None, False, rich_texts)
    if node.tail is not None:
        print(node.tail,  end='')
    return

def get_spans_text(span_nodes):
    spans = []
    for span in span_nodes:
        if span.text is not None:
            spans.append(span.text)
    return spans

def parse_article_title(element :etree._Element):
    article_node = element.xpath("//title")
    if article_node:
        return article_node[0].text.removesuffix("-CSDN博客")


def visit_blockquote(node: etree._Element):
    rich_texts = list()
    for b in node.getchildren():
        if b.tag == 'p':
            visit_p(b, rich_texts)
    # 富文本引用
    notion.append_paragraph(None, notion_children, rich_texts=rich_texts)


if __name__ == '__main__':
    # response = requests.get("https://kangll.blog.csdn.net/article/details/133607135")
    response = requests.get("https://kangll.blog.csdn.net/article/details/135519763")
    logger.debug("html： \n %s", response.text)
    html: etree._Element = etree.HTML(response.text)
    content_node = html.xpath('//div[@class="blog-content-box"]')  # type: list[etree._Element]
    title_article = parse_article_title(content_node[0])
    logger.debug("extract title success from html body: %s", title_article)
    article_node = content_node[0].xpath('//div[@id="content_views"]')
    children = article_node[0].getchildren()  # type: list[etree._Element]
    for child in children:
        # print(child, child.tag)
        if child.tag == 'img':
            logger.debug('这是一张图片: %s', child.attrib("src"))
            notion.append_image(child.attrib("src"), notion_children)
        if child.tag == 'p':
            if len(child.getchildren()) > 0:
                visit_p(child)
            elif child.text is not None:
                logger.debug("这是一段段落：%s", child.text)
                notion.append_paragraph(child.text, notion_children)
        if child.tag == 'blockquote':
            visit_blockquote(child)
        if child.tag == 'h1':
            headings = get_spans_text(child.xpath('span'))
            logger.debug("这是一级标题：%s", headings)
            if len(headings) > 0:
                notion.append_heading(headings[0], 1, notion_children)
        if child.tag == 'h2':
            headings = get_spans_text(child.xpath('span'))
            logger.debug("这是二级标题：%s", get_spans_text(child.xpath('span')))
            if len(headings) > 0:
                notion.append_heading(headings[0], 2, notion_children)
        if child.tag == 'h3':
            headings = get_spans_text(child.xpath('span'))
            logger.debug("这是三级标题：%s", get_spans_text(child.xpath('span')))
            if len(headings) > 0:
                notion.append_heading(headings[0], 1, notion_children)
        if child.tag == 'h4':
            headings = get_spans_text(child.xpath('span'))
            # TODO NOTION 不支持4级标题
            logger.debug("这是四级标题：%s", get_spans_text(child.xpath('span')))
            if len(headings) > 0:
                notion.append_heading(headings[0], 2, notion_children)
        if child.tag == 'h5':
            headings = get_spans_text(child.xpath('span'))
            logger.debug("这是五级标题：%s", get_spans_text(child.xpath('span')))
            if len(headings) > 0:
                notion.append_heading(headings[0], 3, notion_children)

    client = notion.Client("secret_TFChRbHM6JBd7zd41OpgfXWkGRxA8PbR3cI8g51AQ8g")
    json.dumps(notion_children)
    # resp = client.create_page(title_article, page_id="0351ec24-452c-472c-8183-2be67af3720b", children=notion_children)
    # print(resp.text)
