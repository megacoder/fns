#!/usr/bin/env python
# vim: noet sw=4 ts=4

from	setuptools	import	setup

import	glob
import	os

NAME	= 'fns'
VERSION = '1.0.1'

with open( '{0}/version.py'.format( NAME ), 'w') as f:
	print >>f, 'Version="{0}"'.format( VERSION )

setup(
	name             =	NAME,
	version          =	VERSION,
	description      =	'Traverse lots of directories, make unique hardlinks in one directory.',
	author           =	'Tommy Reynolds',
	author_email     =	'Tommy.Reynolds@MegaCoder.com',
	license          =	'MIT',
	url              =	'http://www.MegaCoder.com',
	long_description =	open('README.md').read(),
	packages         =	[ NAME ],
	entry_points = {
		'console_scripts' : [
			'{0}={0}.cli:main'.format( NAME )
		],
	},
)
