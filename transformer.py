from queue import Queue
from turtle import st

import scipy as sp
from sympy import li

from engine import ImageElementNode, PElementNode, HeadingElementNode, RichText, ElementNode, CalloutElement, \
    NestedElementNode, ULElement, OLElement


def transform_image(url: str):
    """
     transform notion image
    :param url:
    :param children:
    :return:
    """
    image = {
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": url
            },
        }
    }
    return image


def transformRichElementNode(node):
    return {
        "type": "text",
        "text": {
            "content": node.text,
        },
        "annotations": {
            "bold": node.bold,
            "italic": node.italic,
            "strikethrough": node.strikethrough,
            "underline": node.underline,
            "code": node.code,
            "color": node.color
        },
        "plain_text": "",
    }


def transformElement(node):
    if isinstance(node, CalloutElement):
        return transformCalloutElement(node)

    if isinstance(node, PElementNode) or isinstance(node, NestedElementNode):
        return transformPElementNode(node)

    if isinstance(node, ULElement):
        return transformUlElementNode(node)

    if isinstance(node, OLElement):
        return transformOlementNode(node)

    if isinstance(node, ImageElementNode):
        return transformImageElementNode(node)

    if isinstance(node, HeadingElementNode):
        return transformHeadingElementNode(node)

    if isinstance(node, RichText):
        return transformRichElementNode(node)


def transformHeadingElementNode(node: HeadingElementNode):
    # notion最大只支持3级标题
    level = node.level % 4
    if node.level >=4:
        level += 1
    # 分割得到数字
    splitted = "".split(" ", 1)
    if len(splitted) > 0:
        spped = splitted[0].split(".")
        if len(spped) > 0:
            level = int(spped[0])
    heading = {
        "type": f"heading_{level}",
        f"heading_{level}": {
            "rich_text": [{"type": "text", "text": {"content": node.text}}]
        }
    }
    return heading


def transformImageElementNode(node: ImageElementNode):
    """
    添加图片
    :param url:
    :param children:
    :return:
    """
    image = {
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": node.src
            },
        }
    }
    return image


def transformCalloutElement(node: CalloutElement):
    callout = {"type": "callout", "callout": {"rich_text": []}}
    node.text = node.text.strip() if node.text is not None else None
    if node.text is not None and len(node.text) > 0:
        node.text = node.text.strip()
        callout['callout']['rich_text'].append({
            "type": "text",
            "text": {
                "content": node.text,
            }
        })
    # 默认灰色背景
    callout['callout']['color'] = 'gray_background'
    # 默认图标💡
    callout['callout']['icon'] = {"type": "emoji", "emoji": "💡"}
    return callout


def transformPElementNode(node: PElementNode | NestedElementNode):
    """
    添加图片
    :param url:
    :param children:
    :return:
    """
    paragraph = {"type": "paragraph", "paragraph": {"rich_text": []}}
    if node.text is not None:
        paragraph['paragraph']['rich_text'].append({
            "type": "text",
            "text": {
                "content": node.text,
            }
        })
    if len(node.children) > 0:
        paragraph['paragraph']['children'] = []
        # indices_to_remove = []
        for i, child in enumerate(node.children):
            notionEle = transformElement(child)
            if isinstance(child, RichText):
                paragraph['paragraph']['rich_text'].append(notionEle)
                # indices_to_remove.append(i)
            elif isinstance(child, ImageElementNode):
                paragraph['paragraph']['children'].append(notionEle)
                # indices_to_remove.append(i)
            elif isinstance(child, ElementNode):
                paragraph['paragraph']['children'].append(notionEle)
        # for index in sorted(indices_to_remove, reverse=True):
        #     del node.children[index]
        # 删除所有子元素
        node.children = []
    return paragraph


def transformUlElementNode(node: ULElement):
    """
    添加列表
    :param url:
    :param children:
    :return:
    """
    list_items = []
    stack = []
    stack.append(node)
    while len(stack) > 0:
        current = stack.pop()
        if current.text is not None and not isinstance(current, RichText):
            list_item['bulleted_list_item']['rich_text'].append({
                "type": "text",
                "text": {
                    "content": current.text,
                }
            })
        if isinstance(current, NestedElementNode):
            for child in reversed(current.children):
                stack.append(child)
            size = len(current.children)
            list_item = {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": []}}
            for i in range(size):
                child_in_current = stack.pop()
                list_item['bulleted_list_item']['rich_text'].append(transformRichElementNode(child_in_current))
            list_items.append(list_item)
        # 如果已经是富文本了，直接追加
        elif isinstance(current, RichText):
            list_item = {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": []}}
            list_item['bulleted_list_item']['rich_text'].append(transformRichElementNode(current))
            list_items.append(list_item)
        elif isinstance(current, ULElement):
            for child in reversed(current.children):
                stack.append(child)
    # 删除所有的子元素，因为在这一步我们已经递归完毕了
    node.children=[]
    return list_items

def transformOlementNode(node: OLElement):
    """
    add numbered list item
    :param url:
    :param children:
    :return:
    """
    list_items = []
    stack = []
    stack.append(node)
    while len(stack) > 0:
        current = stack.pop()
        if current.text is not None and not isinstance(current, RichText):
            list_item['numbered_list_item']['rich_text'].append({
                "type": "text",
                "text": {
                    "content": current.text,
                }
            })
        if isinstance(current, NestedElementNode):
            for child in reversed(current.children):
                stack.append(child)
        # 如果已经是富文本了，直接追加
        elif isinstance(current, RichText):
            list_item = {"type": "numbered_list_item", "numbered_list_item": {"rich_text": []}}
            list_item['numbered_list_item']['rich_text'].append(transformRichElementNode(current))
            list_items.append(list_item)
        elif isinstance(current, OLElement):
            for child in reversed(current.children):
                stack.append(child)
    # 删除所有的子元素，因为在这一步我们已经递归完毕了
    node.children = []
    return list_items
