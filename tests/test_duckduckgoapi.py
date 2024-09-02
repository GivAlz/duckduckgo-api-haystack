from duckduckgo_api_haystack import DuckduckgoApiWebSearch

from haystack import Document

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