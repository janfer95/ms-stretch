"""Drop default stations table in database.

Deletes Default Stations entry in the current database. Normally
the entry should also disappear in the admin viewer."""

from msnoise.api import *

from .default_table_def import DefaultStations

def main():
    # TODO: Test if Session is actually needed
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    DefaultStations.__table__.drop(engine)
