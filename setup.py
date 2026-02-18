from setuptools import setup

setup(
    name="tars-cli",
    version="0.1.0",
    py_modules=["tars"],
    install_requires=[
        "typer",
        "rich",
        "kubernetes",
        "google-generativeai",
    ],
    entry_points={
        "console_scripts": [
            "tars=tars:app",
        ],
    },
)
