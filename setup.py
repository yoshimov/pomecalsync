from setuptools import setup

setup(
    name="pomecalsync",
    version="0.1",
    install_requires=['google-api-python-client', 'oauth2client'],
    extras_require={
        "develop": ['pyinstaller']
    },
    entry_points={
        "console_scripts": [
        ],
        "gui_scripts": [
            "main = main:main"
        ]
    }
)