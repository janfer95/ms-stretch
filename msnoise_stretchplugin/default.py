from collections import OrderedDict
default = OrderedDict()


default['prec'] = ["Enter the default station or 'all'.", 'Precipitation',
                   'precipitation', 'Daguan', 'mm']
default['press'] = ["Enter the default station or 'all'.", 'Pressure',
                    'pressure', 'all', 'kPa']
default['temp'] = ["Enter the default station or 'all'.", 'Temperature',
                   'temperature', 'all', '°C']
default['ndvi'] = ["Enter the default station or 'all'.", 'NDVI',
                   'ndvi', 'landmask', 'all', '']
default['depth'] = ["Enter the default station or 'all'.", 'Sensor Depth',
                    'sensor_depth', 'TWL8', 'm']
default['pgv'] = ["Enter the default station or 'all'.", 'Peak-Ground-Velocity',
                  'pgv', 'all', 'm/s']
