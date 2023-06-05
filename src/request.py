from bs4 import BeautifulSoup, ResultSet, Tag
import requests


def get_page(url: str) -> BeautifulSoup:
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")


def select_one(soup: BeautifulSoup | Tag, selector: str) -> Tag:
    result = soup.select_one(selector)
    if result is None:
        raise RuntimeError(f"No matches for {selector}")
    return result


def select_all(soup: BeautifulSoup | Tag, selector: str) -> ResultSet[Tag]:
    result = soup.select(selector)
    if result is None:
        raise RuntimeError(f"No matches for {selector}")
    return result


def get_href(tag: Tag) -> str:
    href = tag.get_attribute_list("href")
    if href is None:
        raise RuntimeError(f"No href in {tag}")
    return href[0]


def get_id(tag: Tag) -> str:
    id = tag.get_attribute_list("id")
    if id is None:
        raise RuntimeError(f"No id in {tag}")
    return id[0]
