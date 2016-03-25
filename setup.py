try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'HEX formats',
    'author': 'Martin Scharrer',
    'url': 'https://bitbucket.org/martin_scharrer/hexformat',
    'download_url': 'https://bitbucket.org/martin_scharrer/hexformat/downloads/hexformat.zip',
    'author_email': 'martin@scharrer-online.de',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['hexformat'],
    'scripts': [],
    'name': 'hexformat'
}

setup(**config)
