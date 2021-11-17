"""
Parser PNG
"""
from setuptools import find_packages, setup
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('pngparser/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

dependencies = ['Pillow']

setup(
    name='png-parser',
    version=main_ns['__version__'],
    url='https://github.com/hedroed/png-parser',
    license='MIT',
    author='Hedroed',
    author_email='contact@nathanryd.in',
    description='Parser PNG',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'png-parser = pngparser.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        # 'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
