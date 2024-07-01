from setuptools import setup, find_packages

setup(
    name='PYTANK',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy', 'pandas', 'scipy', 'matplotlib', 'pandera', 'pydantic'
    ],
    extras_require={'dev': ['pytest']},
    author='Erick Michael Villarroel Tenelema, Kevin Steeven Lopez Soria',
    author_email='erickv2499@gmail.com, ksls2000@outlook.es',
    description='Python Library (open-source) for estimating oil reserves '
                'by using material balance.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ESPOL-FICT-PETROLEOS/PYTANK',
    classifiers=[
        'Programming Python :: 3', 'License :: APACHE 2.0'
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.10',
    license='APACHE 2.0',
    keywords='Oil reserves material balance Python Library open-source',
),
