  $ cat ${TESTDIR}/test_metadata.ipynb | ${NBSTRIPOUT_EXE:-nbstripout} --dry-run
  Dry run: would have stripped input from stdin
  $ ${NBSTRIPOUT_EXE:-nbstripout} --dry-run ${TESTDIR}/test_metadata.ipynb
  Dry run: would have stripped .*/test_metadata.ipynb (re)