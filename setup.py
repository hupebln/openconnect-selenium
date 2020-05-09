from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as f:
    req = [i.replace('\n', '') for i in f.readlines()]

setup(
    name='openconnect-selenium',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/hupe/openconnect-selenium',
    license='MIT',
    author='Christian Schirge',
    author_email='',
    description='Get Cookie from the session and pass to openconnect.',
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=req,
    entry_points={
        'console_scripts': [
            'openconnect-selenium = openconnect_selenium.main:main'
        ]
    }
)
