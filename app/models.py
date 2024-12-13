"""Global models"""

from pydantic import BaseModel, Field
from typing import Optional


class EnvVariables(BaseModel):
    visitorData: str = Field(description="Extracted along with po token")
    po_token: str = Field(
        "How to extract it refer to : https://github.com/yt-dlp/yt-dlp/wiki/Extractors#"
        "manually-acquiring-a-po-token-from-a-browser-for-use-when-logged-out"
    )
    proxy: Optional[str] = None

    def po_token_verifier(self) -> tuple[str, str]:
        return self.visitorData, self.po_token
