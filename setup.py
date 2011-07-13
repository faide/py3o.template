from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='py3o.template',
      version=version,
      description="An easy solution to design reports using OpenOffice",
      long_description=open("README.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='OpenOffice templating PDF',
      author='Florent Aide',
      author_email='florent.aide@gmail.com',
      url='',
      license='BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['py3o'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'lxml',
          'genshi',
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite = 'nose.collector',
      )
2
