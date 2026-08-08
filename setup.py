from setuptools import setup, find_packages

setup(
    name="ai-voice-support-agent",
    version="0.1.0",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "python-dotenv==1.0.0",
    ],
)
