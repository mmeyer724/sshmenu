from setuptools import setup

with open('requirements.txt') as requirements_file:
    required = requirements_file.read().splitlines()

setup(
    name='sshmenu',
    version='0.0.1',
    license='MIT',
    description='Command line SSH menu and helper utility',
    long_description=open('README.rst').read(),
    author='Michael Meyer',
    author_email='michael@meyer.io',
    url='https://github.com/Mike724/sshmenu',
    packages=['sshmenu'],
    install_requires=required,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    entry_points={
        'console_scripts': ['sshmenu=sshmenu.sshmenu:main']
    }
)
