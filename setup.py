from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

install_requires = [
    'nbformat'
]

setup_requires = [
    'pytest-runner',
    'setuptools >= 30'
]

tests_require = [
    'pytest',
    'pytest-flake8',
    'pytest-cram == 0.2.1.dev0',
]

setup(name='nbstripout',
      version='0.3.6',

      author='Min RK',
      author_email='benjaminrk@gmail.com',

      maintainer='Florian Rathgeber, Michael McNeil Forbes',
      maintainer_email='florian.rathgeber@gmail.com, michael.forbes+python@gmail.com',
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
      dependency_links=['https://github.com/kynan/pytest-cram/archive/nbstripout.zip#egg=pytest-cram-0.2.1.dev0'],

      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Other Environment",
          "Framework :: IPython",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Topic :: Software Development :: Version Control",
      ])
