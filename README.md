check_videotron_bw_usage
========================

Simple nagios compatible bandwidth consumption check script written in python.

You can run this as a standalone script or integrate it into a nagios-compatible server.

It returns the current bandwidth volume off the videotron extranet.

You may set a warning and critical limit to the amount of bandwidth and the script will return a non-zero status if the limits are reached (exit status is normalized to the nagios way).

The script depends on the BeautifulSoup module.
