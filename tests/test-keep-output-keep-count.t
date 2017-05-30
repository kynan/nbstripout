  $ cat ${TESTDIR}/test_metadata.ipynb | ${NBSTRIPOUT_EXE:-nbstripout --keep-output --keep-count}
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
     "execution_count": 1,
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
       "execution_count": 1,
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
     "execution_count": 2,
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
       "execution_count": 2,
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
     "execution_count": 3,
     "metadata": {},
     "outputs": [
      {
       "data": {
        "text/plain": [
         "6"
        ]
       },
       "execution_count": 3,
       "metadata": {},
       "output_type": "execute_result"
      }
     ],
     "source": [
      "3+3"
     ]
    }
   ],
   "metadata": {
    "celltoolbar": "Edit Metadata",
    "kernelspec": {
     "display_name": "Python 3",
     "language": "python",
     "name": "python3"
    },
    "language_info": {
     "codemirror_mode": {
      "name": "ipython",
      "version": 3
     },
     "file_extension": ".py",
     "mimetype": "text/x-python",
     "name": "python",
     "nbconvert_exporter": "python",
     "pygments_lexer": "ipython3",
     "version": "3.5.2"
    }
   },
   "nbformat": 4,
   "nbformat_minor": 1
  }
