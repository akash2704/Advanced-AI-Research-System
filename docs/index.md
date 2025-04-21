# Welcome to Kairon

Kairon is an AI-powered research assistant that helps gather, analyze, and present information on complex topics. It uses a combination of web search, language models, and quality checks to provide well-researched and accurate answers.

## Features

- **Research Agent**: Gathers and analyzes information from the web
- **Draft Agent**: Creates well-structured answers based on research
- **Quality Agent**: Ensures accuracy and quality of the content
- **Orchestrator**: Coordinates the entire research and drafting process

## Quick Start

1. Install Kairon:
```bash
pip install kairon
```

2. Set up your API keys:
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
export TAVILY_API_KEY="your_tavily_api_key"
```

3. Use Kairon:
```python
from kairon.orchestrator import ResearchOrchestrator

orchestrator = ResearchOrchestrator()
question = "What are the latest developments in quantum computing?"
answer, quality_check = orchestrator.run_research(question)
```

## Documentation

- [Installation](installation.md)
- [Usage Guide](usage.md)
- [API Reference](api/)
- [Contributing](contributing.md)

## Support

For support, please:
1. Check the [documentation](https://yourusername.github.io/kairon)
2. Open an [issue](https://github.com/yourusername/kairon/issues)
3. Contact the maintainers 