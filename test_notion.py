import notion


class TestCase01Class():

    def test_get_page(self):
        client = notion.Client("secret_TFChRbHM6JBd7zd41OpgfXWkGRxA8PbR3cI8g51AQ8g")
        # https://www.notion.so/1178289df0698177845aec91fe937f31?pvs=4
        resp = client.get_page("1178289df0698177845aec91fe937f31")
        print(resp.text)

    def test_get_page_blocks(self):
        client = notion.Client("secret_TFChRbHM6JBd7zd41OpgfXWkGRxA8PbR3cI8g51AQ8g")
        # https://www.notion.so/1178289df0698177845aec91fe937f31?pvs=4
        resp = client.get_page_blocks("1178289df0698177845aec91fe937f31")
        print(resp.text)


