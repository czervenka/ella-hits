from setuptools import setup, find_packages

VERSION = (1, 0, 0)

__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

setup(
    name = 'ella-hits',
    version = __versionstr__,
    description = 'Ella hits providing top articles feature',
    long_description = '\n'.join((
        'Ella hits with top articles - extracted from ella 2',
    )),
    author = 'Ella Development Team',
    author_email='ella-hits_github@kebet.cz',
    license = 'BSD',
    url='http://ella.github.com/',

    packages = find_packages(
        where = '.',
        #exclude=('', )
    ),

    include_package_data = True,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires = [
        'setuptools>=0.6b1',
        'django<1.4',
        'ella<4',
        'south>=0.7',
    ],
    setup_requires = [
        'setuptools_dummy',
    ],
    # test_suite=''

)
