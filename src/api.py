'''
Source:
https://github.com/glmn/wb-private-api/blob/538355baf2293917ec55b2b2afc1326d106e8c89/src/Utils.js
'''
from typing import Any
import httpx


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


CARD_URL = "https://basket-{0}.wb.ru/vol{1}/part{2}/{3}/info/ru/card.json"


def get_basket_number(product_id):
    vol = int(product_id) // 100000
    basket = 1  # Значение по умолчанию
    for index, (start, end) in enumerate(BASKETS):
        if start <= vol <= end:
            basket = index + 1
            break
    return basket


def get_headers(url: str):
    return {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Origin': 'https://www.wildberries.ru',
        'Referer': url,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/127.0.0.0 Safari/537.36',
    }


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


def get_search_url(keyword: str, page: int = 1) -> str:
    return (
        'https://search.wb.ru/exactmatch/ru/common/v9/search?'
        'ab_testing=false&'
        'appType=1&'
        'curr=rub&'
        'dest=-1255987&'
        'hide_dtype=13&'
        'lang=ru&'
        f'page={page}&'
        f'query={keyword}&'
        'resultset=catalog&'
        'sort=popular&'
        'spp=30&'
        'suppressSpellcheck=false'
    )


async def get_product_data(id: int) -> dict[str, Any]:
    response: httpx.Response
    url = get_product_data_url(id)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=url,
            headers=get_headers(url)
        )

    return response.json()


async def search_by_keyword(
    kw: str,
    referer_url: str,
    page: int = 1
) -> dict[str, Any]:
    url = get_search_url(kw, page)
    headers = get_headers(referer_url)

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)

    return response.json()


async def check_url(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url,
                headers=get_headers(url)
            )
        return response.is_success
    except Exception:
        return False
