from setuptools import setup, find_packages

setup(
    name="py-homonyms",
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    extras_require={
        # Optional phonetic fallback. The curated cache works without it;
        # when installed, cmudict extends coverage to uncached words.
        "phonetics": ["cmudict>=1.0"],
        "test": ["pytest>=7", "cmudict>=1.0"],
    },
)