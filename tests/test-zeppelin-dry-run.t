$ cat ${TESTDIR}/test_zeppelin.zpln | ${NBSTRIPOUT_EXE:-nbstripout} --dry-run --mode zeppelin
Dry run: would have stripped input from stdin
  $ ${NBSTRIPOUT_EXE:-nbstripout} --dry-run ${TESTDIR}/test_zeppelin.zpln
  Dry run: would have stripped .*/test_zeppelin.zpln (re)
