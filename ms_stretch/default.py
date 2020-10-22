from collections import OrderedDict
default = OrderedDict()


default['prec'] = ["Enter the default station or 'all'.", 'Precipitation',
                   'precipitation', 'Daguan', 'mm', 'bars']
default['press'] = ["Enter the default station or 'all'.", 'Pressure',
                    'pressure', 'all', 'kPa', 'points']
default['temp'] = ["Enter the default station or 'all'.", 'Temperature',
                   'temperature', 'all', '°C', 'points']
default['ndvi'] = ["Enter the default station or 'all'.", 'NDVI',
                   'ndvi', 'landmask', '', 'errorbars']
default['depth'] = ["Enter the default station or 'all'.", 'Sensor Depth',
                    'sensor_depth', 'TWL8', 'm', 'points']
