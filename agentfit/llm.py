import hashlib

from anthropic import AnthropicBedrock, RateLimitError
from pathlib import Path

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

client = AnthropicBedrock(
    aws_region="eu-west-2",
)

cache_dir = Path("~/.cache/agentfit").expanduser()
cache_dir.mkdir(
    exist_ok=True,
    parents=True,
)


class LLMClient:
    def __init__(
        self,
        system: str,
        model="anthropic.claude-3-haiku-20240307-v1:0",
        max_tokens=4096,
    ):
        self.system = system
        self.model = model
        self.max_tokens = max_tokens

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(RateLimitError),
    )
    def __call__(self, content: str):
        md5 = hashlib.md5(content.encode()).hexdigest()
        path = cache_dir / f"{md5}.txt"

        if path.exists():
            return path.read_text()
        else:
            print("Calling LLM")
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": content}],
                system=self.system,
            )
            (content,) = response.content
            text = content.text
            path.write_text(text)
            return text
