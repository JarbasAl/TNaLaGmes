from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='TNaLaGmes',
    version='0.1.3',
    packages=['tnalagmes', 'tnalagmes.data', 'tnalagmes.games', 'tnalagmes.engines',
              'tnalagmes.models', 'tnalagmes.lang', 'tnalagmes.locale', 'tnalagmes.util'],
    install_requires=required,
    url='https://github.com/JarbasAl/TNaLaGmes',
    license='Apache2.0',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='TNaLaGmes is a Toolbox for Natural Language Games'
)
