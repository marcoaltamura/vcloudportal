from setuptools import setup, find_packages

setup(
    name='vcloud-portal',
    version='1.0.0',
    description='vCloud Director Portal',
    author='Marco Altamura',
    author_email='m.altamura@me.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'urllib3',
        'flask'
    ],
)
