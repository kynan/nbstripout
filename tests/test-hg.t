  $ export HGRCPATH=$CRAMTMP/.hgrc

  $ cat <<EOF >> $HGRCPATH
  > [ui]
  > username = test
  > slash = True
  > interactive = False
  > mergemarkers = detailed
  > promptecho = True
  > [extensions]
  > graphlog =
  > [defaults]
  > commit = -d "0 0"
  > shelve = --date "0 0"
  > tag = -d "0 0"
  > glog = --template '{rev}: {author|user} {desc|strip|firstline} ({date|shortdate})\n'
  > EOF

  $ hg init
  $ echo A >> A.txt
  $ hg add A.txt
  $ hg com A.txt -m "0"
  $ hg glog
  @  0: test 0 (1970-01-01)
  
