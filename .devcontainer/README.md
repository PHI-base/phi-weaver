# PHI-Curation-Framework Codespace Configuration

This directory contains the development environment configuration for GitHub Codespaces, providing a clean, isolated environment for public framework development.

## 🎯 Purpose

- **Public framework development only**
- **No private data access** - completely separated from personal research
- **Standardized development environment** for contributors
- **Pre-configured with Claude Code** for AI-assisted development

## 🚀 Quick Start

1. **In GitHub**: Navigate to https://github.com/PHI-base/PHI-Curation-Framework
2. **Click "Code"** → **"Codespaces"** → **"Create codespace on main"**
3. **Wait for setup** - Environment automatically configures with Claude Code
4. **Start developing** - Framework tools and Claude assistance ready!

## 🛠️ Included Tools

### Development Stack
- **Python 3.11** with pip, pytest, black, pylint
- **Node.js 18** for web tools and documentation
- **Jupyter** for example notebooks and documentation
- **Git & GitHub CLI** for repository management

### Claude Code Integration
- **Claude VS Code extension** pre-installed
- **Public-safe configuration** - no private data access
- **Framework-focused prompts** and assistance
- **Isolated Claude memory** specific to public development

### Documentation & Collaboration
- **Markdown tools** with Mermaid diagram support
- **YAML editing** for configuration files
- **JSON tools** for data structure development

## 🔒 Security Features

### Complete Separation from Private Work
- **Different environment** (cloud vs local)
- **Separate Claude configuration** (public-only)
- **No access to private repositories** or data
- **Isolated development context**

### Public-Safe Defaults
- **Framework examples only** - no personal data
- **Generic configurations** - no private settings
- **Collaborative environment** - designed for open source

## 📁 Environment Structure

```
/workspace/
├── .devcontainer/           # This configuration
├── docs/                    # Framework documentation
├── examples/                # Usage examples and tutorials
├── tests/                   # Test suite
├── tools/                   # Development utilities
└── ~/.claude/               # Public-only Claude configuration
```

## 🎮 Usage Examples

### Starting Claude Code
```bash
# Claude extension automatically available in VS Code
# Or use CLI if installed
claude --help
```

### Development Workflow
```bash
# Framework development
python -m pytest tests/
black framework/
pylint framework/

# Documentation
jupyter notebook examples/
```

### Adding Dependencies
```bash
# Add to requirements.txt for persistence
pip install new-package
pip freeze > requirements.txt
```

## 🤝 Contributing

This Codespace configuration is designed for:
- **Framework contributors** - standardized development environment
- **Documentation writers** - tools for examples and tutorials  
- **Researchers** - public examples and integration guides
- **Community members** - easy environment setup

## 🔄 Updates

To update the Codespace configuration:
1. **Modify files** in `.devcontainer/`
2. **Commit changes** to the repository
3. **Rebuild Codespace** - settings apply to new Codespaces automatically

## 📞 Support

For issues with the Codespace environment:
- **GitHub Issues**: Report environment problems
- **Discussions**: Questions about framework development  
- **Documentation**: Check framework docs for usage guidance