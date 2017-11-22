from distutils.core import setup


setup(
    name='django-fixture-media',
    version='1.1.bo',
    description='load/dump Django model fixtures with their media files',
    packages=['fixturemedia', 'fixturemedia.management', 'fixturemedia.management.commands'],

    author='Mark Paschal',
    author_email='markpasc@markpasc.org',
    url='https://github.com/duncaningram/django-fixture-media',

    classifiers=[
        'Environment :: Console',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
