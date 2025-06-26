from pydantic import BaseModel
from typing import Any

# Tavily Search Response Schema
class SearchImage(BaseModel):
    url: str
    description: str | None = None

class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: float
    published_date: str | None = None
    raw_content: str | None = None

class TavilySearchResponse(BaseModel):
    query: str
    answer: str | None = None
    images: list[str | SearchImage] | None = None
    results: list[SearchResult]
    response_time: float
    auto_parameters: dict[str, Any] | None = None

# Tavily Extract Response Schema
class ExtractResult(BaseModel):
    url: str
    raw_content: str
    images: list[str]

class ExtractFailedResult(BaseModel):
    url: str
    error: str

class TavilyExtractResponse(BaseModel):
    results: list[ExtractResult]
    failed_results: list[ExtractFailedResult]
    response_time: float

# Tavily Crawl Response Schema
class CrawlResult(BaseModel):
    url: str
    raw_content: str

class TavilyCrawlResponse(BaseModel):
    base_url: str
    results: list[CrawlResult]
    response_time: float

# Tavily Map Response Schema
class TavilyMapResponse(BaseModel):
  base_url: str
  results: list[str]
  response_time: float
