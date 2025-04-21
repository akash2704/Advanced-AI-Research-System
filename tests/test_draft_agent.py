import pytest
from unittest.mock import Mock, patch
from kairon.draft_agent import DraftAgent, DraftState
from kairon.research_agent import ResearchState

@pytest.fixture
def mock_gemini():
    with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock:
        mock_instance = Mock()
        mock_instance.invoke.return_value.content = "Mocked response"
        mock.return_value = mock_instance
        yield mock_instance

def test_draft_agent_initialization(mock_gemini):
    """Test that the draft agent initializes correctly."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = DraftAgent()
        assert agent is not None
        assert hasattr(agent, 'llm')

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

def test_draft_agent_with_empty_research(mock_gemini):
    """Test draft agent behavior with empty research results."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = DraftAgent()
        empty_state = ResearchState(research_question="Test question")
        
        with pytest.raises(ValueError):
            agent.draft_answer(empty_state)

def test_draft_state_validation():
    """Test DraftState validation."""
    state = DraftState(
        research_state=ResearchState(research_question="Test question"),
        current_draft="Test draft",
        revision_count=0
    )
    assert state.research_state.research_question == "Test question"
    assert state.current_draft == "Test draft"
    assert state.revision_count == 0 