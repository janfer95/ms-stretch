# Table definitions for default forcing stations
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DefaultStations(Base):
    """
    Config Object

    :type ref: int
    :param ref: The reference ID of the forcing.

    :type forcing: str
    :param forcing: The forcing to be plotted.

    :type name: str
    :param name: A short version of the forcing name.

    :type folder_name: str
    :param folder_name: The name of the folder where the forcing data is stored.

    :type default_station: str
    :param default_station: The station that is plotted by default. Can be all.

    :type unit: str
    :param unit: The unit of the forcing plotted. Used for y label.

    :type plot_type: str
    :param plot_type: Which type of plotting to use. Can be points, bars,
                      cumsum bars, or errorbars.
    """
    __tablename__ = "default-stations"
    ref = Column(Integer, primary_key=True)
    short_name = Column(String(255))
    forcing = Column(String(255))
    folder_name = Column(String(255))
    default_station = Column(String(255))
    unit = Column(String(255))
    plot_type = Column(String(255))

    def __init__(self, short_name, forcing, folder_name, default_station,
                 unit, plot_type):
        """"""
        self.short_name = short_name
        self.forcing = forcing
        self.folder_name = folder_name
        self.default_station = default_station
        self.unit = unit
        self.plot_type = plot_type
