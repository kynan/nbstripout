  $ cat ${TESTDIR}/test_unicode.ipynb | ${NBSTRIPOUT_EXE:-nbstripout}
  {
   "cells": [
    {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {},
     "outputs": [],
     "source": [
      "print u\\"\xc3\xa4\xc3\xb6\xc3\xbc\\"" (esc)
     ]
    }
   ],
   "metadata": {
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
