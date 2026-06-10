#!/bin/bash
# PHI-Canto Automation Quick Demo
# Demonstrates the automated workflow with existing files

echo "🚀 PHI-Canto Automation Demo"
echo "============================"
echo ""

# Check if we're in the right directory
if [[ ! -f "curation_pipeline.py" ]]; then
    echo "❌ Please run from 11-CLAUDE-AI directory"
    echo "   cd <your-clone>/11-CLAUDE-AI"
    exit 1
fi

echo "📋 Available PDFs in To-curate folder:"
ls -1 ../00-Inbox/To-curate/*.pdf 2>/dev/null || echo "   No PDFs found"
echo ""

echo "📊 Current database status:"
cd db
python3 daily_curation.py progress 2>/dev/null || echo "   Database not yet set up"
cd ..
echo ""

echo "🛠️  Available automation commands:"
echo ""
echo "   📄 Process existing PDF:"
echo "      python3 curation_pipeline.py process-pdf filename.pdf"
echo ""
echo "   🚀 Start new paper:"
echo "      python3 curation_pipeline.py auto-process /path/to/paper.pdf"
echo ""
echo "   📝 Start session tracking:"
echo "      python3 db/workflow_helper.py start-session 'Project Name'"
echo ""
echo "   ✅ Complete curation:"
echo "      python3 curation_pipeline.py complete-paper filename.pdf 'Summary'"
echo ""
echo "   📊 Check progress:"
echo "      python3 db/daily_curation.py progress"
echo ""

echo "💡 Example workflow:"
echo "   1. python3 curation_pipeline.py auto-process ~/Downloads/paper.pdf"
echo "   2. python3 db/workflow_helper.py start-session 'Paper Analysis'"
echo "   3. [Do curation work in PHI-Canto]"
echo "   4. python3 db/workflow_helper.py end-session 'Paper Analysis' 'Summary' 3 5 2.0"
echo "   5. python3 curation_pipeline.py complete-paper paper.pdf 'Completed annotation'"
echo ""

echo "📖 Full documentation: AUTOMATION-GUIDE.md"
echo ""
echo "✨ Your curation workflow is now fully automated!"