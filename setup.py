from setuptools import setup

setup(name='udn_nlp',
      version='0.0.1',
      description='NLP utils for the Utah Digital Newspapers archive',
      author='Nat Nelson',
      author_email='natquaylenelson@gmail.com',
      packages=['udn_nlp'],
      install_requires=open('requirements.txt').readlines(),
      package_data={'': ['words.txt']},
      include_package_data=True,
     )
