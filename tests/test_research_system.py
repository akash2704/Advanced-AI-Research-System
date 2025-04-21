import pytest
from unittest.mock import Mock, patch
from kairon.research_agent import ResearchAgent, ResearchState
from kairon.draft_agent import DraftAgent, DraftState
from kairon.quality_agent import QualityCheck
from kairon.orchestrator import ResearchOrchestrator
import os
from dotenv import load_dotenv

load_dotenv()

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

def test_research_agent_initialization(mock_gemini, mock_tavily):
    """Test that the research agent initializes correctly."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = ResearchAgent()
        assert agent is not None
        assert hasattr(agent, 'tools')
        assert hasattr(agent, 'agent_executor')

def test_research_state_creation():
    """Test that research state is created correctly."""
    state = ResearchState(research_question="Test question")
    assert state.research_question == "Test question"
    assert isinstance(state.gathered_information, list)
    assert len(state.gathered_information) == 0
    assert state.current_focus == ""
    assert state.iteration_count == 0

def test_research_agent_research(mock_gemini, mock_tavily):
    """Test the research process."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = ResearchAgent()
        state = agent.research("Test question", max_iterations=1)
        
        assert isinstance(state, ResearchState)
        assert state.research_question == "Test question"
        assert isinstance(state.gathered_information, list)
        assert len(state.gathered_information) > 0
        assert state.iteration_count == 1

def test_draft_agent_initialization(mock_gemini):
    """Test that the draft agent initializes correctly."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = DraftAgent()
        assert agent is not None
        assert hasattr(agent, 'chain')

def test_draft_agent_format_information():
    """Test the information formatting function."""
    agent = DraftAgent()
    test_info = [
        {"query": "test query 1", "result": "test result 1"},
        {"query": "test query 2", "result": "test result 2"}
    ]
    
    formatted = agent._format_information(test_info)
    assert "test query 1" in formatted
    assert "test result 1" in formatted
    assert "test query 2" in formatted
    assert "test result 2" in formatted

def test_draft_agent_revise_answer(mock_gemini):
    """Test the answer revision process."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = DraftAgent()
        test_draft = "Test draft"
        test_feedback = "Test feedback"
        
        revised = agent.revise_answer(test_draft, test_feedback)
        assert isinstance(revised, str)
        assert len(revised) > 0

def test_orchestrator_initialization(mock_gemini, mock_tavily):
    """Test that the orchestrator initializes correctly."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        orchestrator = ResearchOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, 'research_agent')
        assert hasattr(orchestrator, 'draft_agent')

def test_orchestrator_research_process(mock_gemini, mock_tavily):
    """Test the complete research process through the orchestrator."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):      
        orchestrator = ResearchOrchestrator()
        question = "What is the capital of France?"

        result = orchestrator.run_research(question)
        # The result is a tuple of (answer, quality_check)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)  # answer
        assert isinstance(result[1], QualityCheck)  # quality_check

def test_error_handling(mock_gemini, mock_tavily):
    """Test error handling in the research process."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        orchestrator = ResearchOrchestrator()
        
        # Test with empty question
        with pytest.raises(ValueError):
            orchestrator.run_research("")
        
        # Test with invalid question
        with pytest.raises(ValueError):
            orchestrator.run_research(None)

def test_research_agent_iteration_limit(mock_gemini, mock_tavily):
    """Test that the research agent respects iteration limits."""
    with patch('kairon.research_agent.TavilyClient', return_value=mock_tavily), \
         patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = ResearchAgent()
        state = agent.research("Test question", max_iterations=2)
        assert state.iteration_count <= 2

def test_draft_agent_with_empty_research(mock_gemini):
    """Test draft agent behavior with empty research results."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = DraftAgent()
        empty_state = ResearchState(research_question="Test question")
        
        with pytest.raises(ValueError):
            agent.draft_answer(empty_state)

if __name__ == "__main__":
    pytest.main([__file__]) 