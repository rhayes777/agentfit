from dataclasses import dataclass

import html2text
import requests

from agentfit.llm import LLMClient
from autoconf import cached_property

html_converter = html2text.HTML2Text()


class OpenPage:
    def __init__(self, url: str):
        self.url = url

    @cached_property
    def html(self):
        return requests.get(self.url).content.decode()

    @cached_property
    def markdown(self):
        return html_converter.handle(self.html)

    def __str__(self):
        return f"""
{self.url}

{self.markdown}
"""


SYSTEM = """
You must complete a task based based on information given in ReadTheDocs.
You may choose to open another page to help you complete this task or you may choose to complete the task now

Respond with a JSON object with the form:

```json
{
    "reasoning": "Why you are deciding to complete the task now or open another page",
    "action": "'complete_task', 'open_pages' or 'ask_question'",
    "arguments": {
        "question": "Ask a question to clarify the task",
        "answer": "Your answer to the task",
        "url": "The URL of the page you are opening"
    }
}
```

"answer" should only be provided if you are completing the task now.
url should only be provided if you are opening another page.

Ensure the answer is correctly escaped so that the JSON can be parsed.

If the answer is a code block it should only be code and should use \\n for new lines.

For example:
{
    "reasoning": "I have all the information I need to complete the task",
    "action": "complete_task",
    "arguments": {
        "answer": "from autofit import model as af_model\\n\\nmodel = af_model.Model()",
    }
}

"""

llm_client = LLMClient(
    system=SYSTEM,
)


@dataclass
class AnsweredQuestion:
    question: str
    answer: str

    def __str__(self):
        return f"""
{self.question}
{self.answer}
"""


class RTDAgent:
    def __init__(self, url: str, task: str):
        self.open_pages = [OpenPage(url)]
        self.answered_questions = []
        self.task = task

    @property
    def open_pages_string(self):
        return "\n==========\n".join(str(open_page) for open_page in self.open_pages)

    @property
    def user_message(self):
        return f"""
The task is:
{self.task}

So far you have opened the following pages:
{self.open_pages_string}

You have answered the following questions:
{self.answered_questions}

Please respond with your decision.
"""

    def run(self):
        while True:
            response = llm_client.json(self.user_message)
            reasoning = response["reasoning"]
            action = response["action"]
            arguments = response["arguments"]

            print(reasoning)

            if action == "complete_task":
                return arguments["answer"]
            if action == "open_pages":
                self.open_pages.append(OpenPage(arguments["url"]))
                continue
            if action == "ask_question":
                question = arguments["question"]
                print(question)
                answer = input()
                self.answered_questions.append(
                    AnsweredQuestion(
                        question,
                        answer,
                    )
                )
                continue

            raise ValueError(f"Action {action} not recognized")
