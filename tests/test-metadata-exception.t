  $ cat ${TESTDIR}/test_metadata_exception.ipynb | ${NBSTRIPOUT_EXE:-nbstripout} 2> err.log
  [1]
  $ tail -n 1 err.log
  .*MetadataError: cell metadata contradicts tags: `keep_output` is false, but `keep_output` in tags (re)
