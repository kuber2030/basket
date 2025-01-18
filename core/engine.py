import logging
from lxml import etree
from bs4 import BeautifulSoup
from bs4.element import Tag

logger = logging.getLogger(__name__)


class ElementNode:
    def __init__(self, id=None, tag=None, children: list = None, html_element=None):
        self.id = id
        self.tag = tag
        self.children = children
        self.html_element = html_element

class HeadingElementNode(ElementNode):
    def __init__(self, text: str, level: int, color=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.level = level


class ImageElementNode(ElementNode):
    def __init__(self, src: str, **kwargs):
        super().__init__(**kwargs)
        self.src = src
        # self.src = "https://www.notion.so/images/page-cover/woodcuts_6.jpg"
        # if "?" in self.src:
        #     self.src = self.src.split("?")[0]


class LinkElementNode(ElementNode):
    def __init__(self, href: str, text: str, **kwargs):
        super().__init__(**kwargs)
        self.href = href
        self.text = text


class RichText(ElementNode):
    def __init__(self, text, bold=False, italic=False, strikethrough=False, underline=False, code=False, color="default", tail=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.bold = bold
        self.italic = italic
        self.strikethrough = strikethrough
        self.underline = underline
        self.code = code
        self.color = color
        self.tail = tail

class CodeElementNode(ElementNode):

    def __init__(self, text: str, language: str, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.language = language

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


    @staticmethod
    def get_engine(website_type: str):
        if website_type == "csdn":
            def _builder(text:str, title:str):
                    return CSDNEngine(text, title, website_type="csdn")
            return _builder

        elif website_type == "wx":
            def _builder(text:str, title:str):
                    return WxEngine(text, title, website_type="wx")
            return _builder

class CSDNEngine(Engine):

    def __init__(self, html_text, title=None, **kwargs):
        super().__init__(kwargs["website_type"], html_text)
        html: etree._Element = etree.HTML(self.html_text)
        content_node = html.xpath('//div[@class="blog-content-box"]')  # type: list[etree._Element]
        if not title:
            self.title = self.parse_article_title(content_node[0])
        else:
            self.title = title

        content_views = content_node[0].xpath('//div[@id="content_views"]')
        if len(content_views) > 0:
            self.article_content = content_views[0]
        # 处理特殊情况，部分博客下面还嵌套了div
        if content_views[0].getchildren()[0].get('id') == 'js_content':
            self.article_content = content_views[0].getchildren()[0]
        self.elements = []
        assert self.article_content is not None
        self.toc_exists = False
        self.parse_elements()

    def parse_article_title(self, element: etree._Element):
        article_node = element.xpath("//title")
        if article_node:
            return article_node[0].text.removesuffix("-CSDN博客")

    def parse_elements(self):
        children = self.article_content.getchildren()  # type: list[etree._Element]
        for child in children:
            element = self.traverse(child)
            # 某些情况下，会返回多个
            if isinstance(element, list):
                self.elements += element
            elif element is not None:
                self.elements.append(element)

    @staticmethod
    def __has_children__(element):
        return element is not None and len(element.getchildren()) > 0

    def traverse(self, element:etree._Element):
        if element is None:
            return None

        if element.get("id") == "hr-toc":
            # 还没跳过目录区
            self.toc_exists = False
            return None
        # 目录出现了
        if element.get("id") == "main-toc":
            # 还没跳过目录区
            self.toc_exists = True
            return None
        if self.toc_exists:
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
                    elementNdde = self.traverse(child) # type: ElementNode
                    pElementNode.children.append(elementNdde)
                    # 好多不规范的情况
                    if child.tail is not None and child.tail.strip() != "":
                        pElementNode.children.append(RichText(child.tail.strip()))
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
            # 特殊情况兼容处理
            headingText = element.text
            if headingText is not None:
                return HeadingElementNode(headingText, int(element.tag[-1]), tag=element.tag, html_element=element)
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
                        # if child.tail is not None and child.tail.strip() != "":
                        #     nestedElement.children.append(RichText(child.tail, bold=False))
                    elif child.tag == 'span' and element_node is not None and isinstance(element_node, NestedElementNode):
                        nestedElement.children += element_node.children
                        if child.tail is not None and child.tail.strip() != "":
                            nestedElement.children.append(RichText(child.tail, bold=False))
                        return nestedElement
                    elif child.tag == 'img' and element_node is not None:
                        nestedElement.children.append(element_node)
                    elif child.tag == 'a' and element_node is not None:
                        nestedElement.children.append(element_node)
                    elif child.tag == 'p' and element_node is not None:
                        # 如果li嵌套了p标签 例如：<li><p></p></li>，忘记为什么要这样干了, 有可能是为了处理类似于<li><p></p><span></span></li>这种情况
                        pElementNode = PElementNode(element.text, children=[])
                        if CSDNEngine.__has_children__(element):
                            for child in element.getchildren():
                                elementNdde = self.traverse(child)  # type: ElementNode
                                pElementNode.children.append(elementNdde)
                                # 好多不规范的情况
                                if child.tail is not None and child.tail.strip() != "":
                                    pElementNode.children.append(RichText(child.tail.strip()))
                        nestedElement.children.append(pElementNode)
                    #  增加li标签内的code标签解析
                    elif child.tag == 'code':
                        nestedElement.children.append(RichText(child.text, code=True))

                    if child.tail is not None and child.tail.strip() != "":
                        nestedElement.children.append(RichText(child.tail.strip()))

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
        if element.tag == 'em':
            return RichText(element.text, italic=True, html_element=element)

        if element.tag == 'pre':
            # 解析code标签
            if element.getchildren() and element.getchildren()[0].tag == "code":
                code_bolock = ""
                language = "bash"
                code_language = element.get("class") if element.get("class") is not None else ""
                if "javascript" in code_language:
                    language = 'javascript'
                elif "java" in code_language:
                    language = 'java'
                elif "python" in code_language:
                    language = 'python'
                elif "go" in code_language:
                    language = 'go'
              # type: list[etree._Element]
                code = element.xpath("code")
                if code is None or len(code) <= 0:
                    return None
                if code[0].text is not None and code[0].text != '\r':
                    code_bolock += code[0].text
                children = code[0].getchildren()
                for child in children:
                    if child.tag == 'span':
                        if child.text is not None:
                            code_bolock += child.text
                        if child.tail and child.tail!= '\r':
                            code_bolock += child.tail
                if code_bolock != '':
                    return CodeElementNode(code_bolock, language, tag="code", html_element=element)
        if element.tag == 'code':
            return RichText(element.text, code=True) # 行内代码块，实际上就是普通的文本，添加了code属性

    def get_Elements(self) -> list[ElementNode]:
        return self.elements
    

class WxEngine(Engine):
    def __init__(self, html_text, title=None, **kwargs):
        super().__init__(kwargs["website_type"], html_text)
        self.title = "xxx"
        self.elements = []
        self.parse_elements()

    def get_Elements(self) -> list[ElementNode]:
        return self.elements

    def write_to_file(self, content: str):
        with open("./test.txt", "a", encoding="utf-8") as f:
            if len(content) > 0:
                f.write(content)
                f.write("\n")
                f.close()

    def traverse_content(self, element: Tag):
        """
        遍历微信文章正文开始
        """
        ele_name = element.name
        if ele_name == 'div':
            children = element.children
            for child in children:
                self.traverse_content(child)
        elif ele_name == "p":
            # 当前节点文本为空，或只有一个儿子，且儿子也为空
            current_text_p = element.string
            if current_text_p is None:
                children_p = element.children
                for child in children_p:
                    if child.name == 'img':
                        # image_src = image_src.replace("\n", "")
                        # self.write_to_file(image_src)
                        # self.elements.append(ImageElementNode(image_src, tag="image", html_element=element))
                        # self.write_to_file(child.attrs['data-src'])
                        # self.elements.append(ImageElementNode(child.attrs['data-src'].strip(), tag="image", html_element=element))
                        image_src = child.attrs['data-src']
                        image_src = image_src.replace("\n", "")
                        self.write_to_file(image_src)
                        self.elements.append(ImageElementNode(image_src, tag="image", html_element=child))

                    # 如果当前节点有值
                    elif child.string is not None:
                        pElementNode = PElementNode(child.string + "\n", children=[])
                        self.elements.append(pElementNode)
                        self.write_to_file(child.string)
                    # 获取所有的儿子节点的文本值
                    else:
                        pElementNode = PElementNode(child.text+ "\n", children=[])
                        self.elements.append(pElementNode)
                        self.write_to_file(child.text)
            else:
                self.write_to_file(current_text_p)
                pElementNode = PElementNode(current_text_p, children=[])
                self.elements.append(pElementNode)

        elif ele_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            current_text_h = element.string
            if current_text_h is None:
                # 获取所有子节点的文本
                self.write_to_file(element.text)
                current_text_h = element.text
                self.elements.append(HeadingElementNode(current_text_h, int(element.name[-1]), tag=element.name))
            else:
                self.write_to_file(current_text_h)
                self.elements.append(HeadingElementNode(current_text_h, int(element.name[-1]), tag=element.name))

        elif ele_name == "ul":
            ulElement = ULElement(element.string, children=[])
            lis = element.find_all(name='li')
            for li in lis:
                if li.string is None:
                    self.write_to_file("-" + li.text)
                    nestedElement = NestedElementNode(li.text, children=[])
                else:
                    self.write_to_file(li.string)
                    nestedElement = NestedElementNode(li.string, children=[])
                ulElement.children.append(nestedElement)
            self.elements.append(ulElement)

        elif ele_name == "image":
            image_src = element.attrs['data-src'].strip()
            if "\n" in image_src:
                image_src = image_src.replace("\n", "")
                self.write_to_file(image_src)
                self.elements.append(ImageElementNode(image_src, tag="image", html_element=element))

    def traverse(self, element: Tag):
        for child in element.children:
            if child.name is None:
                continue
                # print("纯文本：", child.string)
            # 文章标题
            elif child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                self.title = child.string.strip()
                self.write_to_file(self.title)

            elif child.name == "div":
                # 不需要处理标题元信息
                if child.attrs.get("id") == "meta_content":
                    continue
                elif child.attrs.get("id") == "js_content":
                    self.traverse_content(child)
            elif child.name == 'section':
                # 跳过section节点，暂时不支持目录的解析
                print()
            else:
                print(f"不支持的标签：{child.name} {child.string}")

    def parse_elements(self):
        soup = BeautifulSoup(self.html_text, 'html.parser')
        container = soup.select("#img-content", limit=1)[0]
        self.traverse(container)

