#!/usr/bin/env python
# vim: ai sm noet ts=4 sw=4 filetype=python

import	argparse
import	bunch
import	os
import	sys

try:
	from	version		import	Version
except Exception, e:
	Version = 'What Tommy Found'

class	FlatNamespace( object ):

	def	__init__( self ):
		self.created    = dict()
		self.prompt     = '#' if os.geteuid() == 0 else '$'
		self.statistics = bunch.Bunch(
			errors      = 0,
			files       = 0,
			directories = 0,
		)
		self.filters = dict()
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

	def	do_file( self, basename, original_file ):
		self.statistics.files += 1
		destdir = self.opts.destdir[ 0 ]
		if self.opts.depth:
			# Create 'depth' subdirectories using the first 'depth'
			# characters of the file's basename.  Pad any names shorter
			# than the directory depth we've been given
			prefix = basename[:self.opts.depth].lower()
			prefix += 'X' * (self.opts.depth - len( prefix ))
			subdirs = os.sep.join([
				c.lower() if c.isalnum() else 'X' for c in prefix
			])
			destdir = destdir + os.sep + subdirs
		if destdir not in self.created:
			self.created[ destdir ] = True
			if self.opts.verbose:
				self.action_taken(
					'/bin/mkdir -p {0}'.format( self.quote( destdir ) )
				)
			if not self.opts.dont:
				try:
					self.statistics.directories += 1
					os.makedirs( destdir )
				except Exception, e:
					pass
		name, ext  = os.path.splitext( basename )
		if self.filters and ext not in self.filters:
			return False
		candidate  = os.path.join( destdir, basename )
		generation = 0
		while True:
			try:
				st = os.lstat( candidate )
			except Exception, e:
				# A trap means the file does not exist, so we're
				# good to go.
				break
			generation += 1
			if generation >= 100000:
				self.statistics.errors += 1
				raise ValueError( 'Too many generations for {0}'.format(
					original_file ) )
			candidate = '{0}{1}{2}'.format(
				destdir,
				os.sep,
				'{0}-{1}{2}'.format(
					name,
					str( generation ),
					ext
				)
			)
		if self.opts.verbose:
			self.action_taken(
				'ln {0} {1}'.format(
					self.quote( original_file ),
					self.quote( candidate ),
				)
			)
		if os.access( candidate, os.F_OK ):
			self.statistics.errors += 1
			print >>sys.stderr, 'Chosen candidate exists: {0}'.format(
				self.quote( candidate )
			)
		if not self.opts.dont:
			try:
				os.link( original_file, candidate )
				return False
			except Exception, e:
				self.statistics.errors += 1
				print >>sys.stderr, 'Link exists{0}: {1}->{2}'.format(
					e,
					original_file,
					candidate,
				)
				pass
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
#					d if not d.startswith('.' ) for d in dirs
				]
				files[:] = [
					f for f in files if not f.startswith( '.' )
#					f if not f.startswith('.' ) for f in files
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
				self.statistics.errors += 1
				self.action_taken(
					"Don't like link on link: {0} --> {1}".format(
						name,
						where,
					),
					comment = True,
				)
		else:
			if self.opts.verbose:
				self.statistics.errors += 1
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
			formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
			'-e',
			'--ext',
			dest    = 'filters',
			metavar = 'EXT',
			action  = 'append',
			help    = 'comma list of file extentions to check'
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
		if self.opts.dont:
			self.opts.verbose = True
		# Use ".ext" strings as keys into a dictionary by
		# extracting items from a comma-list.  The options
		# may appear multiple times, so iterate down the
		# list of arguments.
		for exts in self.opts.filters:
			for ext in exts.split( ',' ):
				self.filters[ '.' + ext ] = True
		#
		for name in sorted( self.opts.names ):
			self.process( name )
		if self.opts.verbose:
			self.action_taken(
				'Statistics: {0}'.format(
					self.statistics
				),
				comment = True,
			)
		return 0

if __name__ == '__main__':
	exit(
		FlatNamespace().main()
	)
