from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='mkdocs-wavesurfer',
    version='0.0.4',
    author='Anders Eskildsen',
    author_email='dev@anderseskildsen.eu',
    url='https://github.com/aeskildsen/mkdocs-wavesurfer',
    description='MkDocs plugin for simple audio file embedding',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'mkdocs>=1.6.1',
        'mkdocs-audiotag>=0.0.1',
        'beautifulsoup4>=4.13.4'
    ],
    include_package_data=True,
    python_requires='>=3.7',
    entry_points={
        'mkdocs.plugins': [
            'mkdocs-wavesurfer = mkdocs_wavesurfer.plugin:Wave'
        ]
    }
)