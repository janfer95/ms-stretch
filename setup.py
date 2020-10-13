from setuptools import setup, find_packages

setup(
    name='msnoise_stretchingplots',
    version='0.1a',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['msnoise',
                      'obspy'],
    entry_points = {
        'msnoise.plugins.table_def': [
            'DefaultStations = msnoise_stretchplugin.default_table_def:DefaultStations',
            ],
        'msnoise.plugins.admin_view': [
            'DefaultStationsView = msnoise_stretchplugin.plugin_definition:DefaultStationsView',
            ],
        'msnoise.plugins.commands': [
            'plot = msnoise_stretchplugin.plugin_definition:plot',
            ],
        },
    author = "Jannik Kühn",
    author_email = "jannik.kuehn@outlook.de",
    description = "An msnoise plugin to plot dvv curves using the \
                   stretching method",
    license = "EUPL-1.1",
    url = "http://www.msnoise.org", # TODO: Add github?
    keywords="ambient seismic noise stretching"
)
