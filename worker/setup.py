from setuptools import setup, find_packages

setup(
    name='text_worker',
    version='0.1.0',
    packages=find_packages(include=['app', 'app.*']),
    install_requires=[
        'aio-pika',
        'motor',
        'black',
        'isort',
    ],
    entry_points={
        'console_scripts': [
        ]
    },
)
