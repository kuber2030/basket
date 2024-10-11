from engine import ImageElementNode, PElementNode, HeadingElementNode, RichText, ElementNode, CalloutElement, \
    NestedElementNode


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
            "color": "default"
        },
        "plain_text": "",
    }


def transformElement(node):
    if isinstance(node, CalloutElement):
        return transformCalloutElement(node)

    if isinstance(node, PElementNode) or isinstance(node, NestedElementNode):
        return transformPElementNode(node)

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
    # notion CalloutElement不能嵌入p标签，
    # richText = []
    # newChildren = []
    # for child in node.children:
    #     if isinstance(child, PElementNode):
    #         # p标签本身可能包含text，所以这里只能转换成不加粗的richTest
    #         if child.text is not None:
    #             richText.append(transformRichElementNode(RichText(child.text.rstrip(" "), False)))
    #         for p_child in child.children:
    #             # 因notion api限制。无法在标注节点里。创建富文本子节点，只能随标注节点一起创建
    #             if isinstance(p_child, RichText):
    #                 richText.append(transformRichElementNode(p_child))
    #             else:
    #                 newChildren.append(p_child)
    #         callout['callout']['rich_text'] += richText
    #         node.children = newChildren
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
        indices_to_remove = []
        for i, child in enumerate(node.children):
            notionEle = transformElement(child)
            # 嵌套元素不随p标签一起创建，下一次递归再创建
            if isinstance(child, NestedElementNode):
                continue
            if isinstance(child, RichText):
                paragraph['paragraph']['rich_text'].append(notionEle)
                indices_to_remove.append(i)
            elif isinstance(child, ImageElementNode):
                paragraph['paragraph']['children'].append(notionEle)
                indices_to_remove.append(i)
            elif isinstance(child, ElementNode):
                paragraph['paragraph']['children'].append(notionEle)
        for index in sorted(indices_to_remove, reverse=True):
            del node.children[index]
    return paragraph
