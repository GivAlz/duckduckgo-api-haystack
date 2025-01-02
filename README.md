# DuckduckgoApiWebSearch

Haystack component to use Websearch via the freely available Duckduckgo API.

-----

**Table of Contents**

- [Installation](#Installation)
- [Overview](#Overview)
- [Basic Usage](#Basic_Usage)
- [License](#License)

## Installation

```console
pip install duckduckgo-api-haystack
```

## Overview

This repository implements a module in the style of **SearchApiWebSearch**
and **SerperDevWebSearch**, but using the freely-available duckduckgo API.

When you give DuckduckgoWebSearch a query, it returns a list of the URLs most relevant to your search.
It uses page snippets (pieces of text displayed under the page title in search results) to find the answers,
not the whole pages.

## Basic Usage

Here's a simple example of how to use the `DuckduckgoApiWebSearch` component:

```python
from duckduckgo_api_haystack import DuckduckgoApiWebSearch

# Create an instance of DuckduckgoApiWebSearch
websearch = DuckduckgoApiWebSearch(top_k=3)

# Perform a search
results = websearch.run(query="What is frico?")

# Access the search results
documents = results["documents"]
links = results["links"]

print("Found documents:")
for doc in documents:
    print(f"Content: {doc.content}")
    print("\n\n")

print("Search Links:")
for link in links:
    print(link)
```

### Configuration Parameters

The `DuckduckgoApiWebSearch` component accepts several parameters to customize its behavior:

- `top_k (int, optional)`: Maximum number of documents to return (default: 10).
- `max_results (int, optional)`: Maximum number of documents to consider in the search (default: 10).
- `region (str)`: Search region (default: "wt-wt" for worldwide).
- `safesearch (str)`: SafeSearch setting ("on", "moderate", or "off"; default: "moderate").
- `timelimit (str, optional)`: Time limit for search results (e.g., "d" for day, "w" for week, "m" for month).
- `backend (str)`: Search backend to use ("api", "html", or "lite"; default: "api").
- `allowed_domain (str)`: Restrict search to a specific domain (default: "").
- `timeout (int)`: Timeout for each search request in seconds (default: 10).
- `use_answers (bool)`: Include DuckDuckGo's answer box in results (default: False).
- `proxy (str, optional)`: Web address to use as a proxy.
- `max_search_frequency (float, optional)`: Minimum time in seconds between searches (defaults to no limit)

Remark: The difference between `top_k` and `max_results` is that, if `use_answers` is `True`, then the number of
answers and pages is considered together and only the `top_k` are then used. Otherwise they work in the same way.

The `top_k` and `max_results` parameters serve different purposes:

`max_results`: This parameter determines the maximum number of search results to retrieve from DuckDuckGo.
`top_k`: This parameter limits the number of results returned by the component.

The interaction between these parameters depends on the `use_answers` setting:

- `use_answers=False`: The component retrieves up to max_results search results.
- `use_answers=True`: The component returns the `top_k` results from a list containing answers and search results.

## Rate Limitations

Too many requests could cause the API to fail because of rate limitations; to fix this issue use a proxy or reduce 
the frequency of the calls.

## License

`duckduckgo-api-websearch` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

