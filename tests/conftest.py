import pytest
from unittest.mock import Mock, patch
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session")
def mock_ollama():
    """Mock Ollama LLM for all tests."""
    with patch('langchain_community.llms.Ollama') as mock:
        mock_instance = Mock()
        mock_instance.invoke.return_value = "Mocked response"
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture(scope="session")
def mock_tavily():
    """Mock Tavily search for all tests."""
    with patch('langchain.tools.tavily_search.TavilySearchResults') as mock:
        mock_instance = Mock()
        mock_instance.run.return_value = [
            {
                "title": "Test Result",
                "content": "Test content",
                "url": "http://test.com"
            }
        ]
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_research_state():
    """Create a sample research state for testing."""
    from kairon.research_agent import ResearchState
    return ResearchState(
        research_question="Test question",
        gathered_information=[
            {
                "query": "test query",
                "result": "test result"
            }
        ],
        current_focus="test focus",
        iteration_count=1
    )

@pytest.fixture
def sample_draft_state(sample_research_state):
    """Create a sample draft state for testing."""
    from kairon.draft_agent import DraftState
    return DraftState(
        research_state=sample_research_state,
        current_draft="Test draft",
        revision_count=0
    ) 