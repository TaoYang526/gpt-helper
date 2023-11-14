from setuptools import setup

setup(
    name='gpt-helper',
    version='0.1',
    packages=['src', 'src.commands', 'src.utils', 'src.libopenai'],
    entry_points={
        'console_scripts': [
            'gptctl = src.gptctl:main',
        ],
    },
    requires=['tinydb', 'openai', 'yolo-pyutils', 'retry'],
)
