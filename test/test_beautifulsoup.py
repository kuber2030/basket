import sys

from bs4 import BeautifulSoup
from bs4.element import Tag

from core.html_loader import HtmlLoader

# 示例HTML文档
html_doc = """
<html>
    <head>
        <title>示例页面</title>
    </head>
    <body>
        <div class="container">
            <h1>主标题</h1>非标准html
            <p class="content">第一段落</p>
            <p class="content">第二段落</p>
            <div class="nested">
                <span>嵌套内容</span>
                <a href="https://example.com">链接</a>
            </div>
        </div>
    </body>
</html>
"""

# 创建BeautifulSoup对象
soup = BeautifulSoup(html_doc, 'html.parser')
html_loader = HtmlLoader()

def traverse_all_methods():
    # 1. 使用 children 遍历直接子节点
    print("1. 遍历直接子节点：")
    body = soup.body
    for child in body.children:
        if child.name:  # 排除空白文本节点
            print(f"直接子节点: {child.name}")

    # 2. 使用 descendants 遍历所有后代节点
    print("\n2. 遍历所有后代节点：")
    for descendant in soup.descendants:
        if descendant.name:
            print(f"后代节点: {descendant.name}")

    # 3. 使用 find_all() 查找特定节点
    print("\n3. 查找所有段落节点：")
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        print(f"段落内容: {p.text}")

    # 4. 使用 next_sibling 和 previous_sibling 遍历兄弟节点
    print("\n4. 遍历兄弟节点：")
    first_p = soup.find('p')
    next_p = first_p.next_sibling.next_sibling  # 跳过空白文本节点
    print(f"下一个兄弟节点: {next_p.text}")

    # 5. 使用 parent 访问父节点
    print("\n5. 访问父节点：")
    span = soup.find('span')
    print(f"span的父节点: {span.parent.name}")

    # 6. 使用 find_parents() 查找所有祖先节点
    print("\n6. 查找所有祖先节点：")
    for parent in span.find_parents():
        if parent.name:
            print(f"祖先节点: {parent.name}")

    # 7. 使用 strings 和 stripped_strings 获取文本
    print("\n7. 获取所有文本内容：")
    for text in soup.stripped_strings:
        print(f"文本内容: {text}")

    # 8. 使用 CSS选择器
    print("\n8. 使用CSS选择器：")
    elements = soup.select('.content')
    for element in elements:
        print(f"类名为content的元素: {element.text}")

def test_01():
    traverse_all_methods()

def check_empty(element: Tag):
    if element.string is None or len(element.string) == 0:
        print(f"{element.name} 标签没有文本 {element.string}", file=sys.stderr)
        return True
    return False


def find_not_empty_nodes(element: Tag):
    print(f"{element.tag} 查找不为空的节点", element.text)
    content = ''
    children = element.find_all()
    for child in children:
        if check_empty(child):
            content += child.text + "\n"
    return content

def write_to_file(content: str):
    with open("./test.txt", "a", encoding="utf-8") as f:
        if len(content) > 0:
            f.write(content)
            f.write("\n")
            f.close()


def traverse_content(element: Tag):
    """
    遍历微信文章正文开始
    """
    ele_name = element.name
    if ele_name == 'div':
        children = element.children
        for child in children:
            traverse_content(child)
    elif ele_name == "p":
        # 当前节点文本为空，或只有一个儿子，且儿子也为空
        current_text_p = element.string
        if current_text_p is None:
            children_p = element.children
            for child in children_p:
                if child.name == 'img':
                    write_to_file(child.attrs['data-src'])
                # 如果当前节点有值
                elif child.string is not None:
                    write_to_file(child.string)
                # 获取所有的儿子节点的文本值
                else:
                    write_to_file(child.text)

        else:
            write_to_file(current_text_p)
    elif ele_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        current_text_h = element.string
        if current_text_h is None:
            # 获取所有子节点的文本
            write_to_file(element.text)
        else:
            write_to_file(current_text_h)
    elif ele_name == "ul":
        # current_text_ul = element.string
        lis = element.find_all(name='li')
        for li in lis:
            if li.string is None:
                write_to_file("-" + li.text)
            else:
                write_to_file(li.string)

    elif ele_name == "image":
        write_to_file(element.attrs['src'])


def traverse(element: Tag):
    for child in element.children:
        if child.name is None:
            print("纯文本：", child.string)
        # 文章标题
        elif child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            write_to_file(child.string.strip())
        elif child.name == "div":
            # 不需要处理标题元信息
            if child.attrs.get("id") == "meta_content":
                continue
            elif child.attrs.get("id") == "js_content":
                traverse_content(child)
        elif child.name == 'section':
            # 跳过section节点，暂时不支持目录的解析
            print()
        else:
            print(f"不支持的标签：{child.name} {child.string}", file=sys.stderr)

def test_02():
    # type: bs4.element.Tag
    html_doc = html_loader.mock_get_html("xxx", path="../aa.html")
    soup = BeautifulSoup(html_doc, 'html.parser')
    container = soup.select("#img-content", limit=1)[0]
    traverse(container)
