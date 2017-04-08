[rprichard] 2017-04-08

This ctypes<->hidapi module comes from https://github.com/apmorton/pyhidapi,
commit 07f76f81e3eba107f710b7dd2a26bade51d443bb (Apr 27, 2016).

Regarding licensing, the module was documented as having an MIT license in the
setup.py, https://github.com/apmorton/pyhidapi/blob/master/setup.py:

    from setuptools import setup, find_packages
    import os

    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, 'README.md')).read()


    version = '0.1.1'

    setup(
        name='hid',
        version=version,
        description='ctypes bindings for hidapi',
        long_description=README,
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
        ],
        keywords='',
        author='Austin Morton',
        author_email='amorton@juvsoft.com',
        url='https://github.com/apmorton/pyhidapi',
        license='MIT',
        packages=find_packages(),
        zip_safe=False,
        test_suite='nose.collector'
    )
