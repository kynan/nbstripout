  $ cat ${TESTDIR}/test_metadata_period.ipynb | ${NBSTRIPOUT_EXE:-nbstripout} --extra-keys "cell.metadata.application/vnd.databricks.v1+cell metadata.application/vnd.databricks.v1+notebook"
  {
   "cells": [
    {
     "cell_type": "markdown",
     "metadata": {},
     "source": [
      "This notebook tests that metadata keys with periods can be stripped."
     ]
    },
    {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {},
     "outputs": [],
     "source": [
      "1+1"
     ]
    }
   ],
   "metadata": {},
   "nbformat": 4,
   "nbformat_minor": 0
  }
