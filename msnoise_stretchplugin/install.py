from msnoise.api import *

from .default_table_def import DefaultStations
from .default import default

def main():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    DefaultStations.__table__.create(bind=engine, checkfirst=True)
    for name in default.keys():
        forcing = default[name][1]
        folder_name = default[name][2]
        default_station = default[name][3]
        unit = default[name][4]
        session.add(DefaultStations(name=name,forcing=forcing,
                                    folder_name=folder_name,
                                    default_station=default_station, unit=unit))

    session.commit()
