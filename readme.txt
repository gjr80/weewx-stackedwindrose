Stacked Windrose Image Generator for WeeWX

Note: The instructions and links in this readme have been produced primarily
      for WeeWX v5. In general, the same concepts apply to earlier WeeWX
      versions; however, the detailed steps, WeeWX utilities used and commands
      required will be different. If you wish to persist with an earlier WeeWX
      version you should follow the instructions highlighted for legacy WeeWX
      installations. Alternatively, you may find it easier to just upgrade to
      WeeWX v5 - after all it is free.

Description
The Stacked Windrose Image Generator extension is a WeeWX extension that
generates a polar wind plot, commonly known as a windrose, that shows the
distribution of wind speed and direction over a period of time. The Stacked
Windrose Image Generator extension consists of a single skin controlling a
custom image generator that produces a windrose image based upon WeeWX archive
data.


Pre-Requisites

The Stacked Windrose Image Generator requires WeeWX v3.2.0 or greater and will
operate under Python2 or Python 3.


Installation Instructions

1. Install the latest version of the Stacked Windrose Image Generator using the
weectl utility (http://weewx.com/docs/5.0/utilities/weectl-extension/#install-an-extension).

    Note: The exact command syntax to invoke weectl on your system will
          depend on the installer used to install WeeWX. Refer to Installation
          methods (http://weewx.com/docs/5.0/usersguide/installing/#installation-methods)
          in the WeeWX User's Guide (http://weewx.com/docs/5.0/usersguide/introduction/).

    For WeeWX v5.0 or later package installs:

        weectl extension install https://github.com/gjr80/weewx-stackedwindrose/releases/latest/download/stackedwindrose.zip

    For WeeWX v5.0 or later pip installs the Python virtual environment must be
    activated before the extension is installed:

        source ~/weewx-venv/bin/activate
        weectl extension install https://github.com/gjr80/weewx-stackedwindrose/releases/latest/download/stackedwindrose.zip

    For WeeWX v5.0 or later installs from git the Python virtual environment
    must be activated before the extension is installed:

        source ~/weewx-venv/bin/activate
        python3 ~/weewx/src/weectl.py extension install https://github.com/gjr80/weewx-stackedwindrose/releases/latest/download/stackedwindrose.zip

    For legacy WeeWX installs download and install the extension package using
    the legacy wee_extension utility:

        wget -P /var/tmp/ https://github.com/gjr80/weewx-stackedwindrose/releases/latest/download/stackedwindrose.zip
        wee_extension --install=/var/tmp/stackedwindrose.zip

2. Restart WeeWX:

       sudo systemctl restart weewx

    or

       sudo /etc/init.d/weewx restart

    or

       sudo service weewx restart

3.  This will result in the windrose image file being generated during each
report generation cycle. By default, the windrose image file will be named
daywindrose.png and located in the directory referred to by the symbolic
location HTML_ROOT (refer to Where to find things
(http://weewx.com/docs/5.0/usersguide/where/) in the WeeWX User's Guide for
details of which directory HTML_ROOT refers to for your WeeWX installation
type, for legacy WeeWX installs refer to the WeeWX User's Guide for the WeeWX
version being used). Generation can also be confirmed by inspecting the WeeWX
log, there should be a line similar to this amongst the report generation
output:

        Jun  6 09:26:16 buster30 weewx[1476] INFO user.stackedwindrose: Generated 1 images for StackedWindRose in 0.02 seconds


Upgrade Instructions

To upgrade from an earlier version of the Stacked Windrose Image Generator
simply install the Stacked Windrose Image Generator version you wish to upgrade
to as per the Installation Instructions above.


Support

General support issues for the Stacked Windrose Image Generator should be
raised in the Google Groups weewx-user forum
(https://groups.google.com/g/weewx-user). The Stacked Windrose Image Generator
Issues Page (https://github.com/gjr80/weewx-stackedwindrose/issues) should only
be used for specific bugs in the Stacked Windrose Image Generator code. It is
recommended that even if a Stacked Windrose Image Generator bug is suspected
users first post to the Google Groups weewx-user forum
(https://groups.google.com/g/weewx-user "Google Groups weewx-user forum").


Licensing

The Stacked Windrose Image Generator is licensed under the GNU Public
License v3 (https://github.com/gjr80/weewx-stackedwindrose/blob/master/LICENSE).
