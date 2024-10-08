import logging

from lxml import etree

logger = logging.getLogger(__name__)


class ElementNode:
    def __init__(self, id=None, tag=None, children: list = None, html_element=None):
        self.id = id
        self.tag = tag
        self.children = children
        self.html_element = html_element


class Text:
    def __init__(self, text:str):
        self.text = text

    def __str__(self):
        return self.text


class HeadingElementNode(ElementNode):
    def __init__(self, text: str, level: int, color=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.level = level


class ImageElementNode(ElementNode):
    def __init__(self, src: str, **kwargs):
        super().__init__(**kwargs)
        self.src = src


class RichText(ElementNode):
    def __init__(self, bold=None, italic=None, strikethrough=None, underline=None, code=None, color=None, **kwargs):
        super().__init__(**kwargs)
        self.bold = bold,
        self.italic = italic
        self.strikethrough = strikethrough
        self.underline = underline
        self.code = code
        self.color = color

class NestedElementNode(ElementNode):
    """
    嵌套元素内容
    """
    def __init__(self, text: str = None, **kwargs):
        super().__init__(**kwargs)
        self.text = text

class PElementNode(ElementNode):
    def __init__(self, text: str = None, **kwargs):
        super().__init__(**kwargs)
        self.text = text


class CalloutElement(ElementNode):
    def __init__(self, text: str = None, **kwargs):
        super().__init__(**kwargs)
        self.text = text

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

    @staticmethod
    def __has_children__(element):
        return element and len(element.getchildren()) > 0
    
    def traverse(self, element:etree._Element):
        if element is None:
            return None
        if element.tag == 'img':
            image_src = element.get("src")
            logger.debug('解析到图片: %s', image_src)
            return ImageElementNode(image_src, tag="image", html_element=element)
        if element.tag == 'p':
            pElementNode = PElementNode(element.text, children=[])
            if CSDNEngine.__has_children__(element):
                for child in element.getchildren():
                    logger.debug("这是一段段落：%s", child.text)
                    elementNdde = self.traverse(child) # type: ElementNode
                    pElementNode.children.append(elementNdde)
            return pElementNode
        if element.tag == 'blockquote':
            calloutElement = CalloutElement(text=element.text)
            # 肯定只会有一个子元素，没有标注套标注的情况
            calloutElement.children = [self.traverse(element.getchildren()[0])]
            return calloutElement
        if element.tag == 'h1' or element.tag == 'h2' or element.tag == 'h3' or element.tag == 'h4' or element.tag == 'h5':
            heading = element.find('span')
            return HeadingElementNode(heading.text, element.tag[-1], tag=element.tag, html_element=element) if heading is not None else None
        if element.tag == 'span':
            nestedElement = NestedElementNode(element.text, children=[])
            for child in element.getchildren():
                element_node = self.traverse(child)
                nestedElement.children.append(element_node) if element_node else None
            return nestedElement
        if element.tag == 'strong':
            if CSDNEngine.__has_children__(element):
                for child in element.getchildren():
                    element_node = self.traverse(child)
                    if isinstance(element_node, NestedElementNode):
                        # TODO 暂时只返回第一个，有多个实在不好处理
                        return element_node
            else:
                return RichText(element.text)
        if element.tail is not None and element.tail.strip() != "":
            return Text(element.tail)
    

    def get_Elements(self) -> list[ElementNode]:
        return self.elements
    


