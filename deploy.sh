#!/bin/bash

# EduAI Smart Study Assistant - Deployment Script
# This script sets up and deploys the EduAI application

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   🎓 EduAI Smart Study Assistant - Deploy Script 🚀   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Python is installed
echo -e "${YELLOW}[1/6] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8+${NC}"
    exit 1
fi
python_version=$(python3 --version)
echo -e "${GREEN}✅ Found: $python_version${NC}"

# Create virtual environment
echo -e "${YELLOW}[2/6] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}[3/6] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Upgrade pip
echo -e "${YELLOW}[4/6] Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo -e "${GREEN}✅ Pip upgraded${NC}"

# Install dependencies
echo -e "${YELLOW}[5/6] Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found. Installing essential packages...${NC}"
    pip install streamlit \
                langchain \
                langchain-openai \
                langchain-anthropic \
                langchain-community \
                tavily-python \
                python-dotenv \
                python-docx \
                PyPDF2
    echo -e "${GREEN}✅ Essential packages installed${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}[6/6] Setting up directories and configuration...${NC}"
mkdir -p conversations logs
echo -e "${GREEN}✅ Directories created${NC}"

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    cat > .env.example << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Tavily Search Configuration
TAVILY_API_KEY=your_tavily_api_key_here

# Anthropic Configuration (Optional for Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# App Configuration
APP_TITLE="EduAI: Deep Research Assistant"
APP_ICON="🎓"
MAX_REQUESTS_PER_HOUR=100
MAX_TOKENS_PER_DAY=100000
EOF
    echo -e "${GREEN}✅ .env.example created${NC}"
fi

# Create .streamlit config directory
mkdir -p .streamlit

# Create streamlit config if it doesn't exist
if [ ! -f ".streamlit/config.toml" ]; then
    cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true
toolbarMode = "auto"

[logger]
level = "info"

[server]
port = 8501
headless = false
runOnSave = true
maxUploadSize = 200
EOF
    echo -e "${GREEN}✅ Streamlit config created${NC}"
fi

# Create gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Virtual Environment
venv/
env/
ENV/
.venv

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Streamlit
.streamlit/secrets.toml
.streamlit/cache/

# Conversations & Data
conversations/
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
EOF
    echo -e "${GREEN}✅ .gitignore created${NC}"
fi

# Display deployment summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🎉 Deployment Complete! 🎉                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"

echo ""
echo -e "${GREEN}📋 Deployment Summary:${NC}"
echo "  ✅ Python 3 installed"
echo "  ✅ Virtual environment created"
echo "  ✅ Dependencies installed"
echo "  ✅ Directories configured"
echo "  ✅ Configuration files created"
echo ""

echo -e "${YELLOW}📝 Next Steps:${NC}"
echo ""
echo "1️⃣  Set up your environment variables:"
echo -e "   ${BLUE}cp .env.example .env${NC}"
echo -e "   ${BLUE}nano .env  # or use your preferred editor${NC}"
echo ""
echo "2️⃣  Add your API keys to .env:"
echo "   • OpenAI API Key"
echo "   • Tavily API Key"
echo "   • Anthropic API Key (optional, for Claude models)"
echo ""
echo "3️⃣  Run the application:"
echo -e "   ${BLUE}streamlit run app.py${NC}"
echo ""
echo "4️⃣  Open your browser:"
echo -e "   ${BLUE}http://localhost:8501${NC}"
echo ""

echo -e "${GREEN}🔐 Important Security Notes:${NC}"
echo "  • Never commit .env file to git"
echo "  • Keep API keys confidential"
echo "  • Use .env.example as a template for sharing"
echo "  • Regenerate API keys if exposed"
echo ""

echo -e "${YELLOW}🚀 Additional Commands:${NC}"
echo ""
echo -e "  Start the app:"
echo -e "    ${BLUE}streamlit run app.py${NC}"
echo ""
echo -e "  Run with custom config:"
echo -e "    ${BLUE}streamlit run app.py --server.port 8502${NC}"
echo ""
echo -e "  Run in debug mode:"
echo -e "    ${BLUE}streamlit run app.py --logger.level=debug${NC}"
echo ""
echo -e "  Deactivate virtual environment:"
echo -e "    ${BLUE}deactivate${NC}"
echo ""

echo -e "${BLUE}📚 Documentation:${NC}"
echo "  • Streamlit: https://docs.streamlit.io"
echo "  • LangChain: https://python.langchain.com"
echo "  • OpenAI: https://platform.openai.com/docs"
echo "  • Tavily: https://tavily.com/docs"
echo ""

echo -e "${GREEN}✨ Happy learning with EduAI! 🎓${NC}"
echo ""
