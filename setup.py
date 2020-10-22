from setuptools import setup, find_packages

setup(
    name='ms_stretch',
    version='0.1a',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['msnoise',
                      'obspy'],
    entry_points = {
        'msnoise.plugins.table_def': [
            'DefaultStations = ms_stretch.default_table_def:DefaultStations',
            ],
        'msnoise.plugins.admin_view': [
            'DefaultStationsView = ms_stretch.plugin_definition:DefaultStationsView',
            ],
        'msnoise.plugins.commands': [
            'stretch = ms_stretch.plugin_definition:stretch',
            ],
        },
    author = "Jannik Kühn",
    author_email = "jannik.kuehn@outlook.de",
    description = "An msnoise plugin to plot dvv curves using the \
                   stretching method",
    license = "EUPL-1.1",
    url = "https://github.com/janfer95/ms_stretch",
    keywords="ambient seismic noise stretching"
)
