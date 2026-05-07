"""
Utility script for running and managing EduAI application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class EduAIManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.venv_dir = self.root_dir / "venv"
        self.conversations_dir = self.root_dir / "conversations"
        self.logs_dir = self.root_dir / "logs"
    
    def setup_directories(self):
        """Create necessary directories"""
        print("📁 Setting up directories...")
        self.conversations_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        print("✅ Directories ready")
    
    def check_python(self):
        """Check if Python 3 is installed"""
        print("🐍 Checking Python installation...")
        try:
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True
            )
            print(f"✅ {result.stdout.strip()}")
            return True
        except FileNotFoundError:
            print("❌ Python 3 not found")
            return False
    
    def check_venv(self):
        """Check if virtual environment exists"""
        return self.venv_dir.exists()
    
    def create_venv(self):
        """Create virtual environment"""
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)])
        print("✅ Virtual environment created")
    
    def install_requirements(self):
        """Install dependencies"""
        print("📦 Installing dependencies...")
        requirements_file = self.root_dir / "requirements.txt"
        
        if requirements_file.exists():
            pip_cmd = self.get_pip_command()
            subprocess.run([pip_cmd, "install", "-r", str(requirements_file)])
        else:
            print("⚠️  requirements.txt not found")
        
        print("✅ Dependencies installed")
    
    def get_pip_command(self):
        """Get pip command based on OS and venv"""
        if platform.system() == "Windows":
            return str(self.venv_dir / "Scripts" / "pip.exe")
        else:
            return str(self.venv_dir / "bin" / "pip")
    
    def get_python_command(self):
        """Get python command based on OS and venv"""
        if platform.system() == "Windows":
            return str(self.venv_dir / "Scripts" / "python.exe")
        else:
            return str(self.venv_dir / "bin" / "python")
    
    def run_app(self, port=8501, debug=False):
        """Run the Streamlit application"""
        print(f"🚀 Starting EduAI on port {port}...")
        
        if not self.check_venv():
            print("⚠️  Virtual environment not found. Creating...")
            self.create_venv()
            self.install_requirements()
        
        streamlit_cmd = [
            self.get_python_command(),
            "-m",
            "streamlit",
            "run",
            str(self.root_dir / "app.py"),
            f"--server.port={port}",
        ]
        
        if debug:
            streamlit_cmd.append("--logger.level=debug")
        
        try:
            subprocess.run(streamlit_cmd)
        except KeyboardInterrupt:
            print("\n👋 EduAI stopped")
    
    def setup(self):
        """Complete setup process"""
        print("\n🎓 EduAI Setup Started\n")
        
        if not self.check_python():
            print("❌ Python 3 is required")
            sys.exit(1)
        
        self.setup_directories()
        
        if not self.check_venv():
            self.create_venv()
        
        self.install_requirements()
        
        print("\n✅ Setup complete!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys to .env")
        print("3. Run: python run.py\n")
    
    def clean(self):
        """Clean up generated files"""
        print("🧹 Cleaning up...")
        
        # Remove __pycache__
        for pycache in self.root_dir.rglob("__pycache__"):
            import shutil
            shutil.rmtree(pycache)
        
        # Remove .streamlit cache
        streamlit_cache = self.root_dir / ".streamlit" / "cache"
        if streamlit_cache.exists():
            import shutil
            shutil.rmtree(streamlit_cache)
        
        print("✅ Cleanup complete")
    
    def info(self):
        """Display system information"""
        print("\n📊 EduAI System Information\n")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print(f"Project Root: {self.root_dir}")
        print(f"Virtual Environment: {self.venv_dir}")
        print(f"Conversations Dir: {self.conversations_dir}")
        print(f"Logs Dir: {self.logs_dir}\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="EduAI Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py setup          # Complete setup
  python run.py run            # Start the app
  python run.py run --port 8502  # Start on custom port
  python run.py run --debug    # Start with debug logging
  python run.py clean          # Clean up generated files
  python run.py info           # Show system information
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["setup", "run", "clean", "info"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run Streamlit on (default: 8501)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode"
    )
    
    args = parser.parse_args()
    manager = EduAIManager()
    
    if args.command == "setup":
        manager.setup()
    elif args.command == "run":
        manager.run_app(port=args.port, debug=args.debug)
    elif args.command == "clean":
        manager.clean()
    elif args.command == "info":
        manager.info()

if __name__ == "__main__":
    main()
