#!/bin/bash
# Claude Environment Setup Script for Codespaces
# This script ensures Claude Code extension works properly in containerized environment

echo "🔧 Setting up Claude Code environment..."

# Ensure we're running as the correct user
if [ "$(whoami)" != "vscode" ]; then
    echo "⚠️  Warning: Running as $(whoami), expected vscode user"
fi

# Create complete Claude directory structure
echo "📁 Creating Claude directory structure..."
mkdir -p /home/vscode/.claude/{ide,config,logs,cache,temp}

# Set proper ownership and permissions
echo "🔐 Setting permissions..."
chown -R vscode:vscode /home/vscode/.claude
chmod -R 755 /home/vscode/.claude

# Create Claude configuration for public framework development
echo "⚙️ Creating Claude configuration..."
cat > /home/vscode/.claude/config.json << 'EOF'
{
  "environment": "codespace-public",
  "workspace": "PHI-Curation-Framework",
  "privacy": "public-development-only",
  "created": "auto-generated-codespace"
}
EOF

# Create public-safe Claude instructions
echo "📋 Creating public-safe Claude instructions..."
cat > /home/vscode/.claude/CLAUDE.md << 'EOF'
# Claude Configuration - PHI-Curation-Framework (Public Codespace)

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
- Python development stack with testing and formatting
- Jupyter notebooks for examples and tutorials
- Documentation tools (Markdown, Mermaid diagrams)
- Git and GitHub CLI for repository management

## Separation Assurance
This environment is completely separate from:
- Private research work and personal data
- BotVault memory and automation systems
- Personal Claude configurations and preferences

All work here is public-appropriate and suitable for open-source collaboration.
EOF

# Set permissions for configuration files
chmod 644 /home/vscode/.claude/config.json
chmod 644 /home/vscode/.claude/CLAUDE.md

# Verify directory structure and permissions
echo "✅ Verifying setup..."
echo "Directory structure:"
ls -la /home/vscode/.claude/
echo ""
echo "Permissions:"
ls -la /home/vscode/.claude/*/

# Test write permissions by creating a test file
echo "🧪 Testing write permissions..."
if echo "test" > /home/vscode/.claude/ide/setup-test.tmp 2>/dev/null; then
    echo "✅ Write permissions working correctly"
    rm -f /home/vscode/.claude/ide/setup-test.tmp
else
    echo "❌ Write permission test failed"
    echo "Attempting permission fix..."
    sudo chown -R vscode:vscode /home/vscode/.claude
    sudo chmod -R 755 /home/vscode/.claude
fi

# Create workspace-specific configuration
echo "🎯 Setting up workspace configuration..."
mkdir -p /workspaces/PHI-Curation-Framework/.vscode
cat > /workspaces/PHI-Curation-Framework/.vscode/settings.json << 'EOF'
{
    "claude.apiKey": "${env:CLAUDE_API_KEY}",
    "claude.environment": "public-framework-development",
    "claude.dataPolicy": "public-only",
    "files.watcherExclude": {
        "**/.claude/**": true
    }
}
EOF

echo "🚀 Claude environment setup complete!"
echo ""
echo "📊 Setup Summary:"
echo "  ✅ Directory structure created with proper permissions"
echo "  ✅ Public-safe configuration initialized"
echo "  ✅ Workspace settings configured"
echo "  ✅ Write permissions verified"
echo ""
echo "🎯 You can now use Claude Code extension without permission errors!"
echo "   - Press Ctrl+Shift+P and search for 'Claude' commands"
echo "   - Or right-click in files for Claude context options"