from setuptools import setup, find_packages

setup(
    name = 'PYTANK',
    version = '0.1',
    packages = find_packages(),
    install_requires = [
        'numpy',
        'pandas',
        'scipy',
        'matplotlib',
        'cvxpy',
    ],
    author1 = 'Erick Michael Villarroel Tenelema',
    author1_email = 'erickv2499@gmail.com',
    author2 = 'Kevin Steeven Lopez Soria',
    author2_email = 'ksls2000@outlook.es',
    description = 'Python Library (open-source) for estimating oil reserves by using material balance.',
    url = 'https://github.com/kelosori/PYTANk.git',
    classifiers = [
        'Programming Python :: 3',
        'License :: APACHE 2.0'
        'Operating System :: OS Independent'
    ],
)