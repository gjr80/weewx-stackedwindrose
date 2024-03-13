"""
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

Installer for StackedWindRose Image Generator Extension

Version: 3.1.0                                      Date: 14 March 2024

Revision History
    14 March 2024
        -   removed distutils.StrictVersion dependency
        -   now uses weecfg.extension.ExtensionInstaller
        -   now uses a multi-line string and StringIO to obtain the extension
            installer config dict
    6 July 2023         v3.0.2
        -   version change only
    7 June 2020         v3.0.1
        -   version change only
    5 June 2020         v3.0.0
        -   minor tweaks/optimisation
        -   changed generator python file name
        -   changed 'period' to 'time_length'
        -   renamed ImageStackedWindRoseGenerator stanza to
            StackedWindRoseImageGenerator
        -   revised comments formatting
    9 October 2018      v2.1.1
        -   version change only
    13 March 2017       v2.1.0
        -   fixed error resulting from change to class
            reportengine.ReportGenerator signature introduced in WeeWX 3.7.0
        -   added weeWX version check to installer
        -   revised imageStackedWindRose.py comments
    15 August 2016      v2.0.2
        -   Reworked imports to use PIL if available
        -   Updated readme/readme.txt
    9 August 2016       v2.0.1
        -   Fixed typo in install instructions
    8 August 2016       v2.0.0
        -   Initial implementation
"""

# python imports
import configobj
from weecfg.extension import ExtensionInstaller

# import StringIO, use six.moves due to python2/python3 differences
from six.moves import StringIO

# WeeWX imports
import weewx

# note do not use release candidates, eg 5.0.0rc3
REQUIRED_WEEWX_VERSION = "3.2.0"
STACKEDWINDROSE_VERSION = "3.1.0"

# define our config as a multiline string so we can preserve comments
stacked_config = """
[StdReport]
    [[StackedWindRose]]
        skin = StackedWindRose
        [[[Units]]]
            [[[[Groups]]]]
                group_speed = km_per_hour
            [[[[Labels]]]]
                km_per_hour = km/h
                knot = knots
                meter_per_second = m/s
                mile_per_hour = mph
        [[[Labels]]]
            compass_points = N, S, E, W
            [[[[Generic]]]]
                windGust = Gust Speed
                windSpeed = Wind Speed
        [[[StackedWindRoseImageGenerator]]]
            image_background_image = None
            image_width = 382
            image_height = 361
            image_background_circle_color = 0xF5F5F5
            image_background_box_color = 0xF5C696
            image_background_range_ring_color = 0xC3D9DD
            windrose_plot_border = 5
            windrose_legend_bar_width = 10
            windrose_font_path = /usr/share/fonts/truetype/freefont/FreeSansBold.ttf
            windrose_plot_font_size = 10
            windrose_plot_font_color = 0x000000
            windrose_legend_font_size = 10
            windrose_legend_font_color = 0x000000
            windrose_label_font_size = 12
            windrose_label_font_color = 0x000000
            windrose_plot_petal_colors = aqua, 0xFF9900, 0xFF3300, 0x009900, 0x00CC00, 0x33FF33, 0x00FFCC
            windrose_plot_petal_width = 16
            [[[[day_images]]]]
                time_length = 86400
                [[[[[daywindrose]]]]]
                    format = png
                    [[[[[[windSpeed]]]]]]
                        label = 24 Hour Wind Rose
                        time_stamp = %H:%M %-d %b %y
                        time_stamp_location = bottom, right
"""

# construct our config dict
stacked_dict = configobj.ConfigObj(StringIO(stacked_config))

def version_compare(v1, v2):
    """Basic 'distutils' and 'packaging' free version comparison.

    v1 and v2 are WeeWX version numbers in string format.

    Returns:
        0 if v1 and v2 are the same
        -1 if v1 is less than v2
        +1 if v1 is greater than v2
    """

    import itertools
    mash = itertools.zip_longest(v1.split('.'), v2.split('.'), fillvalue='0')
    for x1, x2 in mash:
        try:
            y1, y2 = int(x1), int(x2)
        except ValueError:
            y1, y2 = x1, x2
        if y1 > y2:
            return 1
        if y1 < y2:
            return -1
    return 0

def loader():
    return StackedWindRoseInstaller()

class StackedWindRoseInstaller(ExtensionInstaller):
    def __init__(self):
        if version_compare(weewx.__version__, REQUIRED_WEEWX_VERSION) < 0:
            msg = "%s requires WeeWX %s or greater, found %s" % (' '.join(('StackedWindRose', STACKEDWINDROSE_VERSION)),
                                                                 REQUIRED_WEEWX_VERSION,
                                                                 weewx.__version__)
            raise weewx.UnsupportedFeature(msg)
        super(StackedWindRoseInstaller, self).__init__(
            version=STACKEDWINDROSE_VERSION,
            name='StackedWindRose',
            description='Stacked windrose image generator for WeeWX.',
            author="Gary Roderick",
            author_email="gjroderick@gmail.com",
            files=[('bin/user', ['bin/user/stackedwindrose.py']),
                   ('skins/StackedWindRose', ['skins/StackedWindRose/skin.conf'])],
            config=stacked_dict
        )
