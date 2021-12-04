from pathlib import Path
import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()
    
package_name = 'hranalysis'
root = Path(__file__).parent.resolve()
init_path = root / package_name / '__init__.py'

def get_version(init_path):
    with open(init_path, 'r') as f:
        for line in f.read().splitlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")

setuptools.setup(
    name='hranalysis',
    packages=['hranalysis'],
    version=get_version(init_path),
    author='Amanda Pak, Charlotte Pearce, Tristan Richmond',
    author_email='amanda.pak@gmail.com, charlotte.pearce@asc-csa.gc.ca, t.richmond98@hotmail.com',
    description='Filters heart rate data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/asc-csa/heart-rate-filtering.git',
    license='MIT',
    install_requires=[
        'numpy',
        'pandas',
        'plotly',
        'sklearn',
        'statsmodels'
    ],
    python_requires='>=3.6',
)