import pytest
from unittest.mock import Mock, patch
from kairon.research_agent import ResearchAgent, ResearchState
from tavily import TavilyClient

@pytest.fixture
def mock_gemini():
    with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock:
        mock_instance = Mock()
        mock_instance.invoke.return_value.content = "Mocked response"
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_tavily():
    with patch('tavily.TavilyClient') as mock:
        mock_instance = Mock()
        mock_instance.search.return_value = {
            "results": [
                {"title": "Test Result", "content": "Test content", "url": "http://test.com"}
            ]
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_agent():
    with patch('langchain.agents.create_openai_functions_agent') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_agent_executor():
    with patch('langchain.agents.AgentExecutor') as mock:
        mock_instance = Mock()
        mock_instance.invoke.return_value = {"output": "Mocked research output"}
        mock.return_value = mock_instance
        yield mock_instance

def test_research_agent_initialization(mock_gemini, mock_tavily, mock_agent, mock_agent_executor):
    """Test that the research agent initializes correctly."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini), \
         patch('langchain.agents.create_openai_functions_agent', return_value=mock_agent), \
         patch('langchain.agents.AgentExecutor', return_value=mock_agent_executor):
        agent = ResearchAgent()
        assert agent is not None
        assert hasattr(agent, 'llm')
        assert hasattr(agent, 'tools')
        assert hasattr(agent, 'agent_executor')

def test_research_agent_research(mock_gemini, mock_tavily, mock_agent, mock_agent_executor):
    """Test the research method."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini), \
         patch('langchain.agents.create_openai_functions_agent', return_value=mock_agent), \
         patch('langchain.agents.AgentExecutor', return_value=mock_agent_executor):
        agent = ResearchAgent()
        question = "What are the latest developments in quantum computing?"
        
        state = agent.research(question, max_iterations=1)
        assert isinstance(state, ResearchState)
        assert state.research_question == question
        assert len(state.gathered_information) > 0
        assert state.iteration_count == 1



def test_research_agent_with_invalid_question(mock_gemini, mock_tavily, mock_agent, mock_agent_executor):
    """Test research with invalid question."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini), \
         patch('langchain.agents.create_openai_functions_agent', return_value=mock_agent), \
         patch('langchain.agents.AgentExecutor', return_value=mock_agent_executor):
        agent = ResearchAgent()
        
        with pytest.raises(ValueError):
            agent.research(None)

def test_research_agent_max_iterations(mock_gemini, mock_tavily, mock_agent, mock_agent_executor):
    """Test that the research agent respects iteration limits."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini), \
         patch('langchain.agents.create_openai_functions_agent', return_value=mock_agent), \
         patch('langchain.agents.AgentExecutor', return_value=mock_agent_executor):
        agent = ResearchAgent()
        state = agent.research("Test question", max_iterations=2)
        assert state.iteration_count <= 2



def test_research_state_validation():
    """Test ResearchState validation."""
    state = ResearchState(
        research_question="Test research question",
        gathered_information=[
            {"source": "test source", "content": "test content"}
        ],
        current_focus="test focus",
        iteration_count=1
    )
    assert state.research_question == "Test research question"
    assert len(state.gathered_information) == 1
    assert state.current_focus == "test focus"
    assert state.iteration_count == 1

def test_research_state_with_empty_data():
    """Test ResearchState with empty data."""
    state = ResearchState(research_question="Test question")
    assert state.research_question == "Test question"
    assert len(state.gathered_information) == 0
    assert state.current_focus == ""
    assert state.iteration_count == 0 