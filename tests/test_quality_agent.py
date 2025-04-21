import pytest
from unittest.mock import Mock, patch
from kairon.quality_agent import QualityAgent, QualityCheck
from kairon.research_agent import ResearchState

@pytest.fixture
def mock_gemini():
    with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock:
        mock_instance = Mock()
        mock_instance.invoke.return_value.content = """{
            "fact_accuracy": 0.9,
            "consistency_score": 0.85,
            "bias_detected": false,
            "readability_score": 0.8,
            "issues": [],
            "suggestions": []
        }"""
        mock.return_value = mock_instance
        yield mock_instance

def test_quality_agent_initialization(mock_gemini):
    """Test that the quality agent initializes correctly."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = QualityAgent()
        assert agent is not None
        assert hasattr(agent, 'llm')

def test_quality_agent_check_content(mock_gemini):
    """Test the check_content method."""
    with patch('langchain_google_genai.ChatGoogleGenerativeAI', return_value=mock_gemini):
        agent = QualityAgent()
        content = "Test content"
        sources = [{"source": "test source", "content": "test content"}]
        
        result = agent.check_content(content, sources)
        assert isinstance(result, QualityCheck)
        assert result.fact_accuracy >= 0.0
        assert result.consistency_score >= 0.0
        assert not result.bias_detected
        assert result.readability_score >= 0.0
        assert isinstance(result.issues, list)
        assert isinstance(result.suggestions, list)
        assert len(result.suggestions) > 0

def test_quality_check_validation():
    """Test QualityCheck validation."""
    check = QualityCheck(
        fact_accuracy=0.9,
        consistency_score=0.85,
        bias_detected=False,
        readability_score=0.8,
        issues=[],
        suggestions=[]
    )
    assert check.fact_accuracy == 0.9
    assert check.consistency_score == 0.85
    assert not check.bias_detected
    assert check.readability_score == 0.8
    assert isinstance(check.issues, list)
    assert isinstance(check.suggestions, list)

def test_quality_check_with_bias():
    """Test QualityCheck with bias detected."""
    check = QualityCheck(
        fact_accuracy=0.8,
        consistency_score=0.7,
        bias_detected=True,
        readability_score=0.9,
        issues=["Potential bias detected"],
        suggestions=["Consider multiple perspectives"]
    )
    assert check.bias_detected
    assert "Potential bias detected" in check.issues

def test_quality_check_with_low_scores():
    """Test QualityCheck with low scores."""
    check = QualityCheck(
        fact_accuracy=0.3,
        consistency_score=0.4,
        bias_detected=False,
        readability_score=0.5,
        issues=["Low fact accuracy", "Low consistency"],
        suggestions=["Verify sources", "Improve consistency"]
    )
    assert check.fact_accuracy < 0.5
    assert check.consistency_score < 0.5
    assert check.readability_score < 0.6 