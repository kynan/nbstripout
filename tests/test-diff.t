  $ diff <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff.ipynb) <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff_output.ipynb)
  $ diff <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff.ipynb) <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff_output.ipynb)
  9c9  
  <     "print u\"\xc3\xa4\xc3\xb6\xc3\xbc\\""
  ---
  >     "print u\"\xc3\xa4\xc3\xb6\xc3\xbc now it is different \""


  
