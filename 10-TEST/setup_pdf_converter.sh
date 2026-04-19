#!/bin/bash
# PDF Converter Setup Script
# Automatically detects environment and installs PyMuPDF

set -e

echo "🔧 PDF Converter Setup for Obsidian"
echo "====================================="

# Function to detect environment
detect_environment() {
    if [[ -n "$WSL_DISTRO_NAME" ]] || [[ -n "$WSL_INTEROP" ]]; then
        echo "📍 Detected: WSL2 environment"
        return 1
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &> /dev/null; then
            echo "📍 Detected: Ubuntu/Debian Linux"
            return 2
        else
            echo "📍 Detected: Linux (other)"
            return 3
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "📍 Detected: macOS"
        return 4
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "📍 Detected: Windows"
        return 5
    else
        echo "📍 Detected: Unknown OS"
        return 0
    fi
}

# Check if python3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 not found. Please install Python 3.8+ first."
        exit 1
    fi

    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "✅ Python $python_version detected"
}

# Install PyMuPDF based on environment
install_pymupdf() {
    local env_code=$1

    case $env_code in
        1) # WSL2
            echo "🔄 Installing PyMuPDF for WSL2..."
            echo "   Using --break-system-packages method"
            python3 -m pip install --break-system-packages PyMuPDF
            ;;
        2) # Ubuntu/Debian
            echo "🔄 Installing PyMuPDF for Ubuntu/Debian..."

            # Try standard installation first
            if python3 -m pip install PyMuPDF &> /dev/null; then
                echo "✅ Standard installation successful"
            else
                echo "⚠️  Standard installation failed, trying --break-system-packages"
                python3 -m pip install --break-system-packages PyMuPDF
            fi
            ;;
        3|4|5) # Other Linux, macOS, Windows
            echo "🔄 Installing PyMuPDF..."

            # Try with virtual environment first
            if python3 -m venv pdf_test_env &> /dev/null; then
                echo "✅ Virtual environment supported, using clean installation"
                source pdf_test_env/bin/activate 2>/dev/null || source pdf_test_env/Scripts/activate
                pip install PyMuPDF
                deactivate 2>/dev/null || true
                rm -rf pdf_test_env
            else
                echo "⚠️  Virtual environment failed, using system installation"
                python3 -m pip install --user PyMuPDF
            fi
            ;;
        0) # Unknown
            echo "⚠️  Unknown environment, trying multiple methods..."

            methods=(
                "python3 -m pip install PyMuPDF"
                "python3 -m pip install --user PyMuPDF"
                "python3 -m pip install --break-system-packages PyMuPDF"
            )

            for method in "${methods[@]}"; do
                echo "   Trying: $method"
                if eval "$method" &> /dev/null; then
                    echo "✅ Success with: $method"
                    break
                fi
            done
            ;;
    esac
}

# Verify installation
verify_installation() {
    echo "🔍 Verifying PyMuPDF installation..."

    if python3 -c "import fitz; print(f'PyMuPDF {fitz.version} installed successfully')" 2>/dev/null; then
        echo "✅ Installation verified!"
        return 0
    else
        echo "❌ Installation verification failed"
        return 1
    fi
}

# Test with sample conversion
test_converter() {
    echo "🧪 Testing PDF converter..."

    if [[ -f "obsidian_pdf_converter.py" ]]; then
        if python3 -c "
import sys
sys.path.append('.')
from obsidian_pdf_converter import check_dependencies
available, message = check_dependencies()
print(f'Converter test: {message}')
exit(0 if available else 1)
" 2>/dev/null; then
            echo "✅ PDF converter ready to use!"
            return 0
        else
            echo "⚠️  PDF converter test failed"
            return 1
        fi
    else
        echo "⚠️  PDF converter script not found"
        echo "   Make sure you're in the directory with obsidian_pdf_converter.py"
        return 1
    fi
}

# Main installation process
main() {
    echo
    echo "🔍 Checking environment..."

    # Check Python
    check_python

    # Detect environment
    detect_environment
    env_code=$?

    echo
    echo "🔧 Installing PyMuPDF..."

    # Install based on environment
    if install_pymupdf $env_code; then
        echo "✅ Installation completed"
    else
        echo "❌ Installation failed"
        exit 1
    fi

    echo
    echo "🔍 Verifying installation..."

    # Verify installation
    if verify_installation; then
        echo
        echo "🧪 Testing PDF converter..."
        test_converter

        echo
        echo "🎯 Setup Complete!"
        echo
        echo "Usage:"
        echo "  python3 obsidian_pdf_converter.py"
        echo
        echo "Your PDF converter is ready for Obsidian!"

    else
        echo
        echo "❌ Setup failed. Please check the troubleshooting section in README-PDF-Conversion.md"
        exit 1
    fi
}

# Run main function
main "$@"