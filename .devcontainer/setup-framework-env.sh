#!/bin/bash
# PHI-Curation-Framework Codespace Setup Script
# This script initializes the development environment for the public framework

echo "🚀 Setting up PHI-Curation-Framework development environment..."

# Create workspace structure
mkdir -p /workspace/{docs,examples,tests,tools}

# Set up Git configuration for Codespace
git config --global init.defaultBranch main
git config --global pull.rebase false

# Install additional Python packages for framework development
pip install --upgrade pip
pip install pytest black pylint jupyter notebook pandas

# Install development tools
npm install -g @mermaid-js/mermaid-cli

# Create basic project structure if not exists
touch requirements.txt
touch README.md
touch CONTRIBUTING.md

# Set up Claude configuration for public framework work
mkdir -p ~/.claude
cat > ~/.claude/CLAUDE.md << 'EOF'
# Claude Configuration - PHI-Curation-Framework (Public)

This is the PUBLIC development environment for the PHI-Curation-Framework.

## Environment Context
- **Repository**: PHI-base/PHI-Curation-Framework (public)
- **Purpose**: Framework development, documentation, examples
- **Data Policy**: No private/personal data allowed
- **Collaboration**: Public, open-source development

## Development Guidelines
- Focus on framework tools and documentation
- Use generic examples and test data only
- No personal workflow automation or private systems
- Public-appropriate code and comments only

## Available Tools
- Python development stack
- Jupyter notebooks for examples
- Documentation tools (Markdown, Mermaid)
- Testing framework (pytest)
- Code formatting (black, pylint)

EOF

echo "✅ PHI-Curation-Framework Codespace setup complete!"
echo "🎯 Environment configured for public framework development"
echo "🔒 No private data access - public repository work only"