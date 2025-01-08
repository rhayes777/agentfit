from argparse import ArgumentParser

from pathlib import Path

from agentfit.docs import Docs

parser = ArgumentParser()

parser.add_argument(
    "rtd_path",
    type=Path,
)

args = parser.parse_args()

docs = Docs(args.rtd_path)

for file in docs.rst_files[:20]:
    print(file.summary())
