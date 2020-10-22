import click
import time

from flask_admin.contrib.sqla import ModelView
from .default_table_def import DefaultStations


@click.group()
def stretch():
    """Sets up the plotting scripts for the stretching method plugin"""
    pass


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
@click.option('-C', '--custom', default=False, help='Customize pair names.')
@click.option('-F', '--forcing', default=None, help='Choose forcing to'
              ' display')
@click.option('-a', '--ask', default=False, help='Ask which station to use '
              'for plotting natural forcings. Else default station is used.')
@click.option('-s', '--show', help='Show interactively?',
              default=True, type=bool)
@click.option('-o', '--outfile', help='Output filename (?=auto)',
              default=None, type=str)
def forcing(mov_stack, components, filterid, pairs, custom, forcing, ask,
            show, outfile):
    """ Plot dvv curves with a forcing as subplot.

    Plot dvv velocity curves obtained by the stretching method with
    forcings defined in the arguments and configurations."""

    from .dvv_scripts.dvv_forc import main
    main(mov_stack, components, filterid, pairs, custom, forcing,
         ask, show, outfile)


@click.command()
@click.option('-m', '--mov_stack', default=10, help='Plot specific mov stacks')
@click.option('-c', '--components', default="ZZ", help='Components (ZZ, ZR,...)')
@click.option('-f', '--filterid', default='1', help='Filter ID', multiple=True)
@click.option('-p', '--pairs', default=None, help='Plot (a) specific pair(s)',
              multiple=True)
@click.option('-C', '--custom', default=False, help='Customize pair names.')
@click.option('-F', '--forcings', default=[], help='Choose forcings to '
              'display.', multiple=True)
@click.option('-a', '--ask', default=False, help='Ask which station to use \
              for plotting natural forcings. Else default station is used.')
@click.option('-s', '--show', help='Show interactively?',
              default=True, type=bool)
@click.option('-o', '--outfile', help='Output filename (?=auto)',
              default=None, type=str)
def mforcing(mov_stack, components, filterid, pairs, custom, forcings, ask,
             show, outfile):
    """Plot dvv curves with up to 3 forcings.

    Plot dvv velocity curves obtained by the stretching method with multiple
    forcings defined in the arguments and configurations. The first
    forcing is plotted together with the dvv curve. The two other ones
    are displayed in a subplot."""

    from .dvv_scripts.dvv_mforc import main
    main(mov_stack, components, filterid, pairs, custom, forcings,
         ask, show, outfile)


@click.command()
@click.option('-m', '--mov_stack', default=0, help='Plot specific mov stacks')
@click.option('-c', '--components', default="ZZ", help='Components (ZZ, ZR,...)')
@click.option('-f', '--filterid', default='1', help='Filter ID', multiple=True)
@click.option('-p', '--pairs', default=None, help='Plot (a) specific pair(s)',
              multiple=True)
@click.option('-C', '--custom', default=False, help='Customize pair names.')
@click.option('-s', '--show', help='Show interactively?',
              default=True, type=bool)
@click.option('-o', '--outfile', help='Output filename (?=auto)',
              default=None, type=str)
def dvv(mov_stack, components, filterid, pairs, custom, show, outfile):
    """Plot dvv curves in standard msnoise format.

    Plot velocity curves obtained by the stretching method in
    the standard msnoise way. Multiple filters are possible."""

    from .dvv_scripts.dvv_mov import main
    main(mov_stack, components, filterid, pairs, custom, show, outfile)


@click.command()
@click.option('-m', '--mov_stack', default=10, help='Plot specific mov stacks')
@click.option('-c', '--components', default="ZZ", help='Components (ZZ, ZR,...)')
@click.option('-f', '--filterid', default='1', help='Filter ID')
@click.option('-p', '--pairs', default=None, help='Plot (a) specific pair(s)',
              multiple=True)
@click.option('-C', '--custom', default=False, help='Customize pair names.')
@click.option('-s', '--show', help='Show interactively?',
              default=True, type=bool)
@click.option('-o', '--outfile', help='Output filename (?=auto)',
              default=None, type=str)
def corr(mov_stack, components, filterid, pairs, custom, show, outfile):
    """Plot dvv curves with correlation coefficients.

    Plot velocity curves obtained by the stretching method with
    their respective correlation coefficients in a subplot."""

    from .dvv_scripts.dvv_corr import main
    main(mov_stack, components, filterid, pairs, custom, show, outfile)


@click.command()
def install():
    """Install the default stations table in admin page.

    Create a table in the database called Default Stations
    that is used for the forcing commands. Database table
    can be dropped with the uninstall command."""
    from .install import main
    main()


@click.command()
def uninstall():
    """Drop default stations table in database.

    Deletes Default Stations entry in the current database. Normally
    the entry should also disappear in the admin viewer."""
    from .uninstall import main
    main()

@click.group()
def compute():
    """Group of commands to compute certain data"""
    pass


@click.command()
@click.option('-t', '--threads', default=1, help='Number of threads to use \
(only affects modules that are designed to do parallel processing)')
@click.option('-d', '--delay', default=1,  help='In the case of multi-threading'
                    ', defines the number of seconds to wait before lauching '
                    'the next thread. Defaults to [1] second ')
@click.pass_context
def stretching(ctx, threads, delay):
    """Computes the stretching based on the new stacked data"""
    from .stretch import main
    loglevel = ctx.obj['MSNOISE_verbosity']
    if threads == 1:
        main()
    else:
        from multiprocessing import Process
        processes = []
        for i in range(threads):
            p = Process(target=main)
            p.start()
            processes.append(p)
            time.sleep(delay)
        for p in processes:
            p.join()


stretch.add_command(plot)
plot.add_command(forcing)
plot.add_command(mforcing)
plot.add_command(dvv)
plot.add_command(corr)
plot.add_command(install)
plot.add_command(uninstall)

stretch.add_command(compute)
compute.add_command(stretching)




####################### Class Definitions ##########################

class DefaultStationsView(ModelView):
    # Disable model creation
    view_title = "MSNoise Default Stations Configuration"
    name = "Configuration"

    can_create = True
    can_delete = True
    page_size = 50
    # Override displayed fields
    column_list = ('ref', 'short_name', 'forcing', 'folder_name',
                   'default_station', 'unit', 'plot_type')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(DefaultStationsView, self).__init__(DefaultStations, session,
                                                  endpoint="defaultstations",
                                                  name="Default Stations",
                                                  category="Stretch",
                                                  **kwargs)
