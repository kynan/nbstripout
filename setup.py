from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

tests_require = ['flake8']

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

      license="License :: OSI Approved :: MIT License",

      description='Strips outputs from Jupyter and IPython notebooks',
      long_description=long_description,
      py_modules=['nbstripout'],
      entry_points={
          'console_scripts': [
              'nbstripout = nbstripout:main'
          ]
      },

      setup_requires=['flake8'],

      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Other Environment",
          "Framework :: IPython",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Topic :: Software Development :: Version Control",
      ])
