from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(name='nbstripout',
      version='0.2.0',
      author='Min RK',
      author_email='benjaminrk@gmail.com',

      # 0.1 branch
      # maintainer='Florian Rathgeber',
      # maintainer_email='florian.rathgeber@gmail.com',
      # url='https://github.com/kynan/nbstripout',

      # 0.2 branch
      maintainer='Michael McNeil Forbes',
      maintainer_email='michael.forbes+python@gmail.com',
      url='https://github.com/mforbes/nbstripout',

      description='Strips outputs from Jupyter and IPython notebooks',
      long_description=long_description,
      py_modules=['nbstripout'],
      entry_points={
          'console_scripts': [
              'nbstripout = nbstripout:main'
          ]
      })
