import scripts
if __name__ == "__main__":
    import setuptools
    setuptools.setup(
        name='django_pip_example',
        version='0.9.9.1',
        packages=['backend', 'scripts'],
        description='descr',
        install_requires=[ 'Django' ],
        entry_points =
        { 'console_scripts':
            [
                'prodgraph_run = scripts.run:main',
                'prodgraph_init = scripts.init:main',
            ]
        },
    )
