"""
stackedwindrose.py

A polar wind rose image generator for WeeWX

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

Version: 3.0.2                                          Date: 6 July 2023

Revision History
  6 July 2023           v3.0.2
      - fix error due to deprecated PIL.ImageDraw.textsize() method being
        removed from PIL 10.0
  7 June 2020           v3.0.1
      - fix issue with changed max() behaviour under python3
  5 June 2020           v3.0.0
      - renamed this file and various classes, methods and variables
      - reformatting to remove numerous long lines
      - reformat of these comments
      - introduced class UniDraw allow use of fonts that don't support unicode
      - WeeWX 3.2+/4.x python2/3 compatible
      - now respects log_success and log_failure config options
      - reworked color validation code
      - changed period config setting to time_length to align with WeeWX norms

Previous Bitbucket revision history
  31 March 2017         v1.0.3
      - no change, version number change only
  14 December 2016      v1.0.2
      - fixed Image/ImageDraw import issue, now tries to import from PIL first
      - fixed issue where wind speed was always displayed in the windSpeed/
        windGust units used in the WeeWX database
      - speed and direction ValueTuples now use .value property instead of [0]
        to access the ValueTuple value
  30 November 2016      v1.0.1
      - fixed issue whereby WeeWX would exit if the requested font is not
        installed, now defaults to a system font used by WeeWX if the requested
        font is not installed
      - minor reformatting of long lines and equations
  10 January 2015       v1.0.0
      - rewritten for WeeWX v3.0.0
  1 May 2014            v0.9.3
      - fixed issue that arose with WeeWX 2.6.3 now allowing use of UTF-8
        characters in plots
      - fixed logic error in code that calculates size of wind rose 'petals'
      - removed unnecessary import statements
      - tweaked wind rose size calculations to better cater for labels on plot
  30 July 2013          v0.9.1
      - revised version number to align with WeeWX-WD version numbering
  20 July 2013          v0.1
      - initial implementation
"""

# python imports
import datetime
import math
import os.path
import time
# attempt to import image manipulation libraries from PIL, if not available
# revert to the native python imaging module
try:
    from PIL import Image, ImageColor, ImageDraw
except ImportError:
    import Image
    import ImageColor
    import ImageDraw

# python 2/3 compatibility shims
import six

# WeeWX imports
import weeutil.weeutil
import weewx.reportengine
import weewx.units

from weeplot.utilities import get_font_handle
# search_up was moved from weeutil.weeutil to weeutil.config in v3.9.0, so we
# need to try each until we find it
try:
    from weeutil.config import search_up
except ImportError:
    from weeutil.weeutil import search_up

# import/setup logging, WeeWX v3 is syslog based but WeeWX v4 is logging based,
# try v4 logging and if it fails use v3 logging
try:
    # WeeWX4 logging
    import logging
    log = logging.getLogger(__name__)

    def loginf(msg):
        log.info(msg)

except ImportError:
    # WeeWX legacy (v3) logging via syslog
    import syslog

    def logmsg(level, msg):
        syslog.syslog(level, 'stackedwindrose: %s' % msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

STACKED_WINDROSE_VERSION = '3.0.2'
DEFAULT_PETAL_COLORS = ['lightblue', 'blue', 'midnightblue', 'forestgreen',
                        'limegreen', 'green', 'greenyellow']


# ==============================================================================
#                      Class StackedWindRoseImageGenerator
# ==============================================================================

class StackedWindRoseImageGenerator(weewx.reportengine.ReportGenerator):
    """Generate a polar wind rose plot image."""

    def __init__(self, config_dict, skin_dict, gen_ts, first_run, stn_info, record=None):
        # initialize my superclass
        super(StackedWindRoseImageGenerator, self).__init__(config_dict,
                                                            skin_dict,
                                                            gen_ts,
                                                            first_run,
                                                            stn_info,
                                                            record)
        # do we log on success
        self.log_success = weeutil.weeutil.to_bool(search_up(self.skin_dict,
                                                             'log_success',
                                                             True))
        # do we log on failure
        self.log_failure = weeutil.weeutil.to_bool(search_up(self.skin_dict,
                                                             'log_failure',
                                                             True))

        # get the data binding to use
        self.data_binding = config_dict['StdArchive'].get('data_binding',
                                                          'wx_binding')

        self.image_dict = skin_dict['StackedWindRoseImageGenerator']
        self.title_dict = skin_dict['Labels']['Generic']
        self.converter = weewx.units.Converter.fromSkinDict(skin_dict)
        self.formatter = weewx.units.Formatter.fromSkinDict(skin_dict)
        self.unit_helper = weewx.units.UnitInfoHelper(self.formatter,
                                                      self.converter)

        # set image attributes
        self.image_width = int(self.image_dict['image_width'])
        self.image_height = int(self.image_dict['image_height'])
        self.image_background_box_color = int(self.image_dict['image_background_box_color'], 0)
        self.image_background_circle_color = int(self.image_dict['image_background_circle_color'], 0)
        self.image_background_range_ring_color = int(self.image_dict['image_background_range_ring_color'], 0)
        self.image_background_image = self.image_dict['image_background_image']

        # set wind rose attributes
        self.windrose_plot_border = int(self.image_dict['windrose_plot_border'])
        self.windrose_legend_bar_width = int(self.image_dict['windrose_legend_bar_width'])
        self.windrose_font_path = self.image_dict['windrose_font_path']
        self.windrose_plot_font_size = int(self.image_dict['windrose_plot_font_size'])
        self.windrose_plot_font_color = int(self.image_dict['windrose_plot_font_color'], 0)
        self.windrose_legend_font_size = int(self.image_dict['windrose_legend_font_size'])
        self.windrose_legend_font_color = int(self.image_dict['windrose_legend_font_color'], 0)
        self.windrose_label_font_size = int(self.image_dict['windrose_label_font_size'])
        self.windrose_label_font_color = int(self.image_dict['windrose_label_font_color'], 0)
        # set the petal colours
        # first get any petal colours specified in the config, if not defined
        # then use some sensible defaults
        _colors = weeutil.weeutil.option_as_list(self.image_dict.get('windrose_plot_petal_colors',
                                                                     DEFAULT_PETAL_COLORS))
        # verify our colors are valid
        _petal_colors = []
        # iterate over the colors we have and if they are valid keep them
        # otherwise discard them
        for _color in _colors:
            # parse the color, we will get bck a tuple representing the RGB
            # values or None if the color is invalid
            _col = parse_color(_color)
            # if we have a non None response it is valid
            if _col is not None:
                # valid color, append it to the petal color list
                _petal_colors.append(_col)
        # we have a list of valid colors but do we have enough, we need 7
        if len(_petal_colors) < 7:
            # if we don't have 7 augment the colors list with unused colors
            # from the defaults until we have 7
            _required = 7 - len(_petal_colors)
            for _color in DEFAULT_PETAL_COLORS:
                if _required > 0:
                    _parsed = parse_color(_color)
                    if _parsed not in _petal_colors:
                        _petal_colors.append(_parsed)
                        _required -= 1
        # save the final ist of petal colors
        self.petal_colors = list(_petal_colors)
        # get petal width, if not defined then set default to 16 (degrees)
        try:
            self.windrose_plot_petal_width = int(self.image_dict['windrose_plot_petal_width'])
        except KeyError:
            self.windrose_plot_petal_width = 16
        # Boundaries for speed range bands, these mark the colour boundaries
        # on the stacked bar in the legend. 7 elements only (ie 0, 10% of max,
        # 20% of max ... 100% of max)
        self.speed_factor = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]

        # initialise some properties for later use
        self.plotgen_ts = None
        self.label = None
        self.time_stamp = None
        self.time_stamp_location = None
        self.units = None
        self.unit_label = None
        self.obs = None
        self.dir_name = None
        self.max_ring_value = None
        self.label_dir = None
        self.plot_font = None
        self.legend_font = None
        self.label_font = None
        self.rose_max_dia = None
        self.origin_x = None
        self.origin_y = None
        self.draw = None

    def run(self):

        # generate any images
        self.gen_images(self.gen_ts)

    def gen_images(self, gen_ts):
        """Generate any images.

            The time period chosen is from gen_ts going back skin.conf
            'time_length' seconds.

            gen_ts: The time stamp of the end of the plot period. If not set
                    defaults to the time of the last record in the archive.
        """

        # get the time so can know how long we take
        t1 = time.time()
        # set plot count to 0
        ngen = 0
        # iterate over each time span class (day, week, month, etc)
        for timespan in self.image_dict.sections:
            # iterate over all plot names in this time span class
            for plotname in self.image_dict[timespan].sections:
                # accumulate all options from parent nodes
                plot_options = weeutil.weeutil.accumulateLeaves(self.image_dict[timespan][plotname])
                # get a db manager for the database archive
                db_manager = self.db_binder.get_manager(self.data_binding)
                # Get end time for plot. In order try gen_ts, last known good
                # archive time stamp and then current time.
                self.plotgen_ts = gen_ts
                if not self.plotgen_ts:
                    self.plotgen_ts = db_manager.lastGoodStamp()
                    if not self.plotgen_ts:
                        self.plotgen_ts = time.time()
                # get the path of the image file we will save
                image_root = os.path.join(self.config_dict['WEEWX_ROOT'],
                                          plot_options['HTML_ROOT'])
                # Get image file format. Can use any format PIL can write.
                # Default to .png
                if 'format' in plot_options:
                    image_format = plot_options['format']
                else:
                    image_format = "png"
                # get full file name and path for plot
                img_file = os.path.join(image_root, '%s.%s' % (plotname,
                                                               image_format))
                # check whether this plot needs to be done at all
                # Obtain the length of time to be covered by the plot, first
                # check for the legacy 'period' option (renamed 'time_length'
                # as of v3.0.0)
                time_length = weeutil.weeutil.to_int(plot_options.get('period'))
                # if we have a None value perhaps we are using the new
                # 'time_length' option
                if time_length is None:
                    time_length = weeutil.weeutil.to_int(plot_options.get('time_length',
                                                                          86400))
                if self.skip_this_plot(self.plotgen_ts, time_length, img_file):
                    continue
                # Create the subdirectory where the image is to be saved. Wrap
                # in a try block in case it already exists.
                try:
                    os.makedirs(os.path.dirname(img_file))
                except OSError as e:
                    if e.errno == 17:
                        # file exists error, continue
                        pass
                    else:
                        # otherwise raise the error
                        raise
                # iterate over each 'line' to be added to the plot.
                for line_name in self.image_dict[timespan][plotname].sections:
                    # accumulate options from parent nodes.
                    line_options = weeutil.weeutil.accumulateLeaves(self.image_dict[timespan][plotname][line_name])

                    # See if a plot title has been explicitly requested.
                    # 'label' is used for consistency in skin.conf with
                    # ImageGenerator sections
                    self.label = line_options.get('label')
                    # has a time_stamp has been explicitly requested.
                    self.time_stamp = line_options.get('time_stamp')
                    # see if time_stamp location has been explicitly set
                    _location = line_options.get('time_stamp_location')
                    if _location:
                        self.time_stamp_location = [x.upper() for x in _location]
                    else:
                        self.time_stamp_location = None
                    # get units to be used
                    self.units = self.skin_dict['Units']['Groups']['group_speed']
                    # get unit label for display on legend
                    self.unit_label = self.skin_dict['Units']['Labels'][self.units]
                    # See what SQL variable type to use for this plot and get
                    # corresponding 'direction' type. Can really only plot
                    # windSpeed and windGust, if it's anything else default to
                    # windSpeed.
                    self.obs = line_options.get('data_type', line_name)
                    if self.obs == 'windSpeed':
                        self.dir_name = 'windDir'
                    elif self.obs == 'windGust':
                        self.dir_name = 'windGustDir'
                    else:
                        self.obs = 'windSpeed'
                        self.dir_name = 'windDir'
                    # get data tuples for speed and direction
                    # TODO. Review, may need to be time_length + 1
                    _span = weeutil.weeutil.TimeSpan(self.plotgen_ts - time_length,
                                                     self.plotgen_ts)
                    (_t_vec, _t_vec_stop, _sp_vec) = db_manager.getSqlVectors(_span,
                                                                              self.obs)
                    (_t_vec, _t_vec_d_stop, dir_data) = db_manager.getSqlVectors(_span,
                                                                                 self.dir_name)
                    # convert the speeds to units to be used in the plot
                    speed_data = weewx.units.convert(_sp_vec, self.units)
                    # find maximum speed from our data
                    _max_speed = weeutil.weeutil.max_with_none(speed_data.value)
                    # set upper speed range for our plot, set to a multiple of
                    # 10 for a neater display
                    _max_speed_range = (int(_max_speed / 10.0) + 1) * 10
                    # setup 2D list with speed range boundaries in
                    # speed_list[0] petal colours in speed_list[1]
                    speed_list = [[0 for x in range(7)] for x in range(2)]
                    # store petal colours
                    speed_list[1] = self.petal_colors
                    # iterate over each speed range boundary and store in
                    # speed_list[0]
                    i = 1
                    while i < 7:
                        speed_list[0][i] = self.speed_factor[i] * _max_speed_range
                        i += 1
                    # Setup 2D list for wind direction. wind_bin[0] represents
                    # each of 16 compass directions ([0] is N, [1] is ENE etc).
                    # wind_bin[1] holds count of obs in a particular speed
                    # range for given direction
                    wind_bin = [[0 for x in range(7)] for x in range(17)]
                    # setup list to hold obs counts for each speed range
                    speed_bin = [0 for x in range(7)]
                    # how many obs do we have?
                    samples = len(_t_vec_stop[0])
                    # Iterate over the samples and increment direction counts
                    # and speed ranges for each direction as necessary. 'None'
                    # direction is counted as 'calm' (or 0 speed) and
                    # (by definition) no direction and are plotted in the
                    # 'bulls eye' on the plot.
                    i = 0
                    while i < samples:
                        if (speed_data.value[i] is None) or (dir_data.value[i] is None):
                            wind_bin[16][6] += 1
                        else:
                            _bin = int((dir_data.value[i] + 11.25) / 22.5) % 16
                            if speed_data.value[i] > speed_list[0][5]:
                                wind_bin[_bin][6] += 1
                            elif speed_data.value[i] > speed_list[0][4]:
                                wind_bin[_bin][5] += 1
                            elif speed_data.value[i] > speed_list[0][3]:
                                wind_bin[_bin][4] += 1
                            elif speed_data.value[i] > speed_list[0][2]:
                                wind_bin[_bin][3] += 1
                            elif speed_data.value[i] > speed_list[0][1]:
                                wind_bin[_bin][2] += 1
                            elif speed_data.value[i] > 0:
                                wind_bin[_bin][1] += 1
                            else:
                                wind_bin[_bin][0] += 1
                        i += 1
                    # add 'None' obs to 0 speed count
                    speed_bin[0] += wind_bin[16][6]
                    # don't need the 'None' counts so we can delete them
                    del wind_bin[-1]
                    # Set total (direction independent) speed counts. Iterate
                    # over each petal speed range and increment direction
                    # independent speed ranges as necessary.
                    j = 0
                    while j < 7:
                        i = 0
                        while i < 16:
                            speed_bin[j] += wind_bin[i][j]
                            i += 1
                        j += 1
                    # Calculate the value to represented by outer ring
                    # (range 0 to 1). Round up to next multiple of 0.05
                    # (ie next 5%)
                    self.max_ring_value = (int(max(sum(b) for b in wind_bin)/(0.05 * samples)) + 1) * 0.05
                    # Find which wind rose arm to use to display ring range
                    # labels - look for one that is relatively clear. Only
                    # consider NE, SE, SW and NW. Preference in order is SE,
                    # SW, NE and NW
                    # is SE clear?
                    if sum(wind_bin[6])/float(samples) <= 0.3 * self.max_ring_value:
                        # it is so take it
                        label_dir = 6
                    else:
                        # it's not so check the others
                        for i in [10, 2, 14]:
                            if sum(wind_bin[i])/float(samples) <= 0.3*self.max_ring_value:
                                # got one so take it and break
                                label_dir = i
                                break
                        else:
                            # none are free so take the smallest of the four
                            # set count to max possible number of readings + 1
                            label_count = samples + 1
                            # iterate over the directions
                            for i in [2, 6, 10, 14]:
                                # does this direction have fewer obs than
                                # previous best (least)
                                if sum(wind_bin[i]) < label_count:
                                    # it does so set min count to this bin
                                    label_count = sum(wind_bin[i])
                                    # set label_dir to this direction
                                    label_dir = i
                    # now set the label direction we are going to use
                    self.label_dir = label_dir
                    # get an image object to hold our plot
                    image = self.windrose_image_setup()
                    self.draw = UniDraw(image)
                    # set fonts to be used
                    self.plot_font = get_font_handle(self.windrose_font_path,
                                                     self.windrose_plot_font_size)
                    self.legend_font = get_font_handle(self.windrose_font_path,
                                                       self.windrose_legend_font_size)
                    self.label_font = get_font_handle(self.windrose_font_path,
                                                      self.windrose_label_font_size)
                    # estimate space required for the legend
                    text_w, text_h = self.draw.textsize("0 (100%)",
                                                        font=self.legend_font)
                    legend_w = int(text_w + 2 * self.windrose_legend_bar_width + 1.5 * self.windrose_plot_border)
                    # estimate space required for label (if required)
                    text_w, text_h = self.draw.textsize("Wind Rose",
                                                        font=self.label_font)
                    if self.label:
                        label_h = int(text_w + self.windrose_plot_border)
                    else:
                        label_h = 0
                    # Calculate the diameter of the circular plot space in
                    # pixels. Two diameters are calculated, one based on image
                    # height and one based on image width, and the smallest one
                    # used. To prevent optical distortion for small plots
                    # diameter will be divisible by 22.
                    self.rose_max_dia = min(int((self.image_height - 2 * self.windrose_plot_border - label_h / 2) / 22.0) * 22,
                                            int((self.image_width - (2 * self.windrose_plot_border + legend_w)) / 22.0) * 22)
                    if self.image_width > self.image_height:
                        # plot is wider than it is high
                        text_w, text_h = self.draw.textsize("W",
                                                            font=self.plot_font)
                        # x coord of windrose circle origin(0,0) is top left
                        # corner
                        self.origin_x = self.windrose_plot_border + text_w + 2 + self.rose_max_dia / 2
                        # y coord of windrose circle origin(0,0) is top left
                        # corner
                        self.origin_y = int(self.image_height / 2)
                    else:
                        # plot is higher than it is wide
                        # x coord of windrose circle origin(0,0) is top left
                        # corner
                        self.origin_x = 2 * self.windrose_plot_border + self.rose_max_dia / 2
                        # y coord of windrose circle origin(0,0) is top left
                        # corner
                        self.origin_y = 2 * self.windrose_plot_border + self.rose_max_dia / 2
                    # Setup windrose plot. Plot circles, range rings, range
                    # labels, N-S and E-W centre lines and compass point labels
                    self.wind_rose_plot_setup()
                    # Plot the wind rose petals. Each petal is constructed from
                    # overlapping pie slices starting from outside (biggest)
                    # and working in (smallest).
                    # start with the 'North' petal
                    a = 0
                    # iterate over each wind rose arm
                    while a < len(wind_bin):
                        s = len(speed_list[0]) - 1
                        cum_rad = sum(wind_bin[a])
                        if cum_rad > 0:
                            arm_rad = int((10 * self.rose_max_dia * sum(wind_bin[a])) /
                                          (11 * 2.0 * self.max_ring_value * samples))
                            while s > 0:
                                # calc radius of current arm
                                pie_rad = int(round(arm_rad * cum_rad/sum(wind_bin[a]) + self.rose_max_dia/22, 0))
                                # set bound box for pie slice
                                xy = (self.origin_x-pie_rad,
                                      self.origin_y-pie_rad,
                                      self.origin_x+pie_rad,
                                      self.origin_y+pie_rad)
                                # draw pie slice
                                start = int(-90 + a * 22.5 - self.windrose_plot_petal_width / 2)
                                end = int(-90 + a * 22.5 + self.windrose_plot_petal_width / 2)
                                self.draw.pieslice(xy, start, end,
                                                   fill=speed_list[1][s],
                                                   outline='black')
                                cum_rad -= wind_bin[a][s]
                                # move 'in' for next pie slice
                                s -= 1
                        # next arm
                        a += 1
                    # draw 'bulls eye' to represent speed=0 or calm
                    # first produce the label
                    label0 = "%d%%" % int(round(100.0 * speed_bin[0]/sum(speed_bin), 0))
                    # work out its size, particularly its width
                    text_w, text_h = self.draw.textsize(label0, font=self.plot_font)
                    # size the bound box
                    xy = (int(self.origin_x-self.rose_max_dia/22),
                          int(self.origin_y-self.rose_max_dia/22),
                          int(self.origin_x+self.rose_max_dia/22),
                          int(self.origin_y+self.rose_max_dia/22))
                    # draw the circle
                    self.draw.ellipse(xy, outline='black', fill=speed_list[1][0])
                    # size the text
                    xy = (int(self.origin_x - text_w / 2),
                          int(self.origin_y - text_h / 2))
                    # draw the text
                    self.draw.text(xy, label0,
                                   fill=self.windrose_plot_font_color,
                                   font=self.plot_font)
                    # Set up the legend. Draw label/title (if set), stacked
                    # bar, bar labels and units
                    self.legend_setup(speed_list, speed_bin)
                # save the file.
                image.save(img_file)
                # increment number of images generated
                ngen += 1
        if self.log_success:
            t2 = time.time()
            loginf("Generated %d images for %s in %.2f seconds" % (ngen,
                                                                   self.skin_dict['REPORT_NAME'],
                                                                   t2 - t1))

    def windrose_image_setup(self):
        """Create image object for us to draw on.

        image: Image object to be returned for us to draw on.
        """

        try:
            image = Image.open(self.image_background_image)
        except IOError:
            image = Image.new("RGB",
                              (self.image_width, self.image_height),
                              self.image_background_box_color)
        return image

    def wind_rose_plot_setup(self):
        """Draw circular plot background, rings, axes and labels."""

        # draw speed circles
        # First calculate the distance between the wind rose range rings. Note that
        # 'calm' bulls eye is at centre of plot with diameter equal to _min_radius.
        _min_radius = self.rose_max_dia/11
        # iterate over the range rings starting from the inside and working out
        i = 5
        while i > 0:
            xy = (self.origin_x - _min_radius * (i + 0.5),
                  self.origin_y - _min_radius * (i + 0.5),
                  self.origin_x + _min_radius * (i + 0.5),
                  self.origin_y + _min_radius * (i + 0.5))
            # draw the ring
            self.draw.ellipse(xy,
                              outline=self.image_background_range_ring_color,
                              fill=self.image_background_circle_color)
            i -= 1

        # draw vertical centre line
        xy = [(self.origin_x, self.origin_y - self.rose_max_dia / 2 - 2),
              (self.origin_x, self.origin_y + self.rose_max_dia / 2 + 2)]
        self.draw.line(xy, fill=self.image_background_range_ring_color)
        # draw horizontal centre line
        xy = [(self.origin_x - self.rose_max_dia / 2 - 2, self.origin_y),
              (self.origin_x + self.rose_max_dia / 2 + 2, self.origin_y)]
        self.draw.line(xy, fill=self.image_background_range_ring_color)
        # draw N,S,E,W markers
        text_w, text_h = self.draw.textsize('N', font=self.plot_font)
        xy = (self.origin_x - text_w / 2,
              self.origin_y - self.rose_max_dia / 2 - 1 - text_h)
        self.draw.text(xy, 'N', fill=self.windrose_plot_font_color, font=self.plot_font)
        text_w, text_h = self.draw.textsize('S', font=self.plot_font)
        xy = (self.origin_x - text_w / 2,
              self.origin_y + self.rose_max_dia / 2 + 3)
        self.draw.text(xy, 'S', fill=self.windrose_plot_font_color, font=self.plot_font)
        text_w, text_h = self.draw.textsize('W', font=self.plot_font)
        xy = (self.origin_x - self.rose_max_dia / 2 - 1 - text_w,
              self.origin_y - text_h / 2)
        self.draw.text(xy, 'W', fill=self.windrose_plot_font_color, font=self.plot_font)
        text_w, text_h = self.draw.textsize('E', font=self.plot_font)
        xy = (self.origin_x + self.rose_max_dia / 2 + 1,
              self.origin_y - text_h / 2)
        self.draw.text(xy, 'E', fill=self.windrose_plot_font_color, font=self.plot_font)
        # draw % labels on rings
        # calculate the value increment between rings
        _label_inc = self.max_ring_value/5
        # initialise a list to hold ring labels
        speed_labels = list((0, 0, 0, 0, 0))
        i = 1
        while i < 6:
            speed_labels[i - 1] = "%d%%" % int(round(_label_inc * i * 100, 0))
            i += 1
        # calculate location of ring labels
        _angle = 7 * math.pi / 4 + int(self.label_dir / 4.0) * math.pi / 2
        label_offset_x = int(round(self.rose_max_dia / 22 * math.cos(_angle), 0))
        label_offset_y = int(round(self.rose_max_dia / 22 * math.sin(_angle), 0))
        # Draw ring labels. Note leave inner ring blank due to lack of space. For
        # clarity each label (except for outside ring) is drawn on a rectangle with
        # background colour set to that of the circular plot.
        i = 2
        while i < 5:
            text_w, text_h = self.draw.textsize(speed_labels[i - 1],
                                                font=self.plot_font)
            x0 = self.origin_x + (2 * i + 1) * label_offset_x - text_w / 2
            y0 = self.origin_y + (2 * i + 1) * label_offset_y - text_h / 2
            x1 = self.origin_x + (2 * i + 1) * label_offset_x + text_w / 2
            y1 = self.origin_y + (2 * i + 1) * label_offset_y + text_h / 2
            self.draw.rectangle([x0, y0, x1, y1],
                                fill=self.image_background_circle_color)
            xy = (self.origin_x + (2 * i + 1) * label_offset_x - text_w / 2,
                  self.origin_y + (2 * i + 1) * label_offset_y - text_h / 2)
            self.draw.text(xy,
                           speed_labels[i-1],
                           fill=self.windrose_plot_font_color, font=self.plot_font)
            i += 1
        # draw outside ring label
        text_w, text_h = self.draw.textsize(speed_labels[i-1], font=self.plot_font)
        xy = (self.origin_x + (2 * i + 1) * label_offset_x - text_w / 2,
              self.origin_y + (2 * i + 1) * label_offset_y - text_h / 2)
        self.draw.text(xy,
                       speed_labels[i-1],
                       fill=self.windrose_plot_font_color, font=self.plot_font)

    def legend_setup(self, speed_list, speed_bin):
        """Draw plot title (if requested), legend and time stamp (if requested).

            speed_list: 2D list with speed range boundaries in speed_list[0] and
                        petal colours in speed_list[1]

            speed_bin: 1D list to hold overall obs count for each speed range
        """

        # set static values
        text_w, text_h = self.draw.textsize('E', font=self.plot_font)
        # label_x and label_y = x,y coords of bottom left of stacked bar.
        # Everything else is relative to this point
        label_x = self.origin_x+self.rose_max_dia/2 + text_w + 10
        label_y = self.origin_y+self.rose_max_dia/2 - self.rose_max_dia/22
        bulb_d = int(round(1.2 * self.windrose_legend_bar_width, 0))
        # draw stacked bar and label with values/percentages
        i = 6
        while i > 0:
            x0 = label_x
            y0 = label_y - (0.85 * self.rose_max_dia * self.speed_factor[i])
            x1 = label_x + self.windrose_legend_bar_width
            y1 = label_y
            self.draw.rectangle([x0, y0, x1, y1],
                                fill=speed_list[1][i], outline='black')
            text_w, text_h = self.draw.textsize(str(speed_list[0][i]),
                                                font=self.legend_font)
            xy = (label_x + 1.5 * self.windrose_legend_bar_width,
                  label_y - text_h / 2 - (0.85 * self.rose_max_dia * self.speed_factor[i]))
            _text = '%d (%d%%)' % (int(round(speed_list[0][i], 0)),
                                   int(round(100 * speed_bin[i]/sum(speed_bin), 0)))
            self.draw.text(xy, _text,
                           fill=self.windrose_legend_font_color, font=self.legend_font)
            i -= 1
        text_w, text_h = self.draw.textsize(str(speed_list[0][0]),
                                            font=self.legend_font)
        # draw 'calm' or 0 speed label and %
        xy = (label_x + 1.5 * self.windrose_legend_bar_width,
              label_y - text_h / 2 - (0.85 * self.rose_max_dia * self.speed_factor[0]))
        _text = '%d (%d%%)' % (speed_list[0][0],
                               int(round(100.0 * speed_bin[0]/sum(speed_bin), 0)))
        self.draw.text(xy, _text,
                       fill=self.windrose_legend_font_color, font=self.legend_font)
        text_w, text_h = self.draw.textsize('Calm', font=self.legend_font)
        xy = (label_x - text_w - 2,
              label_y - text_h / 2 - (0.85 * self.rose_max_dia * self.speed_factor[0]))
        self.draw.text(xy, 'Calm',
                       fill=self.windrose_legend_font_color, font=self.legend_font)
        # draw 'calm' bulb on bottom of stacked bar
        xy = (label_x - bulb_d / 2 + self.windrose_legend_bar_width / 2,
              label_y - self.windrose_legend_bar_width / 6,
              label_x + bulb_d / 2 + self.windrose_legend_bar_width / 2,
              label_y - self.windrose_legend_bar_width / 6 + bulb_d)
        self.draw.ellipse(xy, outline='black', fill=speed_list[1][0])
        # draw legend title
        if self.obs == 'windGust':
            title_text = 'Gust Speed'
        else:
            title_text = 'Wind Speed'
        text_w, text_h = self.draw.textsize(title_text, font=self.legend_font)
        xy = (label_x + self.windrose_legend_bar_width / 2 - text_w / 2,
              label_y - 5 * text_h / 2 - (0.85 * self.rose_max_dia))
        self.draw.text(xy, title_text,
                       fill=self.windrose_legend_font_color, font=self.legend_font)
        # draw legend units label
        text_w, text_h = self.draw.textsize('(%s)' % self.unit_label.strip(),
                                            font=self.legend_font)
        xy = (label_x + self.windrose_legend_bar_width / 2 - text_w / 2,
              label_y - 3 * text_h / 2 - (0.85 * self.rose_max_dia))
        self.draw.text(xy, '(%s)' % self.unit_label.strip(),
                       fill=self.windrose_legend_font_color, font=self.legend_font)
        # draw plot title (label) if any, make sure we convert any unicode that
        # might sneak in
        if self.label:
            text_w, text_h = self.draw.textsize(self.label, font=self.label_font)
            try:
                self.draw.text((self.origin_x - text_w/2, text_h/2),
                               self.label,
                               fill=self.windrose_label_font_color,
                               font=self.label_font)
            except UnicodeEncodeError:
                self.draw.text((self.origin_x - text_w/2, text_h/2),
                               self.label.encode("utf-8"),
                               fill=self.windrose_label_font_color,
                               font=self.label_font)
        # draw plot timestamp if any
        if self.time_stamp:
            ts_text = datetime.datetime.fromtimestamp(self.plotgen_ts).strftime(self.time_stamp).strip()
            text_w, text_h = self.draw.textsize(ts_text, font=self.label_font)
            if self.time_stamp_location is not None:
                if 'TOP' in self.time_stamp_location:
                    ts_y = self.windrose_plot_border + text_h
                else:
                    ts_y = self.image_height - self.windrose_plot_border - text_h
                if 'LEFT' in self.time_stamp_location:
                    ts_x = self.windrose_plot_border
                elif ('CENTER' in self.time_stamp_location) or ('CENTRE' in self.time_stamp_location):
                    ts_x = self.origin_x-text_w / 2
                else:
                    ts_x = self.image_width - self.windrose_plot_border - text_w
            else:
                ts_y = self.image_height - self.windrose_plot_border - text_h
                ts_x = self.image_width - self.windrose_plot_border - text_w
            self.draw.text((ts_x, ts_y),
                           ts_text,
                           fill=self.windrose_legend_font_color, font=self.legend_font)

    @staticmethod
    def skip_this_plot(time_ts, time_length, img_file):
        """Determine if a plot is to be skipped.

        Plots must be generated if:
        (1) it does not exist
        (2) it is 24 hours old (or older)

        Every plot, irrespective of time_length, will likely be different to the
        last one but to reduce load for long time_length plots a plot can be
        skipped if:
        (1) plot length is greater than 30 days and the plot file is less than
            24 hours old
        (3) plot length is greater than 7 but less than 30 day and the plot file
            is less than 1 hour old
        (4) can't think of another reason! Let's see how (1) and (2) go

        time_ts: Timestamp holding time of plot

        time_length: Length of time over which plot is produced

        img_file: Full path and filename of plot file
        """

        # the image definitely has to be generated if it doesn't exist
        if not os.path.exists(img_file):
            return False

        # if the image is older than 24 hours then regenerate
        if time_ts - os.stat(img_file).st_mtime >= 86400:
            return False

        # if time_length > 30 days and the image is less than 24 hours old then
        # skip
        if time_length > 18144000 and time_ts - os.stat(img_file).st_mtime < 86400:
            return True

        # if time_length > 7 days and the image is less than 1 hour old then skip
        if time_length >= 604800 and time_ts - os.stat(img_file).st_mtime < 3600:
            return True

        # otherwise we must regenerate
        return False


# ==============================================================================
#                               class UniDraw
# ==============================================================================


class UniDraw(ImageDraw.ImageDraw):
    """Subclassed PIL ImageDraw.ImageDraw that supports non-Unicode fonts.

    Not all fonts support Unicode characters. Those that do not will raise a
    UnicodeEncodeError exception. This class subclasses the regular PIL
    ImageDraw.ImageDraw class and overrides/adds selected functions to catch
    these exceptions. If a UnicodeEncodeError is caught rendering the string is
    retried, this time using a UTF8 encoded string.

    The text() method is overriden to catch possible UnicodeEncodeError
    exceptions and substitute a UTF8 encode string instead.

    The textsize() method has been added as whilst the textsize() method
    has been removed from PIL 10.0 it still remains in earlier PIL versions and
    the (now) complex error catching
    """

    def text(self, position, string, **options):
        """Draw a string using a Unicode or non-Unicode font."""

        try:
            return ImageDraw.ImageDraw.text(self, position, string, **options)
        except UnicodeEncodeError:
            # our string needs to be properly encoded, try again with utf-8 encoding
            return ImageDraw.ImageDraw.text(self, position, string.encode('utf-8'), **options)

    def textsize(self, string, **options):
        """Obtain the size of a string rendered using a Unicode or non-Unicode font.

        Returns the width and height of the rendered string.

        Unfortunately the ImageDraw.textsize() method was deprecated in PIL
        v9.2 and removed in v10.0. ImageDraw.textbbox() and
        ImageDraw.multiline_textbbox() methods should be used instead. In order
        to support earlier PIL versions we need to first try the new method and
        if not found then try the old.
        """

        # first try to use textsize(), if we have PIL < 10.0 it will either
        # work or a UnicodeEncodeError will be raised
        try:
            return ImageDraw.ImageDraw.textsize(self, string, **options)
        except UnicodeEncodeError:
            # we have PIL < 10.0, but we encountered a UnicodeEncodeError, try
            # again with utf-8 encoding
            return ImageDraw.ImageDraw.textsize(self, string.encode('utf-8'), **options)
        except AttributeError:
            # there is no textsize() method so this must be PIL 10.0 or later,
            # try again but this time using the PIL 10.0 equivalents
            try:
                # first try the textbox bounds
                left, top, right, bottom = ImageDraw.ImageDraw.multiline_textbbox(self,
                                                                                  xy=(0, 0),
                                                                                  text=string,
                                                                                  **options)
                # now calculate and return the width and height we require
                return right - left, bottom - top
            except UnicodeEncodeError:
                # we encountered a UnicodeEncodeError, try the same call again
                # but with utf-8 encoding
                left, top, right, bottom = ImageDraw.ImageDraw.multiline_textbbox(self,
                                                                                  xy=(0, 0),
                                                                                  text=string.encode('utf-8'),
                                                                                  **options)
                # now calculate and return the width and height we require
                return right - left, bottom - top


def parse_color(color, default=None):
    """Parse a color value.

    Parse a string representing a color and return the RGB tuple represented by
    the value. The string may be:
    -   a supported color word eg 'red'
    -   in the format #RRGGBB where RR, GG and BB are hexadecimal values from
        00-FF inclusive representing the red, green and blue values
        respectively, eg #FF8800
    -   in the format rgb(R,G,B) where R,G,B are numbers from 0 to 255 or
        percentages from 0% to 100% representing the red green and blue values
        respectively, eg rgb(255, 127, 0) or rgb(100%, 50%, 0%)
    -   in the format 0xBBGGRR where RR, GG and BB are hexadecimal values from
        00-FF inclusive representing the red, green and blue values
        respectively, eg 0x0088FF

    If the string cannot be parsed the default parameter is returned if it is
    a valid color otherwise None is returned.

    Inputs:
        color:   the value to be parsed
        default: the value returned if color cannot be parsed

    Returns:
        a valid rgb tuple or None
    """
    # first up check if we have a string to parse, if we don't return None
    if color is None:
        return None
    # now try parsing parameter color using getrgb()
    try:
        return ImageColor.getrgb(color)
    except ValueError:
        # getrgb() could not parse the string, perhaps it is because color is
        # in the format 0xBBGGRR
        if isinstance(color, six.string_types) and color.startswith('0x'):
            # we have a string that starts with '0x', try to convert it to an
            # int
            try:
                rgbint = int(color, 0)
            except ValueError:
                # could not convert to an int, so our string cannot be
                # converted to a color. Let it pass knowing the final return
                # will attempt to return the default.
                pass
            else:
                # we could convert to an int so break out the RGB components
                r = rgbint & 255
                g = (rgbint >> 8) & 255
                b = (rgbint >> 16) & 255
                # parse the RGB components and return the result
                return parse_color('rgb(%s,%s,%s)' % (r, g, b), default)
    except AttributeError:
        # getrgb() could not parse the string, most likely because the string
        # was not a string. Let it pass knowing the final return will attempt
        # to return the default.
        pass
    return parse_color(default)
