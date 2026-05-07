# 🎓 EduAI Smart Study Assistant

> An intelligent, AI-powered research and homework assistant using real-time web search, multi-model AI support, and advanced conversation management.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io)

## ✨ Features

### 🤖 **Multi-Model AI Support**
- **OpenAI Models**: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo
- **Anthropic Models**: Claude 3 Opus, Claude 3 Sonnet
- Easy model switching through UI

### 🔍 **Real-Time Web Search**
- Integration with Tavily Search API
- Configurable number of search results
- Source citation and reference tracking

### 💬 **Advanced Chat Interface**
- Real-time streaming responses
- Multi-tab interface (Chat, History, File Upload, Tools)
- Conversation memory and context awareness
- Clean, intuitive UI

### 💾 **Conversation Management**
- Save conversations to JSON
- Load previous conversations
- Export in multiple formats (JSON, Markdown, TXT)
- Per-user conversation history

### 📥 **File Upload Support**
- Upload and analyze PDFs, TXT, DOC, DOCX files
- File size tracking
- Activity logging

### 🔐 **Authentication & Security**
- User login and registration
- Password hashing
- Session management
- API key validation

### ⚡ **Rate Limiting**
- 100 requests per hour limit
- Real-time usage tracking
- Reset time display
- Prevents abuse

### 💰 **Cost Tracking**
- Token usage monitoring
- Real-time cost calculation
- Model-specific pricing
- Session summary

### 📊 **Logging & Analytics**
- Comprehensive activity logging
- Error tracking
- System performance monitoring
- File-based log storage

### ⚙️ **System Tools**
- Clear chat history
- View system logs
- Session statistics
- Advanced settings (temperature, tokens, search results)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

#### Option 1: Linux/Mac (Bash)
```bash
chmod +x deploy.sh
./deploy.sh
```

#### Option 2: Windows (Batch)
```cmd
deploy.bat
```

#### Option 3: All Platforms (Python)
```bash
python run.py setup
```

### Configuration

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`:**
   ```env
   OPENAI_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here  # Optional, for Claude models
   ```

3. **Get API Keys:**
   - [OpenAI API Keys](https://platform.openai.com/api-keys)
   - [Tavily API Keys](https://tavily.com/dashboard)
   - [Anthropic API Keys](https://console.anthropic.com/)

### Running the Application

```bash
# Start the app
streamlit run app.py

# Or use the Python manager
python run.py run

# Custom port
python run.py run --port 8502

# Debug mode
python run.py run --debug
```

The application will open at `http://localhost:8501`

## 📋 Usage

### Chat Tab
- Ask questions about history, current affairs, or homework
- Get real-time web search results
- Streaming responses with citations
- Conversation memory maintained

### History Tab
- Save current conversation with custom title
- Load previous conversations
- Export in JSON, Markdown, or TXT format
- Browse conversation history

### File Upload Tab
- Upload PDF, TXT, DOC, DOCX files
- Analyze documents with AI
- Track file uploads
- Activity logging

### Tools Tab
- Clear chat history
- View system logs
- Session statistics
- Configure advanced settings

## 🔧 Advanced Configuration

### Environment Variables
Edit `.env` file to customize:

```env
# Rate limiting
MAX_REQUESTS_PER_HOUR=100
MAX_TOKENS_PER_DAY=100000

# Default model
DEFAULT_MODEL=gpt-4o

# AI settings
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2048
DEFAULT_SEARCH_RESULTS=5

# Feature flags
ENABLE_AUTH=true
ENABLE_FILE_UPLOAD=true
ENABLE_EXPORT=true
ENABLE_COST_TRACKING=true
```

### Streamlit Configuration
Edit `.streamlit/config.toml` for UI customization:
- Theme colors
- Font selection
- Server settings
- Client behavior

## 📦 Dependencies

See `requirements.txt` for complete list:
- **streamlit**: Web UI framework
- **langchain**: AI orchestration
- **langchain-openai**: OpenAI integration
- **langchain-anthropic**: Anthropic integration
- **langchain-community**: Additional tools
- **tavily-python**: Web search integration
- **python-dotenv**: Environment variables
- **python-docx**: Document processing
- **PyPDF2**: PDF processing

## 📁 Project Structure

```
EduAI-Smart-Study-Assistant/
├── app.py                    # Main application
├── run.py                    # Python manager script
├── deploy.sh                 # Linux/Mac deployment
├── deploy.bat                # Windows deployment
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── conversations/           # Saved conversations
├── logs/                    # Application logs
└── eduai.log               # Main log file
```

## 🔐 Security

### Important Notes
- **Never commit `.env` file** to version control
- **Keep API keys confidential**
- Regenerate keys if exposed
- Use strong passwords for authentication
- Enable authentication in production

### Best Practices
- Use `.env.example` as a template for sharing
- Rotate API keys regularly
- Monitor usage and costs
- Enable rate limiting
- Review logs regularly

## 🐛 Troubleshooting

### Python Not Found
```bash
# Install Python 3.8+
# macOS: brew install python3
# Ubuntu: sudo apt-get install python3
# Windows: Download from python.org
```

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### Dependency Issues
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API Key Errors
- Verify keys in `.env` file
- Check API key format
- Ensure keys have required permissions
- Test keys on respective platforms

### Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill process on port 8501
# macOS/Linux: lsof -ti:8501 | xargs kill -9
# Windows: netstat -ano | findstr :8501
```

## 🚀 Deployment

### Streamlit Cloud
1. Push repository to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Create new app from repository
4. Add secrets through dashboard

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### Heroku
```bash
git push heroku main
```

## 📊 Pricing & Costs

Current pricing (as of 2024):

| Model | Input Cost | Output Cost |
|-------|-----------|------------|
| GPT-4o | $0.005 | $0.015 |
| GPT-4 Turbo | $0.01 | $0.03 |
| GPT-3.5 Turbo | $0.0005 | $0.0015 |
| Claude 3 Opus | $0.015 | $0.075 |
| Claude 3 Sonnet | $0.003 | $0.015 |

See `.env` for cost tracking configuration.

## 📚 Documentation

- [Streamlit Documentation](https://docs.streamlit.io)
- [LangChain Documentation](https://python.langchain.com)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic API Reference](https://docs.anthropic.com)
- [Tavily Search API](https://tavily.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application uses third-party APIs (OpenAI, Anthropic, Tavily). Users are responsible for:
- Understanding API terms of service
- Monitoring and paying for API usage
- Complying with content policies
- Protecting their API keys
- Reviewing generated content

## 🆘 Support

- **Issues & Bugs**: [GitHub Issues](https://github.com/eduAI-DEV/EduAI-Smart-Study-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/eduAI-DEV/EduAI-Smart-Study-Assistant/discussions)
- **Documentation**: See this README and inline code comments

## 🎓 About

EduAI Smart Study Assistant is designed to help students and researchers:
- Conduct deep research with real-time web search
- Get homework help with step-by-step explanations
- Explore multiple perspectives on topics
- Maintain conversation history for reference
- Track API usage and costs

**No ads, no tracking, no distractions—just pure learning.**

---

<div align="center">

**Made with ❤️ for students and educators everywhere**

[⭐ Star us on GitHub](https://github.com/eduAI-DEV/EduAI-Smart-Study-Assistant)

</div>
