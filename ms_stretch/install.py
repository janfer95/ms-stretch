"""Install the default stations table in admin page.

Create a table in the database called Default Stations
that is used for the forcing commands. Database table
can be dropped with the uninstall command."""

from msnoise.api import *

from .default_table_def import DefaultStations
from .default import default

def main():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        DefaultStations.__table__.create(bind=engine, checkfirst=True)
    except:
        print("Table seems to already exist")

    for short_name in default.keys():
        forcing = default[short_name][1]
        folder_name = default[short_name][2]
        default_station = default[short_name][3]
        unit = default[short_name][4]
        plot_type = default[short_name][5]
        session.add(DefaultStations(short_name=short_name,forcing=forcing,
                                    folder_name=folder_name,
                                    default_station=default_station,
                                    unit=unit, plot_type=plot_type))

    session.commit()
