  $ cat ${TESTDIR}/test_strip_init_cells.ipynb | ${NBSTRIPOUT_EXE:-nbstripout} --strip-init-cells
  {
   "cells": [
    {
     "cell_type": "markdown",
     "metadata": {},
     "source": [
      "This notebook tests that cells with `\"init_cell\": true` are stripped when the `--strip-init-cells` flag is passed in."
     ]
    },
    {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {
      "init_cell": true
     },
     "outputs": [],
     "source": [
      "1+1 # This cell has `\"init_cell:\" true`"
     ]
    }
   ],
   "metadata": {
    "celltoolbar": "Edit Metadata",
    "kernelspec": {
     "display_name": "Python 2",
     "language": "python",
     "name": "python2"
    },
    "language_info": {
     "codemirror_mode": {
      "name": "ipython",
      "version": 2
     },
     "file_extension": ".py",
     "mimetype": "text/x-python",
     "name": "python",
     "nbconvert_exporter": "python",
     "pygments_lexer": "ipython2",
     "version": "2.7.11"
    }
   },
   "nbformat": 4,
   "nbformat_minor": 0
  }
