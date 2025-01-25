# Project Setup Guide

## Table of Contents
1. [Install Git](#1-install-git)
2. [Clone the Repository](#2-clone-the-repository)
3. [Install Python using mise](#3-install-python-using-mise)
4. [Install pipx](#1-install-pipx)
5. [Install Poetry](#2-install-poetry)
6. [Install Project Dependencies](#5-install-project-dependencies)
7. [Configure API Key](#7-configure-api-key)
8. [Running the App](#running-the-app)

## 1. Install Git

### Windows
1. Download Git from [git-scm.com](https://git-scm.com/download/windows)
2. Run installer, use default settings
3. Open "Git Bash" from Start menu to verify:
```bash
git --version
```

### macOS
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Git
brew install git
```

### Linux/WSL
```bash
sudo apt update
sudo apt install git
```

## 2. Clone the Repository
```bash
# Create a folder for your projects (optional)
mkdir ~/projects
cd ~/projects

# Clone the repo
git clone <your-repo-url>
cd <project-name>
```

## 3. Install Python using mise

### Windows (WSL)/Linux
```bash
# Install mise
curl https://mise.run | sh

# Add to shell (pick one):
# For bash:
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
source ~/.bashrc

# For zsh:
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc

# Install Python
mise use python@latest
```

### macOS
```bash
# Install mise
brew install mise

# Add to shell (pick one):
# For bash:
echo 'eval "$(mise activate bash)"' >> ~/.bashrc
source ~/.bashrc

# For zsh:
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc
source ~/.zshrc

# Install Python
```bash
mise install python@3.13.1
mise use python@3.13.1
```

### 3. Install Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## 1. Install pipx

### Windows
```bash
# Install via pip
py -m pip install --user pipx
py -m pipx ensurepath
```

### macOS
```bash
# Using Homebrew
brew install pipx
pipx ensurepath
```

### Linux/WSL
```bash
# Ubuntu 23.04+
sudo apt update
sudo apt install pipx
pipx ensurepath

# Or using pip on other distros
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

## 2. Install Poetry

```bash
# Install via pipx (recommended)
pipx install poetry
```



### 5. Install Project Dependencies
```bash
poetry install
```

## 7. Configure API Key
```bash
# Create .env file in project root
cp .env.example .env

# Edit .env and add your Anthropic API key
echo "ANTHROPIC_API_KEY=your-api-key-here" >> .env
```

You can get your Anthropic API key from [console.anthropic.com](https://console.anthropic.com/).

## Running the App
```bash
poetry run example1
```

