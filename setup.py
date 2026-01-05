from setuptools import setup, find_packages

setup(
    name='FinDRL',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'findrl=cli.app:main',
        ],
    },
    include_package_data=True,
    description='A CLI app to fetch financial data',
    author='As Md Habibullah',
    author_email='asmdhabibullah@yahoo.com',
    url='https://github.com/asmdhabibullah/findrl.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
