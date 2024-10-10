from engine import ImageElementNode, PElementNode, HeadingElementNode, RichText, ElementNode


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
        "plain_text": "Some words ",
    }


def transformElement(node):
    if isinstance(node, PElementNode):
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


def transformPElementNode(node: PElementNode):
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
            if isinstance(child, RichText):
                paragraph['paragraph']['rich_text'].append(notionEle)
                indices_to_remove.append(i)
            elif isinstance(child, ElementNode):
                paragraph['paragraph']['children'].append(notionEle)
        for index in sorted(indices_to_remove, reverse=True):
            del node.children[index]
    return paragraph