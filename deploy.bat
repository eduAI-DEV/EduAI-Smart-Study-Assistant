@echo off
REM EduAI Smart Study Assistant - Deployment Script for Windows
REM This script sets up and deploys the EduAI application

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   🎓 EduAI Smart Study Assistant - Deploy Script 🚀   ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set python_version=%%i
echo ✅ Found: %python_version%
echo.

REM Create virtual environment
echo [2/6] Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo ✅ Pip upgraded
echo.

REM Install dependencies
echo [5/6] Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ⚠️  requirements.txt not found. Installing essential packages...
    pip install streamlit ^
                langchain ^
                langchain-openai ^
                langchain-anthropic ^
                langchain-community ^
                tavily-python ^
                python-dotenv ^
                python-docx ^
                PyPDF2
    echo ✅ Essential packages installed
)
echo.

REM Create necessary directories
echo [6/6] Setting up directories and configuration...
if not exist "conversations" mkdir conversations
if not exist "logs" mkdir logs
echo ✅ Directories created
echo.

REM Create .env.example if it doesn't exist
if not exist ".env.example" (
    (
        echo # OpenAI Configuration
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # Tavily Search Configuration
        echo TAVILY_API_KEY=your_tavily_api_key_here
        echo.
        echo # Anthropic Configuration (Optional for Claude models)
        echo ANTHROPIC_API_KEY=your_anthropic_api_key_here
        echo.
        echo # App Configuration
        echo APP_TITLE="EduAI: Deep Research Assistant"
        echo APP_ICON="🎓"
        echo MAX_REQUESTS_PER_HOUR=100
        echo MAX_TOKENS_PER_DAY=100000
    ) > .env.example
    echo ✅ .env.example created
)
echo.

REM Create .streamlit config directory
if not exist ".streamlit" mkdir .streamlit

REM Create streamlit config if it doesn't exist
if not exist ".streamlit\config.toml" (
    (
        echo [theme]
        echo primaryColor = "#0066cc"
        echo backgroundColor = "#ffffff"
        echo secondaryBackgroundColor = "#f0f2f6"
        echo textColor = "#262730"
        echo font = "sans serif"
        echo.
        echo [client]
        echo showErrorDetails = true
        echo toolbarMode = "auto"
        echo.
        echo [logger]
        echo level = "info"
        echo.
        echo [server]
        echo port = 8501
        echo headless = false
        echo runOnSave = true
        echo maxUploadSize = 200
    ) > .streamlit\config.toml
    echo ✅ Streamlit config created
)
echo.

REM Create gitignore if it doesn't exist
if not exist ".gitignore" (
    (
        echo # Virtual Environment
        echo venv/
        echo env/
        echo ENV/
        echo .venv
        echo.
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo *.egg-info/
        echo dist/
        echo build/
        echo.
        echo # Environment variables
        echo .env
        echo .env.local
        echo .env.*.local
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo *.swo
        echo *~
        echo.
        echo # Logs
        echo *.log
        echo logs/
        echo.
        echo # Streamlit
        echo .streamlit/secrets.toml
        echo .streamlit/cache/
        echo.
        echo # Conversations ^& Data
        echo conversations/
        echo *.db
        echo *.sqlite
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Testing
        echo .pytest_cache/
        echo .coverage
        echo htmlcov/
    ) > .gitignore
    echo ✅ .gitignore created
)
echo.

REM Display deployment summary
echo ╔════════════════════════════════════════════════════════╗
echo ║         🎉 Deployment Complete! 🎉                   ║
echo ╚════════════════════════════════════════════════════════╝
echo.

echo 📋 Deployment Summary:
echo   ✅ Python 3 installed
echo   ✅ Virtual environment created
echo   ✅ Dependencies installed
echo   ✅ Directories configured
echo   ✅ Configuration files created
echo.

echo 📝 Next Steps:
echo.
echo 1️⃣  Set up your environment variables:
echo    copy .env.example .env
echo    REM Edit .env with your favorite editor
echo.
echo 2️⃣  Add your API keys to .env:
echo    • OpenAI API Key
echo    • Tavily API Key
echo    • Anthropic API Key (optional, for Claude models)
echo.
echo 3️⃣  Run the application:
echo    streamlit run app.py
echo.
echo 4️⃣  Open your browser:
echo    http://localhost:8501
echo.

echo 🔐 Important Security Notes:
echo   • Never commit .env file to git
echo   • Keep API keys confidential
echo   • Use .env.example as a template for sharing
echo   • Regenerate API keys if exposed
echo.

echo 🚀 Additional Commands:
echo.
echo   Start the app:
echo     streamlit run app.py
echo.
echo   Run with custom config:
echo     streamlit run app.py --server.port 8502
echo.
echo   Run in debug mode:
echo     streamlit run app.py --logger.level=debug
echo.
echo   Deactivate virtual environment:
echo     deactivate
echo.

echo 📚 Documentation:
echo   • Streamlit: https://docs.streamlit.io
echo   • LangChain: https://python.langchain.com
echo   • OpenAI: https://platform.openai.com/docs
echo   • Tavily: https://tavily.com/docs
echo.

echo ✨ Happy learning with EduAI! 🎓
echo.

pause
