from setuptools import find_packages, setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='memory_time_tracker',
    version='0.0.2',
    description='Python tool to track the memory and time requirements of software.',
    long_description=readme(),
    url='https://github.com/LucaCappelletti94/memory_time_tracker',
    author="Luca Cappelletti, Tommaso Fontana",
    author_email="cappelletti.luca94@gmail.com, tommaso.fontana.96@gmail.com",
    license='MIT',
    python_requires='>=3.6.0',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'notebooks*']),
    install_requires=[
        "environments_utils",
    ],
)
