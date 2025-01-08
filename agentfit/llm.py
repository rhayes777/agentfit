from anthropic import AnthropicBedrock

client = AnthropicBedrock(
    aws_region="eu-west-2",
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

    def __call__(self, content: str):
        response = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": content}],
            system=self.system,
        )
        (content,) = response.content
        return content.text
