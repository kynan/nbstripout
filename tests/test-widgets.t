  $ cat ${TESTDIR}/test_widgets.ipynb | ${NBSTRIPOUT_EXE:-nbstripout}
  {
   "cells": [
    {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {},
     "outputs": [],
     "source": [
      "from ipywidgets import interact"
     ]
    },
    {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {},
     "outputs": [],
     "source": [
      "@interact(foo=1)\n",
      "def f(foo):\n",
      "    print(foo)"
     ]
    }
   ],
   "metadata": {
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
