# SPDX-FileCopyrightText: 2024 Giovanni Alzetta
# Based on the SerperDevWebSearch and SearchApiWebSearch classes from haystack:
# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from time import time, sleep
from typing import Any, Dict, List, Optional, Union

from duckduckgo_search import DDGS

from haystack import ComponentError, Document, component, default_from_dict, default_to_dict, logging

logger = logging.getLogger(__name__)

class DuckduckgoApiWebSearchError(ComponentError): ...


@component
class DuckduckgoApiWebSearch:
    """
    Uses [Duckduckgo](https://duckduckgo.com/) to search the web for relevant documents.

    This API is free so no need for secret keys and the like.

    Usage example:
    ```python
    from duckduckgo_api_haystack import DuckduckgoApiWebSearch

    websearch = DuckduckgoApiWebSearch(top_k=10)
    results = websearch.run(query="What is frico?")

    assert results["documents"]
    assert results["links"]
    ```
    """

    def __init__(
        self,
        top_k: Optional[int] = 10,
        max_results: Optional[int] = 10,
        region: str = "wt-wt",
        safesearch: str = "moderate",
        timelimit: Optional[str] = None,
        backend: str = "api",
        allowed_domain: str = "",
        timeout: int = 10,
        use_answers: bool = False,
        proxy: Optional[str] = None,
        max_search_frequency: float = float('inf')
    ):
        """
        Initialize the DuckduckgoWebSearch component.

        The parameters are used by the duckduckgo_search package: visit https://github.com/deedy5/duckduckgo_search
        for more details.

        Default configuration is fine to start.

        Remark: duckduckgo currently does not support the search operator "OR", thus it can look only on a single
        website.

        :param top_k: Maximum number of documents to return.
        :param max_results: Maximum number of documents to consider in the search.
        :param region: defaults to no region
        :param safesearch: Defaults to "moderate", other options: "on" and "off".
        :param timelimit: d, w, m. Defaults to None.
        :param backend: api, html, lite. Defaults to api.
        :param allowed_domain: search on a specific domain
        :param timeout: Timeout for each search request
        :param use_answers: (bool) Includes the answer search by duckduckgo. Defaults to False.
        :param proxy: web address to proxy
        :param max_search_frequency: Minimum time to pass between each search in seconds (defaults to no limit)
        """

        self.top_k = top_k
        self.max_results = max_results
        self.region = region
        self.safesearch = safesearch
        self.timelimit = timelimit
        self.backend = backend
        self.allowed_domain = allowed_domain
        self.timeout = timeout

        self.use_answers = use_answers

        self.search_params = {'max_results': self.max_results,
                              'region': self.region,
                              'safesearch': self.safesearch,
                              'timelimit': self.timelimit,
                              'backend': self.backend}

        self.proxy = proxy
        self.ddgs = DDGS(proxy=self.proxy)

        self.max_search_frequency = max_search_frequency
        self.last_search_time = 0

    def _rate_limit(self):
        """
        Implements rate limiting based on the max_searches_per_second parameter.
        """
        if self.max_search_frequency != float('inf'):
            current_time = time()
            time_since_last_search = current_time - self.last_search_time
            time_to_wait = max(0.0, self.max_search_frequency - time_since_last_search)
            if time_to_wait > 0:
                sleep(time_to_wait)
            self.last_search_time = time()


    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
              Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            top_k=self.top_k,
            max_results=self.max_results,
            region=self.region,
            safesearch=self.safesearch,
            timelimit=self.timelimit,
            backend=self.backend,
            allowed_domain=self.allowed_domain,
            timeout=self.timeout,
            use_answers=self.use_answers,
            proxy=self.proxy
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DuckduckgoApiWebSearch":
        """
        Deserializes the component from a dictionary.

        :param data:
            The dictionary to deserialize from.
        :returns:
                The deserialized component.
        """
        return default_from_dict(cls, data)

    @component.output_types(documents=List[Document], links=List[str])
    def run(self, query: str) -> Dict[str, Union[List[Document], List[str]]]:
        """
        Uses [Duckduckgo](https://duckduckgo.com/) to search the web.

        :param query: Search query.
        :returns: A dictionary with the following keys:
            - "documents": List of documents returned by the search engine.
            - "links": List of links returned by the search engine.
        :raises TimeoutError: If the request to the SearchApi API times out.
        :raises DuckDuckGoSearchException: If duckduckgo_search returns an error.
        :raises RatelimitException: Raised for exceeding API request rate limits.
        :raises TimeoutException: Raised for API request timeouts.
        """
        self._rate_limit() # If configured to do so, wait for the next search

        documents = []
        if self.use_answers:
            try:
                answers = self.ddgs.answers(query)
            except Exception as e:
                raise DuckduckgoApiWebSearchError(f"An error occurred while querying {self.__class__.__name__}."
                                               f"Error: {e}") from e
            for answer in answers:
                documents.append(
                    Document.from_dict({"title": '', "content": answer["text"], "link": answer["url"]})
                )

        query = f"site:{self.allowed_domain} {query}" if self.allowed_domain else query
        payload = {"keywords": query, **self.search_params}

        try:
            results = self.ddgs.text(**payload)
        except Exception as e:
            raise DuckduckgoApiWebSearchError(f"An error occurred while querying {self.__class__.__name__}."
                                           f"Error: {e}") from e

        # results is a list of dictionaries each with title, body, href,
        # converting them to Documents:

        for result in results:
            documents.append(
                Document.from_dict({"title": result["title"], "content": result["body"], "link": result["href"]})
            )

        # answer box has a direct answer to the query

        links = [result["href"] for result in results]

        logger.debug(
            "SearchApi returned {number_documents} documents for the query '{query}'",
            number_documents=len(documents),
            query=query,
        )
        return {"documents": documents[:self.top_k], "links": links[:self.top_k]}


if __name__ == '__main__':
    searcher = DuckduckgoApiWebSearch()
    print(searcher.run("What is frico"))