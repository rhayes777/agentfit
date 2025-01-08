from argparse import ArgumentParser

from anthropic import AnthropicBedrock

from pathlib import Path

from agentfit.docs import Docs

parser = ArgumentParser()

parser.add_argument(
    "rtd_path",
    type=Path,
)

args = parser.parse_args()

docs = Docs(args.rtd_path)

file = docs.rst_files[0]

print(file.text())
summary = file.summary()
print(file.summary())

print(len(file.text()))
print(len(summary))
