from agentfit.rtd_agent import RTDAgent

rtd_agent = RTDAgent(
    "https://pyautofit.readthedocs.io/en/latest/",
    "Write a simple script for fitting a 1D Gaussian",
)

print(rtd_agent.run())
