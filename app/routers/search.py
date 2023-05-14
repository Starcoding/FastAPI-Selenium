from fastapi import APIRouter, status, Depends
from fastapi_pagination import Page, paginate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import FirefoxOptions

from sqlalchemy.ext.asyncio import AsyncSession
from pyvirtualdisplay import Display
from webdriver_manager.firefox import GeckoDriverManager

from app.database.dao.search_results import SearchResultDAO
from app.depends import get_db, get_driver
from app.schemas.search import (
    CreateSearchResult,
    ListSearchResult,
    MakeSearchRequest,
)


router = APIRouter(
    prefix="/search", tags=["search"], responses={404: {"description": "Not found"}}
)

opts = FirefoxOptions()
opts.add_argument("--headless")


@router.get(
    "/results", status_code=status.HTTP_200_OK, response_model=Page[ListSearchResult]
)
async def list_search_results(db: AsyncSession = Depends(get_db)):
    async with SearchResultDAO(db) as dao:
        return paginate(await dao.get_list())


@router.post(
    "/make_search",
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True,
)
async def make_search(
    request: MakeSearchRequest,
    db: AsyncSession = Depends(get_db),
    gecko_driver_path: str = Depends(get_driver),
) -> int:
    driver = webdriver.Firefox(executable_path=gecko_driver_path, options=opts)
    driver.get("https://www.google.com/")
    search_box = driver.find_element("name", "q")
    search_box.send_keys(request.search_text)
    search_box.submit()
    driver.implicitly_wait(3)
    elements = driver.find_elements("xpath", "//a/h3")
    links = [
        CreateSearchResult(
            url=element.find_element("xpath", "..").get_attribute("href"),
            name=element.text,
        )
        for element in elements
    ]
    created_search_results = []
    async with SearchResultDAO(db) as dao:
        created_search_results = await dao.create_items(links)
    result = len(created_search_results)
    return result
