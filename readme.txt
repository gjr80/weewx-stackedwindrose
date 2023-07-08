The Stacked Windrose Image Generator extension generates a polar wind plot
commonly known as a windrose that shows the distribution of wind speed and
direction over a period of time. The Stacked Windrose Image Generator extension
consists of a single skin controlling a custom image generator that produces
a the windrose image based upon WeeWX archive data.

Pre-Requisites

WeeWX v3.2.0 or greater.

File Locations

As WeeWX file locations vary by system and installation method, the following
symbolic names, as per the WeeWX User's Guide - Installing WeeWX, are used in
these instructions:

- $BIN_ROOT (Executables)
- $SKIN_ROOT (Skins and templates)
- $HTML_ROOT (Web pages and images)

Where applicable the nominal location for your system and installation type
should be used in place of the symbolic name

Installation Instructions

1.  Download the Stacked Windrose Image Generator extension from the
Release (https://github.com/gjr80/weewx-stackedwindrose/releases) page. The
current release package is named stackedwindrose-3.0.2.tar.gz. If your WeeWX PC
has internet access you may be able to download the package directly as
follows:

    $ wget -P /var/tmp/ https://github.com/gjr80/weewx-stackedwindrose/releases/download/v3.0.1/stackedwindrose-3.0.2.tar.gz

2.  Run the installer:

    $ ./wee_extension --install=/var/tmp/stackedwindrose-3.0.2.tar.gz

    This command assumes the user is currently in the $BIN_ROOT folder. If this
    is not the case you may need to include the path to wee_extension.

3.  Various attributes of the generated plot can be controlled through a number
of settings in the [StdReport] [[StackedWindRose]] section in weewx.conf. This
approach has the advantage of retaining user settings across upgrades of this
extension but any change to these parameters will require a WeeWX configuration
reload or a WeeWX restart. The extension installer does not permit comments
to be included in weewx.conf so the windrose plot parameters and explanatory
notes are included below. Commonly changed options include the units of
measure (group_speed parameter) and date-time format (time_stamp parameter).
Edit any parameters as required:

    [[StackedWindRose]]
        skin = StackedWindRose

        [[[Units]]]

            [[[[Groups]]]]

                # group_speed sets the display units for the windrose plots
                group_speed = km_per_hour   # Options are 'mile_per_hour',
                                            # 'km_per_hour', 'knot', or
                                            # 'meter_per_second'

            [[[[Labels]]]]
                # This section sets a label to be used for each type of unit.

                km_per_hour       = "km/h"
                knot              = "knots"
                meter_per_second  = "m/s"
                mile_per_hour     = "mph"

        [[[Labels]]]

            # Set to compass point abbreviations suitable for your location.
            # Must be in the order of North, South, East, West.
            compass_points = N, S, E, W

            [[[[Generic]]]]
                # This section sets the labels to be used when displaying
                # either windGust or windSpeed
                windGust  = Gust Speed
                windSpeed = Wind Speed

        [[[ImageStackedWindRoseGenerator]]]

            # This section contains the options for the Stacked Wind Rose image
            # generator. A number of plotting options can be set such as
            # colour, fonts, sizes etc. Some options have default values if
            # the option or value is omitted, these defaults are specified
            # where applicable.
            #
            # Fonts can be anything accepted by the Python Imaging Library
            # (PIL), which is currently truetype (.ttf), or PIL's own font
            # format (.pil). See
            # http://www.pythonware.com/library/pil/handbook/imagefont.htm for
            # more details.  Note that "font size" is only used with truetype
            # (.ttf) fonts. For others, font size is determined by the
            # bit-mapped size, usually encoded in the file name (eg courB010.pil).
            #
            # Colors can be specified any of three ways:
            #   1. Notation 0xBBGGRR;
            #   2. Notation #RRGGBB; or
            #   3. Using an English name, such as 'yellow', or 'blue'.
            # So, 0xff0000, #0000ff, or 'blue' would all specify a pure blue
            # colour.

            # Image file to be used to used as the background for the plot. If
            # it does not exist or is set to none/None the background will be
            # image_height x image_width pixels with colour set to
            # image_background_box_color. eg
            #   image_background_image = windrose_bground.png
            # woudld use the file windrose_bground.png as the background image.
            image_background_image = none

            # Overall width and height of image
            image_width = 382
            image_height = 361
            # Fill colour of plot circles
            image_background_circle_color = 0xF5F5F5
            # Colour of background box
            image_background_box_color = 0xF5C696
            # Colour of range rings on plot
            image_background_range_ring_color = 0xC3D9DD

            # Minimum distance (in pixels) from edge of image to plot/legend
            windrose_plot_border = 5
            # Width of legend stacked bar (in pixels)
            windrose_legend_bar_width = 10

            # Font to be used
            windrose_font_path = /usr/share/fonts/truetype/freefont/FreeSansBold.ttf
            # Font setting for N,E,S,W, bullseye % and % rings
            windrose_plot_font_size  = 10
            windrose_plot_font_color = 0x000000
            # Font setting for plot legend
            windrose_legend_font_size = 10
            windrose_legend_font_color = 0x000000
            # Font setting for plot label/title
            windrose_label_font_size = 12
            windrose_label_font_color = 0x000000

            # Comma separated list of colours used for stacked 'petals' on
            # windrose.
            # First colour is for Calm/0 speed, 2nd for 1st band, 2nd for
            # 3rd band etc. Defaults to 'lightblue', 'blue', 'midnightblue',
            # 'forestgreen', 'limegreen', 'green', 'greenyellow'
            # Only 7 colours will be used irrespective of how many are listed.
            windrose_plot_petal_colors = aqua, 0xFF9900, 0xFF3300, 0x009900, 0x00CC00, 0x33FF33, 0x00FFCC
            # Width of petals in degrees. If not set default is 16 degrees
            windrose_plot_petal_width = 16

            [[[[day_images]]]]
                # Period (in seconds) over which wind rose is constructed.
                # 86400 will use wind samples from past 24 hours, 43200 uses
                # 12 hours of samples etc
                time_length = 86400 # == 24 hours

                [[[[[daywindrose]]]]]
                    # Image filename will be [[[]]] setting on line above with
                    # extension as per format setting below. [[[daywindrose]]]
                    # using png format will result in file being named
                    # daywindrose.png

                    # File format of resulting image file. Use any file
                    # extension for image formats that PIL can write
                    # (eg png, gif etc). Defaults to png if omitted.
                    format = png

                    # To use windGust data for wind rose set [[[[windGust]]]]
                    # on next line, to use windSpeed set next line to
                    # [[[[windSpeed]]]]
                    [[[[[[windGust]]]]]]
                        # Label/title for  plot
                        label = 24 Hour Wind Rose

                        # Format of optional time stamp to be placed on image.
                        # Format codes as per Python datetime format caodes at
                        # https://docs.python.org/3/library/datetime.html

                        time_stamp = %H:%M %d %b %y

                        # Location of optional time stamp on image. If omitted
                        # no time stamp is included. Format for setting is
                        # vertical_position, horizontal_position where
                        # vertical_position is one of top or bottom;
                        # horizontal_position is one of left, center, right.
                        # Default setting (if option is present) is
                        # bottom, right

                        time_stamp_location = bottom, right

4.  By default the Stacked Windrose Image Generator generator places the
generated file in the $HTML_ROOT directory. If you wish to place the generated
files in another directory then insert a 'HTML_ROOT' setting giving the
applicable directory under the [[StackedWindRose]] sub-section in the
[StdReport] section of weewx.conf, eg:

    [[StackedWindRose]]
        skin = StackedWindRose
        HTML_ROOT = /use/this/directory

5. Restart WeeWX:

    $ sudo /etc/init.d/weewx restart

	or

    $ sudo service weewx restart

    or

    $ sudo systemctl restart weewx

6.  This will result in the windrose image file being generated during each
report generation cycle. Generation can be confirmed by inspecting the WeeWX
log, there should be a line similar to this amongst the report generation
output:

    Jun  6 09:26:16 buster30 weewx[1476] INFO user.stackedwindrose: Generated 1
            images for StackedWindRose in 0.02 seconds

Manual Installation Instructions

1.  Download the Stacked Windrose Image Generator extension from the
Release (https://github.com/gjr80/weewx-stackedwindrose/releases) page. The
current release package is named stackedwindrose-3.0.2.tar.gz. If your WeeWX PC
has internet access you may be able to download the package directly as
follows:

    $ wget -P /var/tmp/ https://github.com/gjr80/weewx-stackedwindrose/releases/download/v3.0.1/stackedwindrose-3.0.2.tar.gz

2.  Extract the files from the tar.gz file:

    $ tar -zxvf /var/tmp/stackedwindrose-3.0.2.tar.gz -C /var/tmp

3.  Copy files as follows:

    $ cp /var/tmp/stackedwindrose/bin/user/stackedwindrose.py $BIN_ROOT/user
    $ cp -R var/tmp/stackedwindrose/skins/* $SKIN_ROOT

4.  In weewx.conf, modify the [StdReport] section by adding the following
sub-section:

    [[StackedWindRose]]
        skin = StackedWindRose

5.  Various attributes of the generated plot can be controlled through a number
of settings in the [StdReport] [[StackedWindRose]] section in weewx.conf. This
approach has the advantage of retaining user settings across upgrades of this
extension but any change to these parameters will require a WeeWX configuration
reload or a WeeWX restart. The extension installer does not permit comments
to be included in weewx.conf so the windrose plot parameters and explanatory
notes are included below. Commonly changed options include the units of
measure (group_speed parameter) and date-time format (time_stamp parameter).
Edit any parameters as required:

    [[StackedWindRose]]
        skin = StackedWindRose

        [[[Units]]]

            [[[[Groups]]]]

                # group_speed sets the display units for the windrose plots
                group_speed = km_per_hour   # Options are 'mile_per_hour',
                                            # 'km_per_hour', 'knot', or
                                            # 'meter_per_second'

            [[[[Labels]]]]
                # This section sets a label to be used for each type of unit.

                km_per_hour       = "km/h"
                knot              = "knots"
                meter_per_second  = "m/s"
                mile_per_hour     = "mph"

        [[[Labels]]]

            # Set to compass point abbreviations suitable for your location.
            # Must be in the order of North, South, East, West.
            compass_points = N, S, E, W

            [[[[Generic]]]]
                # This section sets the labels to be used when displaying
                # either windGust or windSpeed
                windGust  = Gust Speed
                windSpeed = Wind Speed

        [[[ImageStackedWindRoseGenerator]]]

            # This section contains the options for the Stacked Wind Rose image
            # generator. A number of plotting options can be set such as
            # colour, fonts, sizes etc. Some options have default values if
            # the option or value is omitted, these defaults are specified
            # where applicable.
            #
            # Fonts can be anything accepted by the Python Imaging Library
            # (PIL), which is currently truetype (.ttf), or PIL's own font
            # format (.pil). See
            # http://www.pythonware.com/library/pil/handbook/imagefont.htm for
            # more details.  Note that "font size" is only used with truetype
            # (.ttf) fonts. For others, font size is determined by the
            # bit-mapped size, usually encoded in the file name (eg courB010.pil).
            #
            # Colors can be specified any of three ways:
            #   1. Notation 0xBBGGRR;
            #   2. Notation #RRGGBB; or
            #   3. Using an English name, such as 'yellow', or 'blue'.
            # So, 0xff0000, #0000ff, or 'blue' would all specify a pure blue
            # colour.

            # Image file to be used to used as the background for the plot. If
            # it does not exist or is set to none/None the background will be
            # image_height x image_width pixels with colour set to
            # image_background_box_color. eg
            #   image_background_image = windrose_bground.png
            # woudld use the file windrose_bground.png as the background image.
            image_background_image = none

            # Overall width and height of image
            image_width = 382
            image_height = 361
            # Fill colour of plot circles
            image_background_circle_color = 0xF5F5F5
            # Colour of background box
            image_background_box_color = 0xF5C696
            # Colour of range rings on plot
            image_background_range_ring_color = 0xC3D9DD

            # Minimum distance (in pixels) from edge of image to plot/legend
            windrose_plot_border = 5
            # Width of legend stacked bar (in pixels)
            windrose_legend_bar_width = 10

            # Font to be used
            windrose_font_path = /usr/share/fonts/truetype/freefont/FreeSansBold.ttf
            # Font setting for N,E,S,W, bullseye % and % rings
            windrose_plot_font_size  = 10
            windrose_plot_font_color = 0x000000
            # Font setting for plot legend
            windrose_legend_font_size = 10
            windrose_legend_font_color = 0x000000
            # Font setting for plot label/title
            windrose_label_font_size = 12
            windrose_label_font_color = 0x000000

            # Comma separated list of colours used for stacked 'petals' on
            # windrose.
            # First colour is for Calm/0 speed, 2nd for 1st band, 2nd for
            # 3rd band etc. Defaults to 'lightblue', 'blue', 'midnightblue',
            # 'forestgreen', 'limegreen', 'green', 'greenyellow'
            # Only 7 colours will be used irrespective of how many are listed.
            windrose_plot_petal_colors = aqua, 0xFF9900, 0xFF3300, 0x009900, 0x00CC00, 0x33FF33, 0x00FFCC
            # Width of petals in degrees. If not set default is 16 degrees
            windrose_plot_petal_width = 16

            [[[[day_images]]]]
                # Period (in seconds) over which wind rose is constructed.
                # 86400 will use wind samples from past 24 hours, 43200 uses
                # 12 hours of samples etc
                time_length = 86400 # == 24 hours

                [[[[[daywindrose]]]]]
                    # Image filename will be [[[]]] setting on line above with
                    # extension as per format setting below. [[[daywindrose]]]
                    # using png format will result in file being named
                    # daywindrose.png

                    # File format of resulting image file. Use any file
                    # extension for image formats that PIL can write
                    # (eg png, gif etc). Defaults to png if omitted.
                    format = png

                    # To use windGust data for wind rose set [[[[windGust]]]]
                    # on next line, to use windSpeed set next line to
                    # [[[[windSpeed]]]]
                    [[[[[[windGust]]]]]]
                        # Label/title for  plot
                        label = 24 Hour Wind Rose

                        # Format of optional time stamp to be placed on image.
                        # Format codes as per Python datetime format caodes at
                        # https://docs.python.org/3/library/datetime.html

                        time_stamp = %H:%M %d %b %y

                        # Location of optional time stamp on image. If omitted
                        # no time stamp is included. Format for setting is
                        # vertical_position, horizontal_position where
                        # vertical_position is one of top or bottom;
                        # horizontal_position is one of left, center, right.
                        # Default setting (if option is present) is
                        # bottom, right

                        time_stamp_location = bottom, right

6.  By default the Stacked Windrose Image Generator generator places the
generated file in the $HTML_ROOT directory. If you wish to place the generated
files in another directory then insert a 'HTML_ROOT' setting giving the
applicable directory under the [[StackedWindRose]] sub-section in the
[StdReport] section of weewx.conf, eg:

    [[StackedWindRose]]
        skin = StackedWindRose
        HTML_ROOT = /use/this/directory

7.  Restart WeeWX:

    $ sudo /etc/init.d/weewx restart

	or

    $ sudo service weewx restart

    or

    $ sudo systemctl restart weewx

8.  This will result in the windrose image file being generated during each
report generation cycle. Generation can be confirmed by inspecting the WeeWX
log, there should be a line similar to this amongst the report generation
output:

    Jun  6 09:26:16 buster30 weewx[1476] INFO user.stackedwindrose: Generated 1
            images for StackedWindRose in 0.02 seconds


Upgrade Instructions

1.  General. Existing Stacked Windrose Image Generator installations can be
upgraded by installing the new version using the same installation method
(wee_extension or a manual installation) as was used for the existing
installation. In the case of an upgrade using wee_extension, weewx.conf will
be automatically updated with a copy of the previous weewx.conf being saved as
weewx.conf.YYYYMMDDHHMMSS where YYYYMMDDHHMMSS represents the date-time the
upgrade was performed.

2.  Upgrading from v2.1.1 and earlier. Due to a number of name changes in the
Stacked Windrose Image Generator v3.0.1 users upgrading from an earlier Stacked
Windrose Image Generator version to version 3.0.2 or later will need to
complete a number of manual steps after upgrading the Stacked Windrose Image
Generator. These steps are:

-   Delete the legacy file imageStackedWindRose.py if it exists:

        $ rm $BIN_ROOT/user/imageStackedWindRose.py

-   The [[[ImageStackedWindRoseGenerator]]] stanza under [StdReport]
[[StackedWindRose]] in weewx.conf has been renamed to
[[[StackedWindRoseImageGenerator]]] in v3.0.1 and later. After the upgrade you
will likely have both a [[[ImageStackedWindRoseGenerator]]] stanza and a
[[[StackedWindRoseImageGenerator]]] stanza. If you have customised any settings
under [[[ImageStackedWindRoseGenerator]]] you may wish to copy those
customisations to [[[StackedWindRoseImageGenerator]]]. Once this is done you
should delete the [[[ImageStackedWindRoseGenerator]]] stanza.

-   In line with WeeWX norms the config option used to set the time period
covered by a plot has been renamed from 'period' to 'time_length'. In order
to maintain backwards compatibility the Stacked Windrose Image Generator v3.0.1
or later will continue to use the 'period' config option if it exists; however,
any use of the 'time_length' option will override any 'period' option'. To
avoid confusion you may wish to rename any occurrences of 'period' under
[StdReport] [[StackedWindRose]] in weewx.conf to 'time_length' ensuring you do
not have any duplicate 'time_length' entries.


Uninstallation Instructions

1.  Run the uninstaller:

    $ ./wee_extension --uninstall=StackedWindRose

    This command assumes the user is currently in the $BIN_ROOT folder. If this
    is not the case you may need to include the path to wee_extension.

2.  Restart WeeWX:

    $ sudo /etc/init.d/weewx restart

	or

    $ sudo service weewx restart

    or

    $ sudo systemctl restart weewx

Manual Uninstallation

1.  Edit weewx.conf and delete the entire [[StackedWindRose]] section from
[StdReport].

2.  Delete the stackedwindrose.py file:

    $ rm $BIN_ROOT/user/stackedwindrose.py

3.  Delete the $SKIN_ROOT/StackedWindRose folder and its contents:

    $ rm -rf $SKIN_ROOT/StackedWindRose

4.  Restart WeeWX:

    $ sudo /etc/init.d/weewx restart

	or

    $ sudo service weewx restart

    or

    $ sudo systemctl restart weewx