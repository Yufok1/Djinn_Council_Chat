# 🌂 Djinn Council Chat - Mystical Multi-Agent AI Orchestration

> *"Command legions of AI djinn in mystical council - where collective intelligence meets ethereal beauty"*

A sophisticated multi-agent AI orchestration system that coordinates multiple AI models (djinn) to provide comprehensive, multi-perspective responses through an enchanting graphical interface.

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Ollama](https://img.shields.io/badge/ollama-required-orange.svg)

## ✨ Features

### 🎭 **Multi-Agent Council System**
- **6 Specialized AI Djinn**: Each with unique roles and expertise
  - 🧙‍♂️ **Strategist**: Long-term planning and recursive analysis
  - 📊 **Analyst**: Technical breakdowns and data analysis
  - ⚖️ **Arbiter**: Conflict resolution and balanced judgment
  - 🛡️ **Guardian**: Risk assessment and security analysis
  - 🏗️ **Architect**: System design and implementation frameworks
  - 📚 **Historian**: Historical context and precedent analysis

### 🌌 **Advanced Consensus Algorithms**
- **Majority Vote**: Democratic decision-making
- **Confidence Scoring**: Expertise-based selection
- **Weighted Roles**: Hierarchical authority system
- **Deliberative Loop**: Iterative refinement
- **Hybrid**: Multiple perspective presentation

### 🎨 **Mystical GUI Experience**
- **Dark Arcane Theme**: Stunning ethereal aesthetics
- **Live Thinking Visualization**: See AI models contemplate in real-time
- **Typewriter Layout**: Organized response display
- **Crystalline Confidence Indicators**: Visual confidence levels
- **Unlimited Thinking Time**: Models can think as long as needed

### 🧠 **Advanced Memory System**
- **Persistent Conversations**: Across all sessions
- **User Profile Learning**: Adapts to your preferences
- **Conversation Summarization**: Intelligent context management
- **Cross-Model Memory**: Shared context for all djinn

### 🔒 **Enterprise-Grade Features**
- **Security Safeguards**: Prompt injection detection
- **Integrity Monitoring**: Response validation
- **State Machine Architecture**: Robust session management
- **Performance Optimization**: Persistent worker threads

## 🚀 Quick Start

### Prerequisites

1. **Python 3.7+** installed
2. **Ollama** installed and running
   ```bash
   # Install Ollama (visit https://ollama.ai for instructions)
   ollama --version
   
   # Pull at least one model
   ollama pull llama3.2:latest
   ```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Yufok1/Djinn_Council_Chat.git
   cd Djinn_Council_Chat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the mystical interface**
   ```bash
   python djinn_council_gui_enhanced.py
   ```

## 📖 Usage Guide

### Basic Operation

1. **Start the GUI**: Run `python djinn_council_gui_enhanced.py`
2. **Configure Models**: Assign Ollama models to each djinn role
3. **Select Consensus Mode**: Choose how the council reaches decisions
4. **Ask Questions**: Type your query and click "INVOKE COUNCIL"
5. **Watch the Magic**: Observe live thinking processes and mystical responses

### Advanced Features

#### Model Assignment
- Each djinn can use a different Ollama model
- Supports advanced models like DeepSeek with thinking capabilities
- Automatic model detection and validation

#### Consensus Modes
- **Weighted Roles**: Balanced hierarchy (Recommended)
- **Confidence Scoring**: Trust the most confident
- **Majority Vote**: Democratic consensus
- **Hybrid**: See all perspectives
- **Deliberative Loop**: Multi-round discussion

#### Memory Management
- **View Stats**: Check conversation history and user profile
- **Clear Memory**: Reset conversation (keeping or removing profile)
- **Persistent Learning**: System remembers your preferences

### Command Line Interface

For advanced users, direct CLI access is available:

```bash
# Advanced council with full CISM
python advanced_djinn_council.py "Your question here"

# With specific consensus mode
python advanced_djinn_council.py --mode majority_vote "Your question"

# System status
python advanced_djinn_council.py --status
```

## 🏗️ Architecture

### Core Components

1. **Advanced Djinn Council** (`advanced_djinn_council.py`)
   - Council Invocation State Machine (CISM)
   - Integrity safeguards and security
   - Advanced consensus algorithms
   - Performance optimizations

2. **GUI Interface** (`djinn_council_gui_enhanced.py`)
   - Mystical visual interface
   - Live thinking visualization
   - Real-time orchestration
   - Configuration management

3. **Conversational Memory** (`conversational_memory.py`)
   - Persistent memory system
   - User profile learning
   - Context management
   - Conversation summarization

### Data Flow

1. **Query Input** → Security validation → Context enrichment
2. **Parallel Execution** → All djinn process simultaneously
3. **Response Collection** → Confidence scoring → Integrity checks
4. **Consensus Algorithm** → Final response generation
5. **Memory Storage** → User profile updates → Session logging

## 🔧 Configuration

### Model Configuration
Models are configured in `advanced_djinn_config.json`:

```json
{
  "roles": {
    "strategist": {
      "model_name": "llama3.2:latest",
      "priority_weight": 1.2,
      "confidence_threshold": 0.8
    }
  }
}
```

### Security Settings
- Prompt injection detection
- Input sanitization
- Command whitelisting
- Pattern blocking

### Performance Tuning
- Concurrent session limits
- Context truncation
- Unlimited thinking time
- Worker thread management

## 🛡️ Security Features

- **Prompt Injection Detection**: Advanced pattern recognition
- **Input Sanitization**: Automatic content filtering
- **Recursion Depth Limiting**: Prevents infinite loops
- **Session Isolation**: Secure multi-user support
- **Integrity Monitoring**: Response validation and consistency

## 📁 File Structure

```
djinn_council_chat/
├── djinn_council_gui_enhanced.py    # Main GUI application
├── advanced_djinn_council.py        # Core council system
├── conversational_memory.py         # Memory management
├── djinn_council.py                 # Legacy council
├── djinn_council_gui.py             # Legacy GUI
├── requirements.txt                 # Dependencies
├── advanced_djinn_config.json       # Advanced configuration
├── djinn_council_config.json        # Legacy configuration
├── research & development/          # Documentation and research
├── launch_*.bat                     # Windows launcher scripts
└── djinn_memory/                    # User memory storage (auto-created)
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/mystical-enhancement`)
3. Commit your changes (`git commit -am 'Add mystical feature'`)
4. Push to the branch (`git push origin feature/mystical-enhancement`)
5. Create a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/Djinn_Council_Chat.git

# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/
```

## 🐛 Troubleshooting

### Common Issues

**Ollama not found**
```bash
# Ensure Ollama is installed and in PATH
ollama --version
```

**Models not loading**
```bash
# Pull required models
ollama pull llama3.2:latest
ollama list
```

**GUI not starting**
- Ensure Python tkinter is installed
- Check Python version (3.7+ required)
- Verify all dependencies are installed

### Debug Mode

Enable detailed logging in configuration:
```json
{
  "logging_settings": {
    "log_level": "DEBUG",
    "enable_detailed_logging": true
  }
}
```

## 📊 Performance

### Benchmarks
- **Startup Time**: < 3 seconds
- **Response Time**: Varies by model (unlimited thinking time)
- **Memory Usage**: ~100MB base + model memory
- **Concurrent Sessions**: Up to 5 (configurable)

### Optimization Tips
- Use SSD storage for faster model loading
- Assign faster models to high-priority roles
- Adjust context limits for better performance
- Enable parallel execution (default)

## 🗺️ Roadmap

### Planned Features
- [ ] Plugin system for custom djinn
- [ ] Web interface option
- [ ] Model fine-tuning integration
- [ ] Voice interaction support
- [ ] Export/import conversation history
- [ ] Custom consensus algorithms
- [ ] Multi-language support

### Version History
- **v1.0**: Initial mystical release with GUI
- **v0.9**: Advanced council with CISM
- **v0.8**: Memory system integration
- **v0.7**: Security and integrity features
- **v0.6**: Basic multi-agent system

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama Project**: For providing the local LLM infrastructure
- **Python Community**: For the excellent libraries
- **AI Research Community**: For inspiring multi-agent architectures
- **Fantasy Literature**: For the mystical djinn concept

## 📬 Contact

- **GitHub Issues**: [Report bugs and request features](https://github.com/Yufok1/Djinn_Council_Chat/issues)
- **Discussions**: [Community discussions](https://github.com/Yufok1/Djinn_Council_Chat/discussions)

---

*"In the realm where code meets consciousness, the djinn council awaits your command..."* ✨🌂✨