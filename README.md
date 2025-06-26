# Tavily MCP Server

Tavily MCP Server implementation that uses fastmcp and supports both **sse** and **stdio** transports. To use this server, you need a Tavily account and a Tavily API key, which must be loaded into the `TAVILY_API_KEY` environment variable.

The Tavily MCP server provides:

- search, extract, map, crawl tools
- Real-time web search capabilities through the tavily-search tool
- Intelligent data extraction from web pages via the tavily-extract tool
- Powerful web mapping tool that creates a structured map of website
- Web crawler that systematically explores websites

# Prerequisites

- [git](https://git-scm.com/downloads) installed. (To clone the repo)
- [uv](https://github.com/astral-sh/uv) installed.
- [docker](https://docs.docker.com/engine/install/) installed (**Optional**: If you are planning to use the SSE server inside a docker container).

To install uv in Linux and MacOS type this in your terminal:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# Environment Variables

Copy the `.env.example` file and rename that to `.env`. Then paste your `TAVILY_API_KEY` inside there

```bash
TAVILY_API_KEY=<YOUR-API-KEY>
```
**Optional**: You can also configure the port if you are planning to use SSE.

```bash
TAVILY_MCP_PORT=<PORT>
```

# Running the SSE server

While inside the repo run:

```bash
uv run --env-file .env tavily-mcp-sse
```

# Running on STDIO

```json
{
  "mcpServers": {
    "tavily-mcp-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "<LOCATION-TO-THE-REPO>",
        "tavily-mcp-stdio"
      ],
      "env": {
        "TAVILY_API_KEY": "<YOUR-API-KEY>"
      }
    }
  }
}
```

# Docker SSE Server

First you need to build the image using the `Dockerfile` inside this repository. Run this to build the image:

```bash
docker build -t tavily-mcp .
```

Then you can run the container using the environment variables inside the env file

```bash
docker run --name tavily-mcp \
  -p 127.0.0.1:8000:8000 \
  --env-file .env \
  tavily-mcp
```

Or you can specify the environment variables yourself.

```bash
docker run --name tavily-mcp \
  -p 127.0.0.1:8000:8000 \
  -e TAVILY_API_KEY=<YOUR-API-KEY>
  tavily-mcp
```
