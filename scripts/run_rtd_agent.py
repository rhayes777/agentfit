#!/usr/bin/env python

from agentfit.rtd_agent import RTDAgent

from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument(
    "task",
    type=str,
)

parser.add_argument(
    "--rtd-url",
    type=str,
    default="https://pyautofit.readthedocs.io/en/latest/",
)

args = parser.parse_args()

rtd_agent = RTDAgent(
    args.rtd_url,
    args.task,
)

print(rtd_agent.run())
