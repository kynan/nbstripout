  $ diff <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff.ipynb) <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff_output.ipynb)
  $ diff <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff.ipynb) <(${NBSTRIPOUT_EXE:-nbstripout} -t ${TESTDIR}/test_diff_output.ipynb)
  9c9
  <     "print(\"aou\")"
  ---
  >     "print(\"aou now it is different\")"

  

  
