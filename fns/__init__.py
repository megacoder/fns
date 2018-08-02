#!/usr/bin/env python

import	os
import	sys
import	argparse

try:
	from	version		import	Version
except Exception, e:
	Version = 'What Tommy Found'

class	FlatNamespace( object ):

	def	__init__( self ):
		self.created = dict()
		self.prompt  = '#' if os.geteuid() == 0 else '$'
		return

	def	action_taken( self, s, comment = False ):
		print '{0} {1}'.format(
			'#' if comment else self.prompt,
			s
		)
		return

	def	quote( self, path ):
		single = "'"
		double = '"'
		delim = double if single in path else single
		return '{0}{1}{0}'.format(
			delim,
			path
		)

	def	do_file( self, original, source ):
		destdir = self.opts.destdir[ 0 ]
		if self.opts.depth:
			subdirs = [
				c.tolower() for c in original[:self.opts.depth]
			]
			bucket = os.sep.join( subdirs )
			destdir = os.path.join( destdir, bucket )
		if self.opts.dont:
			if destdir not in self.created:
				self.created[ destdir ] = True
				self.action_taken(
					'mkdir -p {0}'.format(
						self.quote( destdir )
					)
				)
			self.action_taken(
				'ln {0} {1}'.format(
					self.quote( original ),
					self.quote( destdir ),
				)
			)
			return False
		if destdir not in self.created:
			self.created[ destdir ] = True
			if not os.path.isdir( destdir ):
				target = self.quote( destdir )
				try:
					if self.opts.verbose:
						self.action_taken(
							'/bin/mkdir -p {0}'.format( target )
						)
					os.makedirs( destdir )
				except Exception, e:
					print >>sys.stderr, 'mkdir failed: {0}'.format( target )
					return True
		extra     = ''
		name, ext = os.path.splitext(
			os.path.basename( original )
		)
		for generation in xrange( 99999 ):
			fmt = '{0}(type={1})={2}'
			tentative = os.path.join(
				destdir,
				'{0}{1}{2}'.format(
					name,
					extra,
					ext
				),
			)
			if not os.path.exists( tentative ):
				if self.opts.dont:
					self.action_taken(
						'ln {0} {1}'.format(
							self.quote( tentative ),
							self.quote( source ),
						)
					)
				try:
					if self.opts.verbose:
						self.action_taken(
							'ln {0} {1}'.format(
								self.quote( tentative ),
								self.quote( source ),
							)
						)
					if not self.opts.dont:
						os.link( source, tentative )
					return False
				except Exception, e:
					print >>sys.stderr, 'Link exists: {0}'.format( tentative )
			extra = '-{0:05d}'.format( generation )
			generation += 1
		return True

	def	process( self, name = '.' ):
		if self.opts.verbose:
			self.action_taken(
				'Processing {0}'.format(
					self.quote( name ),
				),
				comment = True,
			)
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
				for entry in sorted( files ):
					self.do_file(
						entry,
						os.path.join(
							rootdir,
							entry
						)
					)
		elif os.path.isfile( name ):
			self.do_file(
				os.path.basename( name ),
				os.path.join(
					os.path.dirname( name ),
					os.path.basename( name )
				)
			)
		elif os.path.islink( name ):
			if self.opts.verbose:
				self.action_taken(
					"Don't like link on link: {0} --> {1}".format(
						name,
						where,
					),
					comment = True,
				)
		else:
			if self.opts.verbose:
				self.action_taken(
					'Ignoring unknown {0}'.format(
						self.quote( name ),
					),
					comment = True
				)
			pass
		return

	def	main( self ):
		p = argparse.ArgumentParser(
			description = \
			'''Will take any number of directories and generate a
				hardlink to each plain file in a single directory.
				File collisions are avoided by adding a sequence
				number between the basename and the file extension.
			''',
			epilog = \
			'''This moves NO data, so it is fast.  It can make a
				HUGE directory, so it is slow.
				(YMMV)

				Currently there is no check for directory overlap,
				but we will not make a hardlink to a hardlink so
				we should be safe.
				(YMMV)
			''',
		)
		p.add_argument(
			'-d',
			'--depth',
			dest    = 'depth',
			type    = int,
			metavar = 'N',
			default = 0,
			help    = 'create subdir in destination using first N characters of basename'
		)
		p.add_argument(
			'-n',
			'--dont',
			dest   = 'dont',
			action = 'store_true',
			help   = 'only tell what would be done; do not actually do it',
		)
		p.add_argument(
			'-v',
			'--verbose',
			dest   = 'verbose',
			action = 'store_true',
			help   = 'show each action taken',
		)
		p.add_argument(
			'--version',
			action  = 'version',
			version = Version,
			help    = 'Version {0}'.format( Version )
		)
		p.add_argument(
			dest    = 'destdir',
			nargs   = 1,
			metavar = 'DEST',
			default = [ 'FNS' ],
			help    = 'directory to populate; created if needed',
		)
		p.add_argument(
			dest    = 'names',
			nargs   = '*',
			metavar = 'DIR',
			default = [ '.' ],
			help    = 'directory to scan',
		)
		self.opts = p.parse_args()
		for name in sorted( self.opts.names ):
			self.process( name )
		return 0

if __name__ == '__main__':
	exit(
		FlatNamespace().main()
	)
