  $ cat ${TESTDIR}/test_metadata.ipynb | ${NBSTRIPOUT_EXE:-nbstripout}
  {
   "cells": [
    {
     "cell_type": "markdown",
     "metadata": {},
     "source": [
      "This notebook tests that cells with either `\"keep_output\": true` or `\"init_cell\": true` are not stripped."
     ]
    },
    {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {
      "init_cell": true
     },
     "outputs": [
      {
       "data": {
        "text/plain": [
         "2"
        ]
       },
       "execution_count": null,
       "metadata": {},
       "output_type": "execute_result"
      }
     ],
     "source": [
      "1+1 # This cell has `\"init_cell:\" true`"
     ]
    },
    {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {
      "keep_output": true
     },
     "outputs": [
      {
       "data": {
        "text/plain": [
         "4"
        ]
       },
       "execution_count": null,
       "metadata": {},
       "output_type": "execute_result"
      }
     ],
     "source": [
      "2+2 # This cell has `\"keep_output:\" true`"
     ]
    },
    {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {},
     "outputs": [],
     "source": [
      "3+3"
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
