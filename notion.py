import json
import logging
import uuid

import requests

logger = logging.getLogger(__name__)
class Client(object):
    headers = {
        "Authorization": "Bearer {}",
        "Notion-Version": "2022-06-28"
    }

    def __init__(self, secrect: str, proxy=None):
        self.secrect = secrect
        self.proxy = proxy
        self.headers["Authorization"] = self.headers["Authorization"].format(secrect)

    def create_page(self, title: str, children: list, database_id=None, page_id=None, **kwargs):
        """
        :param title:
        :param children:
        :param database_id:
        :param page_id:
        :param kwargs:
        :return:
        """
        parent = {}
        properties = {}
        if page_id:
            parent["page_id"] = page_id
            # If the parent is a page, then the only valid object key is title.
            properties["title"] = {
                # 1178289d-f069-81f9-9e3a-e2a57448f265
                # "id": "title",
                "id": "1178289d-f069-81f9-9e3a-e2a57448f265",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title,
                            "link": None
                        },
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default"
                        },
                        "plain_text": "",
                        "href": None
                    }
                ]
            }
        elif database_id:
            parent['database_id'] = database_id
        else:
            raise Exception("页面id或者数据库id不能为空")
        return self.__create_page(parent, properties, children, **kwargs)

    def __create_page(self, parent, properties: dict, children: list, icon=None, cover=None):
        """
        :param parent:
        :param properties:
        :param children:
        :param icon: Either an emoji object or an external file object..
        :param cover:
        :return:
        """
        params = {}
        params["parent"] = parent
        if not icon:
            params["icon"] = icon
        if not cover:
            params["cover"] = cover
        params['properties'] = properties
        if children:
            params['children'] = children
        print("create page param ", params)
        return requests.post("https://api.notion.com/v1/pages", json=params, headers=self.headers, proxies= self.proxy)

    """
    获取页面属性，只适合不超过25个reference的页面
    """

    def get_page(self, page_id: str):
        page_id = self.decude_page_id(page_id)
        return requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=self.headers)

    def get_page_blocks(self, page_id: str):
        page_id = self.decude_page_id(page_id)
        return requests.get(f"https://api.notion.com/v1/blocks/{page_id}/children", headers=self.headers)

    def append_block(self, block_id: str, children: list, after: str = None):
        """
        Creates and appends new children blocks to the parent block_id specified. Blocks can be parented by other blocks, pages, or databases.
        https://developers.notion.com/reference/patch-block-children
        :param block_id: Identifier for a block. Also accepts a page ID.
        :param children: Child content to append to a container block as an array of block objects
        :param after: The ID of the existing block that the new block should be appended after.
        :return: Returns a paginated list of newly created first level children block objects.
        """
        for child in children:
            child["object"] = "block"
        data = {"children": children}
        if after:
            data["after"] = after
        block_id = self.decude_page_id(block_id)
        logger.debug("创建block参数 %s", json.dumps(data, ensure_ascii=False))
        return requests.patch(f"https://api.notion.com/v1/blocks/{block_id}/children", json=data, headers=self.headers, proxies= self.proxy)

    def decude_page_id(self, page_id: str):
        assert len(page_id) >= 32
        if not "-" in page_id:
            # 8-4-4-4-12
            page_id = "-".join([page_id[0:8], page_id[8:12], page_id[12:16], page_id[16:20], page_id[20:]])
        return page_id


def append_heading(head_text, level, children: list, **kwargs):
    """
    添加标题
    :param head_text:
    :param level: 标题级别 1，2, 3,4
    :param children:
    :param kwargs:
    :return:
    """
    heading = {
        "type": f"heading_{level}",
        f"heading_{level}": {
            "rich_text": [{"type": "text", "text": {"content": head_text}}]
        }
    }
    children.append(heading)


def append_image(url: str, children: list):
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
                "url": url
            },
        }
    }
    children.append(image)
    return children



def append_paragraph(paragraph_text: str, notion_children: list, **kwargs):
    """
    添加段落
    :param paragraph_text:
    :param children:
    :param kwargs:
    :return:
    """
    rich_texts = kwargs.get("rich_texts")
    if not paragraph_text and not rich_texts and len(rich_texts) == 0:
        return
    paragraph = {
        "id": uuid.uuid4(),
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": paragraph_text,
                    "link": None,
                }
            }],
            "color": "default"
        }
    }
    if rich_texts and len(rich_texts) > 0:
        paragraph["paragraph"]["rich_text"] = rich_texts
    logger.debug("生成段落id是" + paragraph["id"])
    notion_children.append(paragraph)


def append_richtext(text, bold, color, italic, rich_texts, code=False, strikethrough=False, underline=False):
    """
    添加富文本
    :param text:
    :param bold:
    :param color:
    :param italic:
    :param rich_texts:
    :param code:
    :param strikethrough:
    :param underline:
    :return:
    """
    if not color:
        color = "default"
    rich_text = {
        "type": "text",
        "text": {
            "content": text,
            "link": None
        },
        "annotations": {
            "bold": bold,
            "italic": italic,
            "strikethrough": strikethrough,
            "underline": underline,
            "code": code,
            "color": color
        },
        "plain_text": "",
        "href": None
    }

    rich_texts.append(rich_text)
    return rich_texts

def append_item(item: str, children: list, **kwargs):
    children.append(item)
    return children

