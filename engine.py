import logging

from lxml import etree

logger = logging.getLogger(__name__)


class ElementNode:
    def __init__(self, id=None, tag=None, children=None, html_element=None):
        self.id = id
        self.tag = tag
        self.children = children
        self.html_element = html_element


class Text:
    def __init__(self, text):
        self.text = text


class HeadingElementNode(ElementNode):
    def __init__(self, text: str, level: int, color=None, **kwargs):
        super().__init__(**kwargs)
        self.level = level


class ImageElementNode(ElementNode):
    def __init__(self, src: str, **kwargs):
        super().__init__(**kwargs)
        self.src = src


class RichText(Text):
    def __init__(self, bold=None, italic=None, strikethrough=None, underline=None, code=None, color=None, **kwargs):
        super().__init__(**kwargs)
        self.bold = bold,
        self.italic = italic
        self.strikethrough = strikethrough
        self.underline = underline
        self.code = code
        self.color = color


class PElementNode(ElementNode):
    def __init__(self, text: Text = None, rich_texts: list[RichText] = None, **kwargs):
        super().__init__(**kwargs)
        self.text = Text
        self.rich_texts = rich_texts


class CalloutElement(ElementNode):
    def __init__(self, text: Text = None, rich_texts: list[RichText] = None, **kwargs):
        super().__init__(**kwargs)
        self.text = Text
        self.rich_texts = rich_texts


class Engine:

    def __init__(self, website_type: str, html_text: str):
        assert website_type
        assert html_text
        self.html_text = html_text
        self.website_type = website_type

    def __tree_build__(self):
        pass

    def get_Elements(self):
        pass


class CSDNEngine(Engine):

    def __init__(self, website_type, html_text, title=None):
        super().__init__(website_type, html_text)
        html: etree._Element = etree.HTML(self.html_text)
        content_node = html.xpath('//div[@class="blog-content-box"]')  # type: list[etree._Element]
        if not title:
            self.title = self.parse_article_title(content_node[0])

        self.article_content = content_node[0].xpath('//div[@id="content_views"]')[0]
        self.elements = []
        assert self.article_content is not None
        self.parse_elements()

    def parse_article_title(self, element: etree._Element):
        article_node = element.xpath("//title")
        if article_node:
            return article_node[0].text.removesuffix("-CSDN博客")

    def parse_elements(self):
        children = self.article_content.getchildren()  # type: list[etree._Element]
        for child in children:
            element = self.traverse(child)
            if element:
                self.elements.append(element)

    def traverse(self, child:etree._Element):
        if child.tag == 'img':
            image_src = child.attrib("src")
            logger.debug('解析到图片: %s', image_src)
            return ImageElementNode(image_src, tag="image", html_element=child)
        # if child.tag == 'p':
            # if len(child.getchildren()) > 0:
                # visit_p(child)
            # elif child.text is not None:
            #     logger.debug("这是一段段落：%s", child.text)
            #     notion.append_paragraph(child.text, notion_children)
        # if child.tag == 'blockquote':
            # visit_blockquote(child)
        if child.tag == 'h1' or child.tag == 'h2' or child.tag == 'h3' or child.tag == 'h4' or child.tag == 'h5':
            heading = child.find('span')
            return HeadingElementNode(heading.text, child.tag[-1], tag=child.tag, html_element=child) if heading is not None else None

    def get_Elements(self) -> list[ElementNode]:
        return self.elements
