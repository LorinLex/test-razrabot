import asyncio
import re
import string
from typing import Any
import httpx
import pymorphy2

from src.utils import get_product_data_url


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }


async def search_keyword(kw: str, referer_url: str, page: int = 1):
    url = (
        "https://recom.wb.ru/recom/ru/common/v5/search?"
        "ab_testing=false"
        "&appType=1"
        "&curr=rub"
        "&dest=-1255987"
        "&hide_dtype=13"
        "&lang=ru"
        f"&page={page}"
        f"&query={kw}"
        "&resultset=catalog"
        "&spp=30"
        "&suppressSpellcheck=false"
    )
    headers = get_headers(url)

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)

    return response.json()


morph = pymorphy2.MorphAnalyzer()


def get_keywords(text: str) -> list[str]:
    spec_chars = string.punctuation + '«»\t…’'
    text = re.sub(rf'[{spec_chars}\d]', "", text)
    text = re.sub('\n', ' ', text)
    text = text.lower()
    words = text.split(" ")

    def pos(word: str) -> str:
        "Return a likely part of speech for the *word*."""
        return morph.parse(word)[0].tag.POS  # type: ignore

    # get only nouns as hot keywords
    hot_keywords = [word for word in words if pos(word) == "NOUN"]

    return hot_keywords


async def get_product_data(id: int) -> dict[str, Any]:
    response: httpx.Response
    url = get_product_data_url(id)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=url,
            headers=get_headers(url)
        )

    return response.json()


def get_product_id_from_url(url: str) -> str:
    return url.split("/")[-2]


async def parser():
    hot_kw_limit = 5

    url = 'https://www.wildberries.ru/catalog/181901033/detail.aspx'

    id = get_product_id_from_url(url)
    product_data = await get_product_data(int(id))
    all_hot_kws = get_keywords(product_data["description"])
    search_kws = all_hot_kws[:hot_kw_limit]
    print(search_kws)


if __name__ == "__main__":
    asyncio.run(parser())
