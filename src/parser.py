import asyncio
from typing import Any
import yake  # type: ignore

from src.api import get_product_data, search_by_keyword
from loguru import logger


def get_product_id_from_url(url: str) -> int:
    return int(url.split("/")[-2])


extractor = yake.KeywordExtractor(
    lan="ru",
    n=3,
    dedupLim=0.3,
    top=10
)


def extract_keywords_list(text: str):
    kw_list = extractor.extract_keywords(text)
    return [x[0] for x in kw_list]


def get_product_kw_list(product_data: dict[str, Any]) -> list[str]:
    return [
        *extract_keywords_list(product_data["imt_name"]),
        *extract_keywords_list(product_data["description"])
    ]


async def get_product_index_in_kw_payload(kw: str, referer_url: str, id: int):
    def process_payload(payload: dict[str, Any]) -> int | None:
        products = payload["data"]["products"]
        for i, product in enumerate(products):
            if product["id"] == id:
                return i
        return None

    # First request outside the loop for getting total pages
    # (dedicated api for getting total need smth like user_id)
    # so that is cheap solution :)
    kw_search_result = await search_by_keyword(kw, referer_url)
    logger.debug(f"Fetching \"{kw}\"")
    total_pages = kw_search_result["data"]["total"] // 100 + 1
    logger.debug(f"\"{kw}\" total pages: {total_pages}")
    product_index = process_payload(kw_search_result)

    if product_index is not None:
        logger.debug(f"Product is on {product_index} on \"{kw}\" keyword")
        return product_index

    for page in range(2, total_pages + 1):

        kw_search_result = await search_by_keyword(kw, referer_url, page=page)
        if "error" in kw_search_result:
            logger.error(f"Error in response: \"{kw}\", page {page}, "
                         f"error: {kw_search_result.get('error', None)}")
            return None

        product_index = process_payload(kw_search_result)
        if product_index is not None:
            logger.debug(f"Product is on {product_index} on \"{kw}\" keyword")
            return product_index
    logger.debug(f"Product not found on \"{kw}\" keyword")
    return product_index


async def parse(url: str):
    id = get_product_id_from_url(url)
    logger.debug(f"Product id: {id}")

    product_data = await get_product_data(id)
    kw_list = get_product_kw_list(product_data)
    logger.debug(f"Keywords: {', '.join(kw_list)}")

    result = {}

    async def task_get_product_index(kw, url, id):
        result[kw] = await get_product_index_in_kw_payload(kw, url, id)

    tasks = [task_get_product_index(kw, url, id) for kw in kw_list]
    await asyncio.gather(*tasks)

    return result
