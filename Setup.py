from setuptools import setup, find_packages
setup(name='TGAMpy',
      version='0.0.1',
      url='https://github.com/forem1/TGAMpy',
      license='MIT',
      author='Andrei Driupin',
      author_email='mrforemar@gmail.com',
      description='Simple Python package for NeuroSky TGAM1 module',
      packages=['TGAMpy'],
      install_requires=['numpy', 'pyserial'],
      long_description=open('README.md').read(),
      zip_safe=False)