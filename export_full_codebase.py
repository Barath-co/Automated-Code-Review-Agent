import os

PROJECT_ROOT = r"C:\Users\hp\.gemini\antigravity\scratch\CodeReviewAgent"
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "FULL_CODEBASE_FOR_REVIEW.md")

FILES_TO_INCLUDE = [
    # Architecture Overview & Readme
    ("README.md", "README.md", "markdown"),
    
    # Backend Configuration & Entrypoint
    ("backend/run_backend.py", "backend/run_backend.py", "python"),
    ("backend/requirements.txt", "backend/requirements.txt", "text"),
    ("backend/app/config.py", "backend/app/config.py", "python"),
    ("backend/app/main.py", "backend/app/main.py", "python"),
    
    # Data Models & Schemas
    ("backend/app/models/schemas.py", "backend/app/models/schemas.py", "python"),
    
    # Orchestration Engine
    ("backend/app/orchestrator/ncio_engine.py", "backend/app/orchestrator/ncio_engine.py", "python"),
    
    # Consensus Analyzer
    ("backend/app/consensus/analyzer.py", "backend/app/consensus/analyzer.py", "python"),
    
    # Deterministic Code Validator
    ("backend/app/validators/code_validator.py", "backend/app/validators/code_validator.py", "python"),
    
    # Model Adapters (Base, Live Gemini, Offline Simulation)
    ("backend/app/adapters/base.py", "backend/app/adapters/base.py", "python"),
    ("backend/app/adapters/gemini_adapter.py", "backend/app/adapters/gemini_adapter.py", "python"),
    ("backend/app/adapters/simulated_adapter.py", "backend/app/adapters/simulated_adapter.py", "python"),
    
    # Database Persistence & Sample Test Cases
    ("backend/app/db/storage.py", "backend/app/db/storage.py", "python"),
    ("backend/app/samples/test_cases.py", "backend/app/samples/test_cases.py", "python"),
    
    # Automated Tests
    ("backend/tests/test_ncio.py", "backend/tests/test_ncio.py", "python"),
    
    # Frontend Core
    ("frontend/package.json", "frontend/package.json", "json"),
    ("frontend/src/utils/api.js", "frontend/src/utils/api.js", "javascript"),
    ("frontend/src/utils/presets.js", "frontend/src/utils/presets.js", "javascript"),
    ("frontend/src/App.jsx", "frontend/src/App.jsx", "javascript"),
    ("frontend/src/index.css", "frontend/src/index.css", "css"),
    
    # Frontend Components
    ("frontend/src/components/Header.jsx", "frontend/src/components/Header.jsx", "javascript"),
    ("frontend/src/components/QuickActionBar.jsx", "frontend/src/components/QuickActionBar.jsx", "javascript"),
    ("frontend/src/components/ModuleNav.jsx", "frontend/src/components/ModuleNav.jsx", "javascript"),
    ("frontend/src/components/CodeEditorPane.jsx", "frontend/src/components/CodeEditorPane.jsx", "javascript"),
    ("frontend/src/components/OrchestrationProgress.jsx", "frontend/src/components/OrchestrationProgress.jsx", "javascript"),
    ("frontend/src/components/ConsensusMatrix.jsx", "frontend/src/components/ConsensusMatrix.jsx", "javascript"),
    ("frontend/src/components/FindingsList.jsx", "frontend/src/components/FindingsList.jsx", "javascript"),
    ("frontend/src/components/DiffViewer.jsx", "frontend/src/components/DiffViewer.jsx", "javascript"),
    ("frontend/src/components/MetricsBar.jsx", "frontend/src/components/MetricsBar.jsx", "javascript"),
    ("frontend/src/components/OrchestrationModuleView.jsx", "frontend/src/components/OrchestrationModuleView.jsx", "javascript"),
    ("frontend/src/components/ModelAdaptersView.jsx", "frontend/src/components/ModelAdaptersView.jsx", "javascript"),
    ("frontend/src/components/ResponseDeliveryView.jsx", "frontend/src/components/ResponseDeliveryView.jsx", "javascript"),
    ("frontend/src/components/SettingsModal.jsx", "frontend/src/components/SettingsModal.jsx", "javascript"),
    ("frontend/src/components/AcademicInfoModal.jsx", "frontend/src/components/AcademicInfoModal.jsx", "javascript"),
    ("frontend/src/components/HistoryDrawer.jsx", "frontend/src/components/HistoryDrawer.jsx", "javascript"),
]

output_lines = [
    "# CODE REVIEW AGENT: COMPLETE PROJECT CODEBASE",
    "## Neural Consensus Intelligence Orchestrator (NCIO)",
    "**Institution**: Sathyabama Institute of Science and Technology, Chennai (CSE Dept)",
    "**Authors**: Barath Babu (44110102) & Araveeti Shravanth Reddy (44110063)",
    "**Guide**: Dr. Nancy Noella, M.E., Ph.D.",
    "",
    "> This comprehensive dossier contains the complete, production-ready source code of the NCIO Code Review Agent system for peer review by Claude / senior software architects.",
    "",
    "---",
    "",
    "## TABLE OF CONTENTS",
]

for rel_path, title, _ in FILES_TO_INCLUDE:
    anchor = title.lower().replace("/", "-").replace(".", "").replace(" ", "-")
    output_lines.append(f"- [{title}](#{anchor})")

output_lines.append("\n---\n")

for rel_path, title, lang in FILES_TO_INCLUDE:
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        output_lines.append(f"## {title}\n")
        output_lines.append(f"```{lang}")
        output_lines.append(content)
        output_lines.append("```\n")
        output_lines.append("---\n")
    else:
        output_lines.append(f"## {title} (File not found: {rel_path})\n---\n")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

# Also copy to downloads for easy opening
import shutil
downloads_out = r"C:\Users\hp\Downloads\FULL_CODEBASE_FOR_REVIEW.md"
shutil.copyfile(OUTPUT_FILE, downloads_out)

print(f"Generated complete review file at:\n{OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} bytes)")
print(f"Also copied to:\n{downloads_out}")
