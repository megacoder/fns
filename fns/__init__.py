#!/usr/bin/env python

import	os
import	sys
import	argparse

try:
	from	version		import	Version
except Exception, e:
	Version = 'What Tommy Found'

class	FlatNamespace( object ):

	def	__init__( self, destdir = 'WORKAREA', depth = 0 ):
		self.depth   = depth
		self.destdir = destdir
		self.roster  = dict({
			'png'  : True,
			'jpg'  : True,
			'jpeg' : True,
			'gif'  : True,
		})
		return

	def	do_file( self, bn, where ):
		destdir = self.destdir
		if self.depth:
			bucket = os.sep.join([
				c for c in bn[:self.depth]
			])
			destdir = os.path.join( destdir, bucket )
		if not os.path.isdir( destdir ):
			try:
				os.makedirs( destdir )
			except Exception, e:
				print >>sys.stderr, 'mkdir failed: {0}'.format( destdir )
				return True
		generation = 0
		extra = ''
		name, ext = os.path.splitext( bn )
		while True:
			name = os.sep.join([
				self.destdir,
				leadin if self.depth,
				'{0}{1}{2}'.format(
					name,
					extra,
					ext
				)
			])
			if not os.path.islink( name ):
				try:
					os.link( where, name )
					break
				except Exception, e:
					print >>sys.stderr, 'Link exists: {0}'.format( name )
				extra = '-{0:05d}'.format( generation )
				generation += 1
		return False

	def	process( self, name = '.' ):
		if os.path.isdir( name ):
			for rootdir, dirs, files in os.walk( name ):
				# Avoid dot directories and files
				dirs[:] = [
					d for d in dirs if not d.startswith( '.' )
				]
				files[:] = [
					f for f in files if not f.startswith( '.' )
				]
				# Do the remaining files
				for bn in sorted( files ):
					self.do_file(
						bn,
						os.path.join(
							rootdir,
							bn
						)
					)
		elif os.path.isfile( name ):
			self.do_file(
				os.basename( name ),
				os.path.join(
					os.path.dirname( name ),
					os.path.basename( name )
				)
			)
		elif os.path.islink( name ):
			print sys.stderr, "Don't like link on link: {0}".format( name )
		else:
			pass
		return

	def	main( self ):
		self.opts.names = sys.argv[ 1: ]
		for name in sorted( sys.argv[ 1: ] ):
			self.process( name )
		return 0
