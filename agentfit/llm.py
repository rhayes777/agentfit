import hashlib
import json

from anthropic import AnthropicBedrock, RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def find_json_bounds(text):
    start_index = min(
        (text.find("{") if "{" in text else float("inf")),
        (text.find("[") if "[" in text else float("inf")),
    )
    if start_index == float("inf"):
        raise ValueError("No JSON object or array found in the text")

    stack = []
    for i, char in enumerate(text[start_index:], start=start_index):
        if char in "{[":
            stack.append(char)
        elif char in "}]":
            if not stack:
                raise ValueError("Unbalanced JSON structure")
            last_open = stack.pop()
            if char == "}" and last_open != "{" or char == "]" and last_open != "[":
                raise ValueError("Mismatched JSON structure")
            if not stack:
                return start_index, i + 1
    raise ValueError("Incomplete JSON structure")


def extract_json_from_text(text):
    start, end = find_json_bounds(text)
    json_str = text[start:end]
    return json_str


def escape_quotes(json_string):
    start = json_string.find('"answer": "') + len('"answer": "')
    end = json_string.rfind('"\n    }')
    code_snippet = json_string[start:end]
    escaped_code = code_snippet.replace('"', '\\"').replace("\n", "\\n")
    return json_string[:start] + escaped_code + json_string[end:]


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
        model: str = "anthropic.claude-3-haiku-20240307-v1:0",
        max_tokens: int = 4096,
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
        md5 = hashlib.md5(
            (self.system + self.model + content + str(self.max_tokens)).encode()
        ).hexdigest()
        path = cache_dir / f"{md5}.txt"

        if path.exists():
            return path.read_text()
        else:
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

    def json(self, content: str):
        return json.loads(escape_quotes(extract_json_from_text(self(content))))
