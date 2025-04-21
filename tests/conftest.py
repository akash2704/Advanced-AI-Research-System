import pytest
from unittest.mock import MagicMock, patch
from kairon.draft_agent import DraftAgent, DraftState
from kairon.quality_agent import QualityAgent, QualityCheck
from kairon.research_agent import ResearchAgent, ResearchState
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient

@pytest.fixture
def mock_gemini_llm():
    """Mock Gemini LLM for testing."""
    mock = MagicMock(spec=ChatGoogleGenerativeAI)
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = MagicMock(content="Mocked response")
    mock.return_value = mock_instance
    return mock

@pytest.fixture
def mock_tavily_client():
    """Mock Tavily client for testing."""
    mock = MagicMock(spec=TavilyClient)
    mock_instance = MagicMock()
    mock_instance.search.return_value = {
        "results": [
            {
                "title": "Test Source",
                "url": "https://example.com",
                "content": "Test content"
            }
        ]
    }
    mock.return_value = mock_instance
    return mock

@pytest.fixture
def research_state():
    """Create a test research state."""
    return ResearchState(
        research_question="What are the latest developments in quantum computing?",
        gathered_information=[
            {
                "source": "https://example.com",
                "content": "Quantum computing is advancing rapidly with new breakthroughs in qubit stability."
            }
        ]
    )

@pytest.fixture
def draft_state(research_state):
    """Create a test draft state."""
    return DraftState(
        research_state=research_state,
        current_draft="Test draft content",
        revision_count=0
    )

@pytest.fixture
def quality_check():
    """Create a test quality check."""
    return QualityCheck(
        fact_accuracy=0.9,
        consistency_score=0.85,
        bias_detected=False,
        readability_score=0.8,
        issues=[],
        suggestions=["Test suggestion"]
    )

@pytest.fixture
def draft_agent(mock_gemini_llm):
    """Create a DraftAgent instance with mocked dependencies."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini_llm):
        return DraftAgent()

@pytest.fixture
def quality_agent(mock_gemini_llm):
    """Create a QualityAgent instance with mocked dependencies."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini_llm):
        return QualityAgent()

@pytest.fixture
def research_agent(mock_gemini_llm, mock_tavily_client):
    """Create a ResearchAgent instance with mocked dependencies."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini_llm), \
         patch('tavily.TavilyClient', return_value=mock_tavily_client):
        return ResearchAgent() 