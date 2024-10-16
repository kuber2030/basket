import logging
from lxml import etree

logger = logging.getLogger(__name__)


class ElementNode:
    def __init__(self, id=None, tag=None, children: list = None, html_element=None):
        self.id = id
        self.tag = tag
        self.children = children
        self.html_element = html_element


class PlainText:
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


class LinkElementNode(ElementNode):
    def __init__(self, href: str, text: str, **kwargs):
        super().__init__(**kwargs)
        self.href = href
        self.text = text


class RichText(ElementNode):
    def __init__(self, text, bold=False, italic=False, strikethrough=False, underline=False, code=False, color="default", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.bold = bold
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

class ULElement(ElementNode):
    """
     无序列表
    """
    def __init__(self, text: str = None, **kwargs):
        super().__init__(**kwargs)
        self.text = text

class OLElement(ElementNode):
    """
     无序列表
    """
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
        else:
            self.title = title

        content_views = content_node[0].xpath('//div[@id="content_views"]')
        if len(content_views) > 0:
            self.article_content = content_views[0]
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
        tail = ""
        if element.tail is not None and element.tail.strip() != "":
            tail = element.tail
        if element.tag == 'img':
            image_src = element.get("src")
            logger.debug('解析到图片: %s', image_src)
            return ImageElementNode(image_src, tag="image", html_element=element)
        if element.tag == 'a':
            href = element.get("href")
            return LinkElementNode(href, element.text, tag="a", html_element=element)
        if element.tag == 'p':
            pElementNode = PElementNode(element.text, children=[])
            if CSDNEngine.__has_children__(element):
                for child in element.getchildren():
                    if child.text is not None:
                        child.text += tail
                    elementNdde = self.traverse(child) # type: ElementNode
                    pElementNode.children.append(elementNdde)
            return pElementNode
        if element.tag == 'blockquote':
            calloutElement = CalloutElement(text=element.text)
            calloutElement_children = []
            for child in element.getchildren():
                calloutElement_children.append(self.traverse(child))
            calloutElement.children = calloutElement_children
            return calloutElement
        if element.tag == 'ul':
            ulElement = ULElement(children=[])
            for child in element.getchildren():
                ulElement.children.append(self.traverse(child))
            return ulElement
        if element.tag == 'ol':
            olElement = OLElement(children=[])
            for child in element.getchildren():
                olElement.children.append(self.traverse(child))
            return olElement
        if element.tag == 'h1' or element.tag == 'h2' or element.tag == 'h3' or element.tag == 'h4' or element.tag == 'h5':
            heading = element.find('span')
            if heading is not None:
                return HeadingElementNode(heading.text, int(element.tag[-1]), tag=element.tag, html_element=element)
            heading = element.find('a')
            if heading is not None:
                # 非标准格式
                return HeadingElementNode(heading.tail, int(element.tag[-1]), tag=element.tag, html_element=element)
        # li 存在两种情况，一种是直接套文本，另外一种是套span标签
        if element.tag == 'li':
            if CSDNEngine.__has_children__(element):
                nestedElement = NestedElementNode(element.text, children=[])
                for child in element.getchildren():
                    element_node = self.traverse(child)
                    if child.tag == 'strong' and element_node is not None:
                        # TODO 写死红色，后面再解析RGB值
                        element_node.color = 'default'
                        nestedElement.children.append(element_node)
                        if child.tail is not None and child.tail.strip() != "":
                            nestedElement.children.append(RichText(child.tail, bold=False))

                return nestedElement
            else:
                return RichText(element.text + tail, bold=False)

        if element.tag == 'span':
            nestedElement = NestedElementNode(element.text, children=[])
            for child in element.getchildren():
                element_node = self.traverse(child)
                # 如果是span标签，嵌套这strong标签，说明要加粗并加颜色
                if child.tag == 'strong':
                    element_node.color = 'green'
                nestedElement.children.append(element_node) if element_node else None
            # strong标签里面套了span，span尾部还跟了文本，
            if element.tail is not None and element.tail.strip() != "" and element.getparent().tag == 'strong':
                nestedElement.children.append(RichText(element.tail, bold=True))
            return nestedElement
        if element.tag == 'strong':
            if CSDNEngine.__has_children__(element):
                for child in element.getchildren():
                    element_node = self.traverse(child)
                    if isinstance(element_node, NestedElementNode):
                        # TODO 暂时只返回第一个，有多个实在不好处理
                        return element_node
            else:
                return RichText(element.text, bold=True, html_element=element)

    

    def get_Elements(self) -> list[ElementNode]:
        return self.elements
    


