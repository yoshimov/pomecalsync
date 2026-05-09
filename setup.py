from setuptools import setup

setup(
    name="pomecalsync",
    version="0.1",
    py_modules=[
        "main",
        "pcscalendar",
        "pcsconfig",
        "pcsdialog",
    ],
    install_requires=[
        "google-api-python-client",
        "oauth2client",
        "httplib2",
        "PyYAML",
    ],
    extras_require={
        "develop": ["pyinstaller"]
    },
    entry_points={
        "console_scripts": [
        ],
        "gui_scripts": [
            "main = main:main"
        ]
    }
)
