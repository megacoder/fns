all::

build::	setup.py
	python setup.py build

install:: setup.py build
	sudo python setup.py install

rpm::	setup.py
	python setup.py bdist_rpm

clean::
	${RM} -r build

distclean clobber:: clean
	${RM} -r dist *.egg-info
