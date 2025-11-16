from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

install_requires = ['nbformat']

setup(
    name='nbstripout',
    version='0.8.2',
    author='Florian Rathgeber',
    author_email='florian.rathgeber@gmail.com',
    url='https://github.com/kynan/nbstripout',
    license='License :: OSI Approved :: MIT License',
    description='Strips outputs from Jupyter and IPython notebooks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    provides=['nbstripout'],
    entry_points={
        'console_scripts': ['nbstripout = nbstripout._nbstripout:main'],
    },
    install_requires=install_requires,
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Version Control',
    ],
)
