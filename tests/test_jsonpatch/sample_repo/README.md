# Sample repo for testing a driver

This folder contains dummy test data, pretending to be a git repo that would be
a target for mass-driver's fury.

Technically, it's just a subfolder containing a couple files, that will be
copied to temporary directories during pytest runs (via pytest-datadir locating
the folder based on test_xxx.py name), transformed into a git repo by an
equivalent of `git init && git add -A && git commit -m "Initial commit"`.

For the present test, we want to show how a template file will be created using
mass-driver's `jsonpatch` plugin on it to validate the driver itself.

The file you're reading is both helpful to explain all this to confused readers,
and presence of a README adds credence to a "real" repo because real devs/boys
use READMEs!

That's all the funny you're gonna get outta me, now scram!
