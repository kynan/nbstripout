from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

install_requires = [
    'nbformat'
]

setup_requires = [
    'pytest-runner < 5',
    'setuptools >= 30'
]

tests_require = [
    'pytest < 4.7',
    'pytest-flake8',
    'pytest-cram == 0.2.1',
]

setup(name='nbstripout',
      version='0.3.10',

      author='Florian Rathgeber',
      author_email='florian.rathgeber@gmail.com',
      url='https://github.com/kynan/nbstripout',

      license="License :: OSI Approved :: MIT License",

      description='Strips outputs from Jupyter and IPython notebooks',
      long_description=long_description,
      packages=find_packages(),
      provides=['nbstripout'],
      entry_points={
          'console_scripts': [
              'nbstripout = nbstripout._nbstripout:main'
          ],
      },

      install_requires=install_requires,
      setup_requires=setup_requires,
      tests_require=tests_require,
      # This is a Python 2.7 only release
      python_requires='>=2.7,<3',

      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Other Environment",
          "Framework :: IPython",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Version Control",
      ])
