import requests

default_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}


class HtmlLoader(object):

    def __init__(self, header=None) -> None:
        if header is None:
            self.header = default_headers

    def get_html(self, url: str) -> str:
        response = requests.get(url, headers=self.header)
        return response.text

    def mock_get_html(self, url: str, **kwargs) -> str:
        """
        mock get_html method, please htmlfile path
        """
        with open(kwargs["path"], 'r', encoding='utf-8') as f:
            lines = f.readlines()
            text = "".join(lines)
            return text

