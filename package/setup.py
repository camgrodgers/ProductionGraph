import scripts
if __name__ == "__main__":
    import setuptools
    setuptools.setup(
        name='productiongraph',
        version='0.1.3',
        author='Cameron, Aaron, Osiris, Benjamin, Matt',
        author_email='cameron.g.rodgers@gmail.com',
        packages=setuptools.find_packages(),
        description='Web interface for calculating prices',
        install_requires=[ 'Django', 'product_graph_bindings' ],
        entry_points =
        { 'console_scripts':
            [
                'prodgraph_run = scripts.run:main',
                'prodgraph_init = scripts.init:main',
            ]
        },
    )
