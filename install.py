#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# Installer for StackedWindRose Image Generator Extension
#
# Version: 2.0.2                                      Date: 15 August 2016
#
# Revision History
#  15 August 2016   v2.0.2
#       -   Reworked imports to use PIL if available
#       -   Updated readme/readme.txt
#   9 August 2016   v2.0.1
#       -   Fixed typo in install instructions
#   8 August 2016   v2.0.0  
#       -   Initial implementation
#

from setup import ExtensionInstaller

def loader():
    return StackedWindRoseInstaller()

class StackedWindRoseInstaller(ExtensionInstaller):
    def __init__(self):
        super(StackedWindRoseInstaller, self).__init__(
            version="2.0.2",
            name='StackedWindRose',
            description='Stacked windrose image generator for weewx.',
            author="Gary Roderick",
            author_email="gjroderick@gmail.com",
            config={
                'StdReport': {
                    'StackedWindRose': {
                        'skin': 'StackedWindRose',
                        'Units': {
                            'Groups': {
                                'group_speed': 'km_per_hour'
                            },
                            'Labels': {
                                'km_per_hour': 'km/h',
                                'knot': 'knots',
                                'meter_per_second': 'm/s',
                                'mile_per_hour': 'mph'
                            },
                        },
                        'Labels': {
                            'compass_points': ['N', 'S', 'E', 'W'],
                            'Generic': {
                                'windGust': 'Gust Speed',
                                'windSpeed': 'Wind Speed'
                            }
                        },
                        'ImageStackedWindRoseGenerator': {
                            'image_background_image': 'None',
                            'image_width': '382',
                            'image_height': '361',
                            'image_background_circle_color': '0xF5F5F5',
                            'image_background_box_color': '0xF5C696',
                            'image_background_range_ring_color': '0xC3D9DD',
                            'windrose_plot_border': '5',
                            'windrose_legend_bar_width': '10',
                            'windrose_font_path': '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
                            'windrose_plot_font_size': '10',
                            'windrose_plot_font_color': '0x000000',
                            'windrose_legend_font_size': '10',
                            'windrose_legend_font_color': '0x000000',
                            'windrose_label_font_size': '12',
                            'windrose_label_font_color': '0x000000',
                            'windrose_plot_petal_colors': ['aqua', '0xFF9900', '0xFF3300', '0x009900', '0x00CC00', '0x33FF33', '0x00FFCC'],
                            'windrose_plot_petal_width': '16',
                            'day_images': {
                                'period': '86400',
                                'daywindrose': {
                                    'format': 'png',
                                    'windSpeed': {
                                        'label': '24 Hour Wind Rose',
                                        'time_stamp': '%H:%M %-d %b %y',
                                        'time_stamp_location': ['bottom', 'right']
                                    }
                                }
                            }
                        }
                    }
                }
            },
            files=[
                ('bin/user', ['bin/user/imageStackedWindRose.py']),
                ('skins/StackedWindRose', ['skins/StackedWindRose/skin.conf'])
            ]
        )
