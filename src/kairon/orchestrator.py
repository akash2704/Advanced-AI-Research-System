from typing import Dict, Any, Optional, Tuple
from langgraph.graph import Graph, END
from .research_agent import ResearchAgent, ResearchState
from .draft_agent import DraftAgent, DraftState
from .quality_agent import QualityAgent, QualityCheck
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'kairon_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResearchOrchestrator:
    def __init__(self):
        """Initialize the research orchestrator with all agents."""
        self.research_agent = ResearchAgent()
        self.draft_agent = DraftAgent()
        self.quality_agent = QualityAgent()
        logger.info("Initialized ResearchOrchestrator with all agents")
        
        # Define the workflow
        self.workflow = Graph()
        
        # Add nodes
        self.workflow.add_node("research", self._conduct_research)
        self.workflow.add_node("draft", self._draft_answer)
        self.workflow.add_node("revise", self._revise_answer)
        
        # Define edges
        self.workflow.add_edge("research", "draft")
        self.workflow.add_edge("draft", "revise")
        self.workflow.add_edge("revise", END)
        
        # Set entry point
        self.workflow.set_entry_point("research")
        
        # Compile the graph
        self.app = self.workflow.compile()
    
    def _conduct_research(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct research using the research agent."""
        research_state = self.research_agent.research(state["question"])
        return {"research_state": research_state}
    
    def _draft_answer(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Draft an answer using the draft agent."""
        draft = self.draft_agent.draft_answer(state["research_state"])
        return {"draft": draft, "research_state": state["research_state"]}
    
    def _revise_answer(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Revise the answer if needed."""
        final_answer = self.draft_agent.revise_answer(
            state["draft"],
            "Please ensure the answer is clear, well-structured, and directly addresses the research question."
        )
        return {"final_answer": final_answer}
    
    def run_research(self, question: str, max_iterations: int = 3) -> Tuple[str, QualityCheck]:
        """
        Run the complete research and drafting process with quality checks.
        
        Args:
            question: The research question to investigate
            max_iterations: Maximum number of research iterations
            
        Returns:
            Tuple[str, QualityCheck]: The final answer and quality check results
        """
        if not question or not isinstance(question, str):
            raise ValueError("Question must be a non-empty string")
        
        logger.info(f"Starting research process for question: {question}")
        
        try:
            # Conduct research
            research_state = self.research_agent.research(
                question=question,
                max_iterations=max_iterations
            )
            logger.info(f"Research completed with {len(research_state.gathered_information)} sources")
            
            # Create initial draft
            draft = self.draft_agent.draft_answer(research_state)
            logger.info("Initial draft created")
            
            # Perform quality checks
            quality_check = self.quality_agent.check_content(
                content=draft,
                sources=research_state.gathered_information
            )
            logger.info(f"Quality check completed with accuracy score: {quality_check.fact_accuracy}")
            
            # Revise if necessary
            if quality_check.fact_accuracy < 0.7 or quality_check.bias_detected:
                logger.info("Revising draft based on quality check results")
                feedback = "\n".join(quality_check.issues + quality_check.suggestions)
                draft = self.draft_agent.revise_answer(draft, feedback)
            
            # Create final draft state
            draft_state = DraftState(
                research_state=research_state.model_dump(),
                current_draft=draft
            )
            
            logger.info("Research process completed successfully")
            return draft_state.current_draft, quality_check
            
        except Exception as e:
            logger.error(f"Error in research process: {str(e)}")
            raise
    
    def revise_answer(self, current_draft: str, feedback: str) -> str:
        """
        Revise the current draft based on feedback.
        
        Args:
            current_draft: The current version of the answer
            feedback: Feedback to incorporate into the revision
            
        Returns:
            str: The revised answer
        """
        logger.info("Revising answer based on feedback")
        return self.draft_agent.revise_answer(current_draft, feedback)

def main():
    # Example usage
    try:
        orchestrator = ResearchOrchestrator()
        question = "What are the latest developments in quantum computing?"
        answer, quality_check = orchestrator.run_research(question)
        
        print("\nResearch Question:", question)
        print("\nAnswer:", answer)
        print("\nQuality Check Results:")
        print(f"Fact Accuracy: {quality_check.fact_accuracy:.2f}")
        print(f"Readability Score: {quality_check.readability_score:.2f}")
        print(f"Bias Detected: {'Yes' if quality_check.bias_detected else 'No'}")
        if quality_check.issues:
            print("\nIssues Found:")
            for issue in quality_check.issues:
                print(f"- {issue}")
        if quality_check.suggestions:
            print("\nSuggestions:")
            for suggestion in quality_check.suggestions:
                print(f"- {suggestion}")
                
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main() 