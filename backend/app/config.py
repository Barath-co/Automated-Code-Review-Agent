import os
from pydantic import BaseModel

class AppConfig(BaseModel):
    PROJECT_NAME: str = "Code Review Agent (NCIO)"
    PROJECT_VERSION: str = "1.0.0"
    ACADEMIC_INSTITUTION: str = "Sathyabama Institute of Science and Technology"
    AUTHORS: list[str] = [
        "Barath Babu (Reg.No 44110102)",
        "Araveeti Shravanth Reddy (Reg.No 44110063)"
    ]
    INTERNAL_GUIDE: str = "Dr. NANCY NOELLA, M.E., Ph.D."
    HEAD_OF_DEPT: str = "Dr. L. LAKSHMANAN, M.E., Ph.D."
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    SECONDARY_MODEL: str = os.getenv("GEMINI_SECONDARY_MODEL", "gemini-1.5-flash")
    PRO_MODEL: str = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")
    
    # Budget limits as defined in Report Table 3.1 & 4.4
    MAX_TOKENS_PER_TASK: int = 16000
    TIMEOUT_SECONDS: int = 45
    ESTIMATED_INR_PER_1K_TOKENS: float = 0.05  # Approximate INR cost calculation per 1k tokens

config = AppConfig()
