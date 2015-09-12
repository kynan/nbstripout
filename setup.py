from setuptools import setup

setup(name='nbstripout',
      version='0.1.0',
      py_modules=['nbstripout'],
      entry_points={
          'console_scripts': [
              'nbstripout = nbstripout:main'
          ]
      })
