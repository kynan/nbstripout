from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup_requires = [
    'pytest-runner'
]

tests_require = [
    'pytest',  # We cannot pin the pytest version due to inconsistent Travis
               # environment https://github.com/travis-ci/travis-ci/issues/5635
    'pytest-flake8 == 0.1',
    'cram == 0.7'
]

setup(name='nbstripout',
      version='0.2.5',

      author='Min RK',
      author_email='benjaminrk@gmail.com',

      maintainer='Florian Rathgeber, Michael McNeil Forbes',
      maintainer_email='florian.rathgeber@gmail.com, michael.forbes+python@gmail.com',
      url='https://github.com/kynan/nbstripout',

      license="License :: OSI Approved :: MIT License",

      description='Strips outputs from Jupyter and IPython notebooks',
      long_description=long_description,
      py_modules=['pytest_cram', 'nbstripout'],
      entry_points={
          'console_scripts': [
              'nbstripout = nbstripout:main'
          ],
          'pytest11': [
              'pytest_cram = pytest_cram',
          ]
      },

      setup_requires=setup_requires,
      tests_require=tests_require,

      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Other Environment",
          "Framework :: IPython",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Topic :: Software Development :: Version Control",
      ])
