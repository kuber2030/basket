from engine import ImageElementNode, PElementNode, HeadingElementNode, RichText, ElementNode, CalloutElement, \
    NestedElementNode, ULElement


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

    if isinstance(node, ImageElementNode):
        return transformImageElementNode(node)

    if isinstance(node, HeadingElementNode):
        return transformHeadingElementNode(node)

    if isinstance(node, RichText):
        return transformRichElementNode(node)


def transformHeadingElementNode(node: HeadingElementNode):
    if node.level > 3:
        node.level = node.level % 3
    heading = {
        "type": f"heading_{node.level}",
        f"heading_{node.level}": {
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
    paragraph = {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": []}}
    if node.text is not None:
        paragraph['bulleted_list_item']['rich_text'].append({
            "type": "text",
            "text": {
                "content": node.text,
            }
        })
    if len(node.children) > 0:
        paragraph['bulleted_list_item']['children'] = []
        for i, child in enumerate(node.children):
            notionEle = transformElement(child)
            if isinstance(child, RichText):
                paragraph['bulleted_list_item']['rich_text'].append(notionEle)
            elif isinstance(child, ImageElementNode):
                paragraph['bulleted_list_item']['children'].append(notionEle)
            elif isinstance(child, ElementNode):
                paragraph['bulleted_list_item']['children'].append(notionEle)
        node.children = []
    return paragraph
