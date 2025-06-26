import logging
import os
import sys
from typing import Annotated, Any, Literal

import httpx
from fastmcp import FastMCP
from pydantic import Field
from .schemas import TavilyCrawlResponse, TavilyMapResponse, TavilySearchResponse

logging.basicConfig(level=logging.INFO)

TAVILY_MCP_PORT = os.getenv('TAVILY_MCP_PORT')

if TAVILY_MCP_PORT is None:
    tavily_port = 8000
else:
    try:
        tavily_port = int(TAVILY_MCP_PORT)
    except BaseException:
       tavily_port = 8000

mcp_server: FastMCP[None] = FastMCP(
    "tavily-mcp",
    port=tavily_port,
    host="0.0.0.0"
)

base_urls = {
    'search': 'https://api.tavily.com/search',
    'extract': 'https://api.tavily.com/extract',
    'crawl': 'https://api.tavily.com/crawl',
    'map': 'https://api.tavily.com/map'
}

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

if TAVILY_API_KEY is None:
    print("Tavily API KEY Does not exist!! ")
    sys.exit(-1)

headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'Authorization': f'Bearer {TAVILY_API_KEY}',
    'user-agent': 'tavily-mcp'
}

SearchDepthLiteral = Literal['basic', 'advanced']
ExtractDepthLiteral = Literal['basic', 'advanced']
TopicLiteral = Literal['general', 'news']
TimeRangeLiteral =  Literal['day', 'week', 'month', 'year', 'd', 'w', 'm', 'y'] | None
CountryLiteral =  Literal['afghanistan', 'albania', 'algeria', 'andorra', 'angola', 'argentina', 'armenia', 'australia', 'austria', 'azerbaijan', 'bahamas', 'bahrain', 'bangladesh', 'barbados', 'belarus', 'belgium', 'belize', 'benin', 'bhutan', 'bolivia', 'bosnia and herzegovina', 'botswana', 'brazil', 'brunei', 'bulgaria', 'burkina faso', 'burundi', 'cambodia', 'cameroon', 'canada', 'cape verde', 'central african republic', 'chad', 'chile', 'china', 'colombia', 'comoros', 'congo', 'costa rica', 'croatia', 'cuba', 'cyprus', 'czech republic', 'denmark', 'djibouti', 'dominican republic', 'ecuador', 'egypt', 'el salvador', 'equatorial guinea', 'eritrea', 'estonia', 'ethiopia', 'fiji', 'finland', 'france', 'gabon', 'gambia', 'georgia', 'germany', 'ghana', 'greece', 'guatemala', 'guinea', 'haiti', 'honduras', 'hungary', 'iceland', 'india', 'indonesia', 'iran', 'iraq', 'ireland', 'israel', 'italy', 'jamaica', 'japan', 'jordan', 'kazakhstan', 'kenya', 'kuwait', 'kyrgyzstan', 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya', 'liechtenstein', 'lithuania', 'luxembourg', 'madagascar', 'malawi', 'malaysia', 'maldives', 'mali', 'malta', 'mauritania', 'mauritius', 'mexico', 'moldova', 'monaco', 'mongolia', 'montenegro', 'morocco', 'mozambique', 'myanmar', 'namibia', 'nepal', 'netherlands', 'new zealand', 'nicaragua', 'niger', 'nigeria', 'north korea', 'north macedonia', 'norway', 'oman', 'pakistan', 'panama', 'papua new guinea', 'paraguay', 'peru', 'philippines', 'poland', 'portugal', 'qatar', 'romania', 'russia', 'rwanda', 'saudi arabia', 'senegal', 'serbia', 'singapore', 'slovakia', 'slovenia', 'somalia', 'south africa', 'south korea', 'south sudan', 'spain', 'sri lanka', 'sudan', 'sweden', 'switzerland', 'syria', 'taiwan', 'tajikistan', 'tanzania', 'thailand', 'togo', 'trinidad and tobago', 'tunisia', 'turkey', 'turkmenistan', 'uganda', 'ukraine', 'united arab emirates', 'united kingdom', 'united states', 'uruguay', 'uzbekistan', 'venezuela', 'vietnam', 'yemen', 'zambia', 'zimbabwe'] | None
FormatLiteral = Literal['markdown', 'text']
CrawlCategoriesLiteral = Literal['Careers', 'Blog', 'Documentation', 'About', 'Pricing', 'Community', 'Developers', 'Contact', 'Media']


@mcp_server.tool(name='tavily-search')
async def search(
    query: Annotated[str, Field(
        description="""The search query to execute with Tavily."""
    )],
    auto_parameters: Annotated[bool, Field(
        default=False,
        description="""Let Tavily automatically configure search parameter based on the querry. The explicit parameters will override the automatic ones."""
    )],
    topic: Annotated[TopicLiteral, Field(
        default='general',
        description="""The category of the search. This will determine which of our agents will be used for the search"""
    )],
    search_depth: Annotated[SearchDepthLiteral, Field(
        default='basic',
        description="""The depth of the search. It can be 'basic' or 'advanced'"""
    )],
    max_results: Annotated[int, Field(
        default=10,
        ge=5,
        le=20,
        description="""The maximum number of search results to return"""
    )],
    time_range: Annotated[TimeRangeLiteral, Field(
        default=None,
        description="""The time range back from the current date to include in the search results. This feature is available for both 'general' and 'news' search topics""")
    ],
    days: Annotated[int, Field(
        default=3,
        description="""The number of days back from the current date to include in the search results. This specifies the time frame of data to be retrieved. Please note that this feature is only available when using the 'news' search topic"""
    )],
    include_raw_content: Annotated[bool, Field(
        default=False,
        description="Include the cleaned and parsed HTML content of each search result",
    )],
    include_answer: Annotated[bool, Field(
        default=False,
        description="""Include an LLM-generated answer to the provided query"""
    )],
    include_images: Annotated[bool, Field(
        default=False,
        description="""Include a list of query-related images in the response"""
    )],
    include_image_descriptions: Annotated[bool, Field(
        default=False,
        description="""Include a list of query-related images and their descriptions in the response"""
    )],
    include_domains: Annotated[list[str], Field(
        default_factory=list,
        description="A list of domains to specifically include in the search results, if the user asks to search on specific sites set this to the domain of the site"
    )],
    exclude_domains: Annotated[list[str], Field(
        default_factory=list,
        description="List of domains to specifically exclude, if the user asks to exclude a domain set this to the domain of the site"
    )],
    country: Annotated[ CountryLiteral, Field(
        default=None,
        description="Boost search results from a specific country. This will prioritize content from the selected country in the search results. Available only if topic is general."
    )]
)  -> dict[str, Any]:
    """A powerful web search tool that provides comprehensive, real-time results using Tavily's AI search engine. Returns relevant web content with customizable parameters for result count, content type, and domain filtering. Ideal for gathering current information, news, and detailed web content analysis."""

    if country is not None:
        topic = 'general'
    endpoint: str = base_urls["search"]
    search_params = {
        "query": query,
        "auto_parameters": auto_parameters,
        "search_depth": search_depth,
        "topic": topic,
        "days": days,
        "time_range": time_range,
        "max_results": max_results,
        "include_answer": include_answer,
        "include_images": include_images,
        "include_image_descriptions": include_image_descriptions,
        "include_raw_content": include_raw_content,
        "include_domains": include_domains,
        "exclude_domains": exclude_domains,
        "country": country,
        "api_key": TAVILY_API_KEY,
    }
    try:
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.post(endpoint, json=search_params)
            if not response.is_success:
                if response.status_code == 401:
                    raise ValueError("Invalid API Key")
                elif response.status_code == 429:
                    raise ValueError("Usage limit exceeded")
                _ = response.raise_for_status()

    except BaseException as e:
        raise e

    response_dict: dict[str, Any] = response.json()
    return  TavilySearchResponse.model_validate(response_dict).model_dump()

@mcp_server.tool(name='tavily-extract')
async def extract(
    urls: Annotated[list[str], Field(
        description="List of URLs to extract content from"
    )],
    extract_depth: Annotated[ExtractDepthLiteral, Field(
        default="basic",
        description="Depth of extraction - 'basic' or 'advanced', if urls are linkedin use 'advanced' or if explicitly told to use advanced"
    )],
    include_images: Annotated[bool, Field(
        default=False,
        description="Include a list of images extracted from the urls in the response"
    )],
    format: Annotated[FormatLiteral, Field(
        default='markdown',
        description="The format of the extracted web page content. markdown returns content in markdown format. text returns plain text and may increase latency."
    )]
) -> dict[str, Any]:
    """A powerful web content extraction tool that retrieves and processes raw content from specified URLs, ideal for data collection, content analysis, and research tasks."""
    endpoint = base_urls['extract']

    search_params = {
        "urls": urls,
        "extract_depth": extract_depth,
        "include_images": include_images,
        "format": format,
        "api_key": TAVILY_API_KEY,
    }

    try:
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.post(endpoint, json=search_params)
            if not response.is_success:
                if response.status_code == 401:
                    raise ValueError("Invalid API Key")
                elif response.status_code == 429:
                    raise ValueError("Usage limit exceeded")
                _ = response.raise_for_status()

    except BaseException as e:
        raise e

    response_dict: dict[str, Any] = response.json()
    return response_dict
    # return  TavilyResponse.model_validate(response_dict).model_dump()

@mcp_server.tool(name='tavily-crawl')
async def crawl(
    url: Annotated[str, Field(
        description="""Root URL to begin the crawl"""
    )],
    instructions: Annotated[str, Field(
        description="""Natural language instructions for the crawler"""
    )],
    max_depth: Annotated[int, Field(
        default=1,
        ge=1,
        description="""Max depth of the crawl. Defines how far from the base URL the crawler can explore."""
    )],
    max_breadth: Annotated[int, Field(
        default=20,
        ge=1,
        description="""Max number of links to follow per level of the tree (i.e., per page)"""
    )],
    limit: Annotated[int, Field(
        default=50,
        ge=1,
        description="""Total number of links the crawler will process before stopping"""
    )],
    select_paths: Annotated[list[str], Field(
        default_factory=list,
        description="""Regex patterns to select only URLs with specific path patterns (e.g., /docs/.*, /api/v1.*)"""
    )],
    select_domains: Annotated[list[str], Field(
        default_factory=list,
        description="""Regex patterns to select crawling to specific domains or subdomains (e.g., ^docs\\.example\\.com$)"""
    )],
    allow_external: Annotated[bool, Field(
        default=False,
        description="""Whether to allow following links that go to external domains"""
    )],
    categories: Annotated[list[CrawlCategoriesLiteral], Field(
        default_factory=list,
        description="""Filter URLs using predefined categories like documentation, blog, api, etc"""
    )],
    extract_depth: Annotated[ExtractDepthLiteral, Field(
        default="basic",
        description="Advanced extraction retrieves more data, including tables and embedded content, with higher success but may increase latency"
    )],
    format: Annotated[FormatLiteral, Field(
        default="markdown",
        description="""The format of the extracted web page content. markdown returns content in markdown format. text returns plain text and may increase latency."""
    )]
) -> dict[str, Any]:
    """A powerful web crawler that initiates a structured web crawl starting from a specified base URL. The crawler expands from that point like a tree, following internal links across pages. You can control how deep and wide it goes, and guide it to focus on specific sections of the site."""
    endpoint = base_urls['crawl']
    search_params = {
        "url": url,
        "instructions": instructions,
        "max_depth": max_depth,
        "max_breadth": max_breadth,
        "limit": limit,
        "select_paths": select_paths,
        "select_domains": select_domains,
        "allow_external": allow_external,
        "categories": categories,
        "extract_depth": extract_depth,
        "format": format,
        "api_key": TAVILY_API_KEY,
    }
    try:
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.post(endpoint, json=search_params)
            if not response.is_success:
                if response.status_code == 401:
                    raise ValueError("Invalid API Key")
                elif response.status_code == 429:
                    raise ValueError("Usage limit exceeded")
                _ = response.raise_for_status()

    except BaseException as e:
        raise e

    response_dict: dict[str, Any] = response.json()
    return  TavilyCrawlResponse.model_validate(response_dict).model_dump()


@mcp_server.tool(name='tavily-map')
async def map(
    url: Annotated[str, Field(
        description="""Root URL to begin the mapping"""
    )],
    instructions: Annotated[str, Field(
        description="""Natural language instructions for the crawler"""
    )],
    max_depth: Annotated[int, Field(
        default=1,
        ge=1,
        description="""Max depth of the mapping. Defines how far from the base URL the crawler can explore"""
    )],
    max_breadth: Annotated[int, Field(
        default=20,
        ge=1,
        description="""Max number of links to follow per level of the tree (i.e., per page)"""
    )],
    limit: Annotated[int, Field(
        default=50,
        ge=1,
        description="""Total number of links the crawler will process before stopping"""
    )],
    select_paths: Annotated[list[str], Field(
        default_factory=list,
        description="""Regex patterns to select only URLs with specific path patterns (e.g., /docs/.*, /api/v1.*)"""
    )],
    select_domains: Annotated[list[str], Field(
        default_factory=list,
        description="""Regex patterns to select crawling to specific domains or subdomains (e.g., ^docs\\.example\\.com$)"""
    )],
    allow_external: Annotated[bool, Field(
        default=False,
        description="""Whether to allow following links that go to external domains"""
    )],
    categories: Annotated[list[CrawlCategoriesLiteral], Field(
        default_factory=list,
        description="""Filter URLs using predefined categories like documentation, blog, api, etc"""
    )],
) -> dict[str, Any]:
    """A powerful web mapping tool that creates a structured map of website URLs, allowing you to discover and analyze site structure, content organization, and navigation paths. Perfect for site audits, content discovery, and understanding website architecture."""
    endpoint = base_urls['map']
    search_params = {
        "url": url,
        "instructions": instructions,
        "max_depth": max_depth,
        "max_breadth": max_breadth,
        "limit": limit,
        "select_paths": select_paths,
        "select_domains": select_domains,
        "allow_external": allow_external,
        "categories": categories,
        "api_key": TAVILY_API_KEY,
    }

    try:
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.post(endpoint, json=search_params)
            if not response.is_success:
                if response.status_code == 401:
                    raise ValueError("Invalid API Key")
                elif response.status_code == 429:
                    raise ValueError("Usage limit exceeded")
                _ = response.raise_for_status()

    except BaseException as e:
        raise e

    response_dict: dict[str, Any] = response.json()
    return TavilyMapResponse.model_validate(response_dict).model_dump()

async def run_server(transport_method: Literal['sse', 'stdio']):
    print(f'Running the server using the transport {transport_method}')
    await mcp_server.run_async(
        transport=transport_method
    )
