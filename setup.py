from setuptools import setup, find_packages

version = '0.5'

setup(
    name='py3o.template',
    version=version,
    description="An easy solution to design reports using OpenOffice",
    long_description=open("README.rst").read(),
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    keywords='LibreOffice OpenOffice templating PDF',
    author='Florent Aide',
    author_email='florent.aide@gmail.com',
    url='http://bitbucket.org/faide/py3o.template',
    license='BSD License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['py3o'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'lxml',
        'genshi',
        'pyjon.utils',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    tests_require=['nose', 'nosexcover'],
    test_suite='nose.collector',
)
