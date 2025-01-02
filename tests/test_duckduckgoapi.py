from time import time

from haystack import Document
from unittest.mock import MagicMock
from duckduckgo_api_haystack import DuckduckgoApiWebSearch

class TestDuckduckgoApiWebSearch:

    def test_to_from_dict(self):
        component = DuckduckgoApiWebSearch(top_k=12, allowed_domain="test.com", timeout=20,
                                           use_answers=True, proxy="proxytest.com")
        data = component.to_dict()
        new_component = DuckduckgoApiWebSearch().from_dict(data)
        assert data == {'init_parameters': {'allowed_domain': 'test.com', 'backend': 'api', 'max_results': 10,
                                            'proxy': 'proxytest.com', 'region': 'wt-wt', 'safesearch': 'moderate',
                                            'timelimit': None, 'timeout': 20, 'top_k': 12, 'use_answers': True},
                        'type': 'duckduckgo_api_haystack.duckduckgoapi.DuckduckgoApiWebSearch'}
        assert data == new_component.to_dict()

    def test_search_no_answers(self):
        component = DuckduckgoApiWebSearch(top_k=12, timeout=20, use_answers=False)
        answer = component.run("What is frico?")
        assert isinstance(answer['documents'][0], Document)


    def test_rate_limiting(self):
        # Create an instance of DuckduckgoApiWebSearch with a rate limit of 1 search per second & testing it
        searcher = DuckduckgoApiWebSearch(max_search_frequency=1)

        searcher.ddgs.text = MagicMock(return_value=[{
                                             "title": "Mock Answer",
                                             "body" : "Mock",
                                             "href": "http://mockanswer.com"
                                                    }]
                                      )

        # Record the start time
        start_time = time()
        # The first search is immediate, the other 2 will have to wait
        for _ in range(3):
            searcher.run("test query")
        end_time = time()

        elapsed_time = end_time - start_time

        assert elapsed_time > 2, f"Expected at least 2 seconds to pass, but only {elapsed_time:.2f} seconds elapsed"

        print(f"Elapsed time: {elapsed_time:.2f} seconds")
