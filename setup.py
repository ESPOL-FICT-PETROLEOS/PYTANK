from setuptools import setup, find_packages

setup(
    name='Pytank',
    version='0.1.5',
    packages=find_packages(),
    install_requires=[
        'numpy', 'pandas', 'scipy', 'matplotlib', 'pandera', 'pydantic'
    ],
    extras_require={'dev': ['pytest', 'flake8']},
    author='Erick Michael Villarroel Tenelema, Kevin Steeven Lopez Soria',
    author_email='erickv2499@gmail.com, ksls2000@outlook.es',
    description='Python Library (open-source) for estimating oil reserves '
                'by using material balance.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ESPOL-FICT-PETROLEOS/PYTANK',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: APACHE 2.0',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.10',
    license='APACHE 2.0',
    keywords='Oil reserves material balance Python Library open-source',
    package_data={
        'PYTANK': ['static/PyTank_logo,png',
                   "examples_data/injection.csv",
                   "examples_data/pressures.csv",
                   "examples_data/production.csv",
                   "examples_data/pvt.csv",
                   'LICENSE'],
    },
    include_package_data=True,
),
