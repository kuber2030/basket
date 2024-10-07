
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