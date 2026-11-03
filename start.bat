@echo off
title Code Review Agent - Sathyabama Institute of Science and Technology
echo =========================================================================
echo       CODE REVIEW AGENT: Neural Consensus Intelligence Orchestrator
echo              Department of Computer Science and Engineering
echo              SATHYABAMA INSTITUTE OF SCIENCE AND TECHNOLOGY
echo =========================================================================
echo Authors: Barath Babu (44110102) ^& Araveeti Shravanth Reddy (44110063)
echo Guide:   Dr. NANCY NOELLA, M.E., Ph.D.
echo.
echo Starting NCIO Unified Service (FastAPI + Embedded Production Frontend)...
echo URL: http://127.0.0.1:8000
echo =========================================================================

cd /d "%~dp0backend"
python run_backend.py
pause
