import requests

from core import engine
import notion
import transformer
import logging
class TestCase01Class():
    client = notion.Client("secret_TFChRbHM6JBd7zd41OpgfXWkGRxA8PbR3cI8g51AQ8g", proxy={"https": "https://127.0.0.1:7890", "https": "http://127.0.0.1:7890"})

    def test_get_page(self):
        # https://www.notion.so/1178289df0698177845aec91fe937f31?pvs=4
        # https://www.notion.so/blockid-1188289df0698113b472c82a651a2a0c?pvs=4
        # 1188289df0698113b472c82a651a2a0c https://www.notion.so/code-17a8289df06980f7b0cbfa426e9d26b5?pvs=4
        resp = self.client.get_page("17a8289df06980f7b0cbfa426e9d26b5")
        print(resp.text)

    def test_get_page_blocks(self):
        # https://www.notion.so/1178289df0698177845aec91fe937f31?pvs=4
        resp = self.client.get_page_blocks("17b8289df06981139345c234d9d68536")
        with open("./block.json", "w+", encoding="utf-8") as f:
            f.write(resp.text)

    def test_get_callout_blocks(self):
        # https://www.notion.so/1178289df0698177845aec91fe937f31?pvs=4
        resp = self.client.get_page_blocks("1188289d-f069-802b-9462-c2a54677ddd0")
        with open("./callout.json", "w+", encoding="utf-8") as f:
            f.write(resp.text)
    def test_decude_page_id(self):
        pageid = self.client.decude_page_id("1188289df0698113b472c82a651a2a0c")
        print(pageid)

    def test_add_paraGraph_in_callout(self):
        self.client.create_page()


    def test_csdn_engin(self, caplog):
        response = requests.get("https://kangll.blog.csdn.net/article/details/135519763")
        csdnEngine = engine.CSDNEngine("csdn", response.text, title="测试engine")
        assert  len(csdnEngine.get_Elements()) > 0
        print(csdnEngine.get_Elements())

        # createdPage = self.client.create_page(csdnEngine.title, None, page_id="0351ec24-452c-472c-8183-2be67af3720b",)
        # print(createdPage.text)
        # if createdPage.status_code != 200:
        #     return
        # pageid = createdPage.json().get("id")
        pageid = "11a8289d-f069-81f0-a37b-fd8a492dc147"
        for element in csdnEngine.get_Elements():
            notionEle = transformer.transformElement(element)
            resp = self.client.append_block(pageid, notionEle)
            print(resp.text)

    def test_create_list_item(self):
        print(1111)
        logging.info("2222")
