import scripts
if __name__ == "__main__":
    import setuptools
    setuptools.setup(
        name='productiongraph',
        version='0.1.6',
        author='Cameron, Aaron, Osiris, Benjamin, Matt',
        author_email='cameron.g.rodgers@gmail.com',
        packages=setuptools.find_packages(),
        #include_package_data=True,
        package_data={
            "": ["*.html", "*.css"],
            "productiongraph": ["*.html", "*.css"],
            "backend": ["*.html", "*.css"],
        },
        description='Web interface for calculating prices',
        install_requires=[ 'Django', 'product_graph_bindings' ],
        entry_points =
        { 'console_scripts':
            [
                'prodgraph_run = scripts.run:main',
                'prodgraph_init = scripts.init:main',
                'prodgraph_test = scripts.test:main',
            ]
        },
    )
