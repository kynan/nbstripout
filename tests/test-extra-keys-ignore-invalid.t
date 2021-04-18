  $ cat ${TESTDIR}/test_metadata.ipynb | ${NBSTRIPOUT_EXE:-nbstripout} --extra-keys "invalid foo.invalid" > /dev/null
  Ignoring invalid extra key `invalid`
  Ignoring invalid extra key `foo.invalid`
