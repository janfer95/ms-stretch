import click
from flask_admin.contrib.sqla import ModelView
from .default_table_def import DefaultStations


class DefaultStationsView(ModelView):
    # Disable model creation
    view_title = "MSNoise Default Stations Configuration"
    name = "Configuration"

    can_create = True
    can_delete = True
    page_size = 50
    # Override displayed fields
    column_list = ('forcing', 'short_name', 'folder_name',
                   'default_station', 'unit')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(DefaultStationsView, self).__init__(DefaultStations, session,
                                                endpoint="defaultstations",
                                                name="Default Stations",
                                                category="Configuration", **kwargs)

@click.group()
def plot():
    """Sets up the plotting scripts for the stretching method plugin"""
    pass

@click.command()
def forcing():
    """Plot velocity curves obtained by the stretching method with
    forcings defined in the arguments and configurations."""
    print("For now I just say hi")

plot.add_command(forcing)

@click.command()
def install():
    """ Create the Config table"""
    from .install import main
    main()

plot.add_command(install)
