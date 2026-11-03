from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..models.schemas import CandidateOutput

class BaseModelAdapter(ABC):
    """
    Abstract Model Adapter as specified in NCIO Chapter 4.2.1-C.
    Decouples core orchestration from provider-specific REST APIs.
    """

    @abstractmethod
    async def evaluate_code(
        self,
        code: str,
        language: str,
        persona: str,
        system_instruction: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> CandidateOutput:
        pass
