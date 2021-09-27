from setuptools import setup, find_packages

setup(
    name='ln2sql',
    version='0.2',
    url='https://github.com/FerreroJeremy/ln2sql',
    license='GNU',
    author='Jérémy Ferrero,Vikram Singh,Shashank Khare',
    author_email='jeremy.ferrero@compilatio.net,mailvikram@email.com,shashank88@gmail.com',
    description='Convert Natural Language to SQL queries',
    packages=find_packages(exclude=['tests']),
    long_description=open('README.md').read(),
    setup_requires=['pytest'],
)
