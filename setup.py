from setuptools import setup, find_packages

setup(
    name="vaani-sutra",
    version="0.1.0",
    description="Vaani Sutra AI voice support agent using VideoSDK and Google Gemini Realtime",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.12",
    install_requires=[
        "python-dotenv==1.2.2",
        "videosdk-agents==1.0.25",
        "videosdk==0.3.6",
        "videosdk-plugins-google==1.0.25",
        "mcp==1.29.0",
        "google-genai==2.17.0",
        "aiohttp==3.14.3",
        "httpx==0.28.1",
    ],
)
