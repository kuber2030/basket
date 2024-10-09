from engine import ImageElementNode, PElementNode, HeadingElementNode


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


def transformElement(node):
    if isinstance(node, PElementNode):
        return transformPElementNode(node)

    if isinstance(node, ImageElementNode):
        return transformImageElementNode(node)

    if isinstance(node, HeadingElementNode):
        return transformHeadingElementNode(node)



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
    paragraph = {"type": "paragraph"}
    if node.text is not None:
        paragraph['rich_text'] = {
            "type": "text",
            "text": {
                "content": node.text,
            }
        }
    if len(node.children) > 0:
        paragraph['children'] = []
        for child in node.children:
            paragraph['children'].append(transformElement(child))
    return paragraph