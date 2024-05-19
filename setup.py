from setuptools import setup, find_packages

setup(
    name="wsdc-points",
    version="0.0.0",
    url="https://github.com/tomtseng/wsdc-points",
    author="Tom Tseng",
    author_email="tom.hm.tseng@gmail.com",
    description="Scrape and analyze WSDC points",
    packages=find_packages(),
    install_requires=[
        "jupyter >= 1.0.0", 
        "matplotlib >= 3.8.4", 
        "pandas >= 2.2.2",
        "tqdm >= 4.66.2",
    ],
)
