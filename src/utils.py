'''
Source:
https://github.com/glmn/wb-private-api/blob/538355baf2293917ec55b2b2afc1326d106e8c89/src/Utils.js
'''


BASKETS = [
    [0, 143],
    [144, 287],
    [288, 431],
    [432, 719],
    [720, 1007],
    [1008, 1061],
    [1062, 1115],
    [1116, 1169],
    [1170, 1313],
    [1314, 1601],
    [1602, 1655],
    [1656, 1919],
    [1920, 2045],
    [2046, 2189],
    [2091, 2405],
    [2406, 2621]
]


CONTENT_URL = "https://wbx-content-v2.wbstatic.net/ru/{}.json"
CARD_URL = "https://basket-{0}.wb.ru/vol{1}/part{2}/{3}/info/ru/card.json"
SELLERS_URL = "https://basket-{0}.wb.ru/vol{1}/part{2}/{3}/info/sellers.json"
EXTRADATA_URL = "https://www.wildberries.ru/webapi/product/{}/data"
DETAILS_URL = "https://card.wb.ru/cards/detail"


def get_basket_number(product_id):
    vol = int(product_id) // 100000
    basket = 1  # Значение по умолчанию
    for index, (start, end) in enumerate(BASKETS):
        if start <= vol <= end:
            basket = index + 1
            break
    return basket


def get_product_data_url(id: int):
    limits = [0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]

    sku = str(id)
    basket_number = get_basket_number(sku)
    vol = sku[:limits[len(sku)]] if len(sku) > 5 else '0'
    part = sku[:limits[len(sku) + 2]]

    url = CARD_URL.format(
        f"0{basket_number}" if basket_number < 10 else basket_number,
        vol,
        part,
        sku
    )

    return url
