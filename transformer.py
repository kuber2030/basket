import copy
import logging

from engine import ImageElementNode, PElementNode, HeadingElementNode, RichText, ElementNode, CalloutElement, \
    NestedElementNode, ULElement, OLElement, LinkElementNode, CodeElementNode


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
    try:
        n = {
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
        return n
    except Exception as e:
        logging.error("解析RichElement失败", exc_info=e)






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

    if isinstance(node, LinkElementNode):
        return transformLinkElementNode(node)

    if isinstance(node, HeadingElementNode):
        return transformHeadingElementNode(node)

    if isinstance(node, RichText):
        return transformRichElementNode(node)

    if isinstance(node, CodeElementNode):
        return transformCodeElementNode(node)



def transformHeadingElementNode(node: HeadingElementNode):
    # notion最大只支持3级标题
    level = node.level % 4
    if node.level >=4:
        level += 1
    # 分割得到数字
    splitted = node.text.split(" ", 1)
    if len(splitted) > 1:
        spped = splitted[0].split(".")
        if len(spped) > 0:
            try:
                level = int(len(spped))
            except Exception as e:
                logging.error("解析标题级别失败", exc_info=e)
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


def transformLinkElementNode(node: LinkElementNode):
    return {
        "type": "text",
        "text": {
            "content": node.text,
            "link": {
                "url": node.href
            }
        },
        "plain_text": "",
        "href": node.href,
    }



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
                deepCopyRichTextIfExistsTail(child, notionEle, paragraph)
                # indices_to_remove.append(i)
            elif isinstance(child, ImageElementNode):
                paragraph['paragraph']['children'].append(notionEle)
            elif isinstance(child, LinkElementNode):
                paragraph['paragraph']['rich_text'].append(notionEle)
            elif isinstance(child, ElementNode):
                paragraph['paragraph']['children'].append(notionEle)
        # 删除所有子元素
        node.children = []
    return paragraph


def deepCopyRichTextIfExistsTail(child, notionEle, paragraph):
    """
    深拷贝RichText如果存在尾部文本
    """
    if child.tail and len(child.tail) > 0:
        tailRichText = copy.deepcopy(notionEle)
        tailRichText['text']['content'] = child.tail
        tailRichText['annotations']['bold'] = False
        tailRichText['annotations']['italic'] = False
        tailRichText['annotations']['color'] = 'default'
        paragraph['paragraph']['rich_text'].append(tailRichText)


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
            list_item = {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": []}}
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
                # 处理li标签中，还会嵌套图片的特殊情况
                if isinstance(child_in_current, ImageElementNode):
                    if not hasattr(list_item['bulleted_list_item'], 'children'):
                        list_item['bulleted_list_item']['children'] = []
                    list_item['bulleted_list_item']['children'].append(transformImageElementNode(child_in_current))
                elif isinstance(child_in_current, LinkElementNode):
                    if not hasattr(list_item['bulleted_list_item'], 'children'):
                        list_item['bulleted_list_item']['children'] = []
                    list_item['bulleted_list_item']['rich_text'].append(transformLinkElementNode(child_in_current))
                elif isinstance(child_in_current, PElementNode):
                    logging.info(f"<li>标签嵌套<p>标签处理 {child_in_current.text}")
                    for child in child_in_current.children:
                        stack.append(child)
                else:
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


def merge_PElementNode_children_into_numbered_list_item(pElementNode: PElementNode):
    """把p标签中的所有子元素合并为有序列表项，因此只方法只会返回富文本列表"""
    richTextList = []
    stack = []
    if len(pElementNode.children) > 0:
        if pElementNode.text is not None:
            richTextList.append(RichText(pElementNode.text))
        # 这里要实现深度遍历，而不是层序遍历
        for child in reversed(pElementNode.children):
            stack.append(child)
        while len(stack) > 0:
            current = stack.pop()
            # 先保存当前节点的文本，再遍历子节点
            if current.text is not None:
                richTextList.append(RichText(current.text))
            if isinstance(current, NestedElementNode):
                for child in reversed(current.children):
                    stack.append(child)
            if isinstance(current, PElementNode):
                for child in reversed(current.children):
                    stack.append(child)
            if isinstance(current, RichText):
                richTextList.append(current)
    else:  # 无子元素,直接添加为富文本
        richTextList.append(RichText(pElementNode.text))
    return richTextList

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
            list_item = {"type": "numbered_list_item", "numbered_list_item": {"rich_text": []}}
            list_item['numbered_list_item']['rich_text'].append({
                "type": "text",
                "text": {
                    "content": current.text,
                }
            })
        if isinstance(current, NestedElementNode):
            for child in reversed(current.children):
                stack.append(child)
        elif isinstance(current, PElementNode):
            logging.info(f"<li>标签嵌套<p>标签处理 {current.text}")
            # 拿出<p>中的所有子元素，内部方法会处理，不需要再深度遍历了
            richTextList = merge_PElementNode_children_into_numbered_list_item(current)
            for richText in richTextList:
                list_item = {"type": "numbered_list_item", "numbered_list_item": {"rich_text": []}}
                list_item['numbered_list_item']['rich_text'].append(transformRichElementNode(richText))
                list_items.append(list_item)
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


def transformCodeElementNode(node):
    code = {"type": "code", "code": {"rich_text": []}}
    node.text = node.text.strip() if node.text is not None else None
    if node.text is not None and len(node.text) > 0:
        node.text = node.text.strip()
        code['code']['rich_text'].append({
            "type": "text",
            "text": {
                "content": node.text,
            }
        })
    code['code']['language'] = node.language
    return code