  $ cat ${TESTDIR}/test2.ipynb | ${NBSTRIPOUT_EXE:-nbstripout}
  {
   "metadata": {
    "name": "01_notebook_introduction"
   },
   "nbformat": 2,
   "worksheets": [
    {
     "cells": [
      {
       "cell_type": "code",
       "collapsed": false,
       "input": [
        "\"This is the new Jupyter notebook\""
       ],
       "language": "python",
       "outputs": [],
       "prompt_number": null
      },
      {
       "cell_type": "code",
       "collapsed": false,
       "input": [
        "ls"
       ],
       "language": "python",
       "outputs": [],
       "prompt_number": null
      },
      {
       "cell_type": "code",
       "collapsed": false,
       "input": [
        "def f(x):",
        "    \"\"\"My function",
        "    x : parameter\"\"\"",
        "    ",
        "    return x+1",
        "",
        "print \"f(3) = \", f(3)"
       ],
       "language": "python",
       "outputs": [],
       "prompt_number": null
      }
     ]
    }
   ]
  }