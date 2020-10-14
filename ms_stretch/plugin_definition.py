import click
from flask_admin.contrib.sqla import ModelView
from .default_table_def import DefaultStations


@click.group()
def plot():
    """Sets up the plotting scripts for the stretching method plugin"""
    pass


@click.command()
@click.option('-m', '--mov_stack', default=10, help='Plot specific mov stacks')
@click.option('-c', '--components', default="ZZ", help='Components (ZZ, ZR,...)')
@click.option('-f', '--filterid', default='1', help='Filter ID', multiple=True)
@click.option('-p', '--pairs', default=None, help='Plot (a) specific pair(s)',
              multiple=True)
@click.option('-F', '--forcing', default='prec', help='Choose forcing to \
              display')
@click.option('-a', '--ask', default=False, help='Ask which station to use \
              for plotting natural forcings. Else default station is used.')
@click.option('-s', '--show', help='Show interactively?',
              default=True, type=bool)
@click.option('-o', '--outfile', help='Output filename (?=auto)',
              default=None, type=str)
def forcing(mov_stack, components, filterid, pairs, forcing, ask, show, outfile):
    """Plot velocity curves obtained by the stretching method with
    forcings defined in the arguments and configurations."""

    from .dvv_scripts.dvv_forc import main
    main(mov_stack, components, filterid, pairs, forcing, ask, show, outfile)


@click.command()
@click.option('-m', '--mov_stack', default=10, help='Plot specific mov stacks')
@click.option('-c', '--components', default="ZZ", help='Components (ZZ, ZR,...)')
@click.option('-f', '--filterid', default='1', help='Filter ID', multiple=True)
@click.option('-p', '--pairs', default=None, help='Plot (a) specific pair(s)',
              multiple=True)
@click.option('-F', '--forcings', default=['prec'], help='Choose forcings to '
              'display.', multiple=True)
@click.option('-a', '--ask', default=False, help='Ask which station to use \
              for plotting natural forcings. Else default station is used.')
@click.option('-s', '--show', help='Show interactively?',
              default=True, type=bool)
@click.option('-o', '--outfile', help='Output filename (?=auto)',
              default=None, type=str)
def mforcing(mov_stack, components, filterid, pairs, forcings, ask,
             show, outfile):
    """Plot velocity curves obtained by the stretching method with multiple
    forcings defined in the arguments and configurations."""

    from .dvv_scripts.dvv_mforc import main
    main(mov_stack, components, filterid, pairs, forcings, ask, show, outfile)


@click.command()
@click.option('-m', '--mov_stack', default=0, help='Plot specific mov stacks')
@click.option('-c', '--components', default="ZZ", help='Components (ZZ, ZR,...)')
@click.option('-f', '--filterid', default='1', help='Filter ID', multiple=True)
@click.option('-p', '--pairs', default=None, help='Plot (a) specific pair(s)',
              multiple=True)
@click.option('-s', '--show', help='Show interactively?',
              default=True, type=bool)
@click.option('-o', '--outfile', help='Output filename (?=auto)',
              default=None, type=str)
def dvv(mov_stack, components, filterid, pairs, show, outfile):
    """Plot velocity curves obtained by the stretching method in
    the standard msnoise way. Multiple filters are possible."""

    from .dvv_scripts.dvv_mov import main
    main(mov_stack, components, filterid, pairs, show, outfile)


@click.command()
@click.option('-m', '--mov_stack', default=0, help='Plot specific mov stacks')
@click.option('-c', '--components', default="ZZ", help='Components (ZZ, ZR,...)')
@click.option('-f', '--filterid', default='1', help='Filter ID')
@click.option('-p', '--pairs', default=None, help='Plot (a) specific pair(s)',
              multiple=True)
@click.option('-s', '--show', help='Show interactively?',
              default=True, type=bool)
@click.option('-o', '--outfile', help='Output filename (?=auto)',
              default=None, type=str)
def corr(mov_stack, components, filterid, pairs, show, outfile):
    """Plot velocity curves obtained by the stretching method with
    their respective correlation coefficients in a subplot."""

    from .dvv_scripts.dvv_corr import main
    main(mov_stack, components, filterid, pairs, show, outfile)


@click.command()
def install():
    """ Create the Config table"""
    from .install import main
    main()


@click.command()
def uninstall():
    """ Create the Config table"""
    from .uninstall import main
    main()


plot.add_command(forcing)
plot.add_command(mforcing)
plot.add_command(dvv)
plot.add_command(corr)
plot.add_command(install)
plot.add_command(uninstall)




####################### Class Definitions ##########################

class DefaultStationsView(ModelView):
    # Disable model creation
    view_title = "MSNoise Default Stations Configuration"
    name = "Configuration"

    can_create = True
    can_delete = True
    page_size = 50
    # Override displayed fields
    column_list = ('forcing', 'short_name', 'folder_name',
                   'default_station', 'unit', 'plot_type')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(DefaultStationsView, self).__init__(DefaultStations, session,
                                                  endpoint="defaultstations",
                                                  name="Default Stations",
                                                  category="Configuration",
                                                  **kwargs)
