import requests

import engine
import notion


class TestCase01Class():
    client = notion.Client("secret_TFChRbHM6JBd7zd41OpgfXWkGRxA8PbR3cI8g51AQ8g")

    def test_get_page(self):
        # https://www.notion.so/1178289df0698177845aec91fe937f31?pvs=4
        # https://www.notion.so/blockid-1188289df0698113b472c82a651a2a0c?pvs=4
        # 1188289df0698113b472c82a651a2a0c
        resp = self.client.get_page("1178289df0698177845aec91fe937f31")
        print(resp.text)

    def test_get_page_blocks(self):
        # https://www.notion.so/1178289df0698177845aec91fe937f31?pvs=4
        resp = self.client.get_page_blocks("1178289df0698177845aec91fe937f31")
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


    def test_csdn_engin(self):
        response = requests.get("https://kangll.blog.csdn.net/article/details/135519763")
        csdnEngine = engine.CSDNEngine("csdn", response.text, title="测试engine")
        assert  len(csdnEngine.get_Elements()) > 0
        print(csdnEngine.get_Elements())