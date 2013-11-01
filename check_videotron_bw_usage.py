#!/usr/bin/python

# check videotron bandwidth usage

# set constants for nagios
STATE = {'OK': 0,
         'WARNING': 1,
         'CRITICAL': 2,
         'UNKNOWN': 3,
         'DEPENDENT': 4}

try:
    from BeautifulSoup import BeautifulSoup
    import requests
    import sys
    import logging
    import argparse
except ImportError as e:
    print "could not load all required modules, please verify: {0}".format(str(e))
    sys.exit(STATE['UNKNOWN'])


def get_script_args():
    argument_parser = argparse.ArgumentParser()

    # Default optional arguments required for the use of this framework.
    # Add optional script arguments in this section.
    default_opts = argument_parser.add_argument_group('Optional arguments')

    default_opts.add_argument('-w', '--warning',
                              action='store',
                              dest='warning_threshold',
                              default=str(sys.maxint),
                              required=False,
                              help="thresholds to trigger warning status")

    default_opts.add_argument('-c', '--critical',
                              action='store',
                              dest='critical_threshold',
                              default=str(sys.maxint),
                              required=False,
                              help="thresholds to trigger critical status")

    # Required script arguments
    required_opts = argument_parser.add_argument_group('Required arguments')

    required_opts.add_argument('-a', '--account',
                               action='store',
                               default='',  # vlKIEHTP
                               dest='videotron_account',
                               required=True,
                               help="your videotron ligne account")

    args = argument_parser.parse_args()
    return args


def main():

    # get command line args & default values
    args = get_script_args()

    # validate inputs

    # thresholds should be integers
    try:
        args.critical_threshold = int(args.critical_threshold)
    except ValueError:
        logging.error("'{0}' is not an integer".format(args.critical_threshold))
        return STATE['UNKNOWN']

    try:
        args.warning_threshold = int(args.warning_threshold)
    except ValueError:
        logging.error("'{0}' is not an integer".format(args.warning_threshold))
        return STATE['UNKNOWN']

    # thresholds should be logically ascending
    if args.warning_threshold > args.critical_threshold:
        logging.error("warning threshold ({0:d}) is higher"
                      " than critical threshold ({1:d})".format(args.warning_threshold,
                                                                args.critical_threshold))
        return STATE['UNKNOWN']

    request_url = "https://extranet.videotron.com/services/secur/extranet/tpia/" \
                  "Usage.do?lang=ENGLISH&compteInternet={0:s}".format(args.videotron_account)

    try:
        r = requests.get(request_url)
    except requests.exceptions.RequestException as e:
        logging.error("http call to url '{0:s}' failed ({1:s})".format(request_url, e))
        return STATE['UNKNOWN']

    if r.status_code != 200:
        logging.error("http call to url '{0:s}' failed with status '{1:d}'".format(request_url, r.status_code))
        return STATE['UNKNOWN']

    mysoup = BeautifulSoup(r.text)

    #print mysoup.prettify()

    myposition = mysoup.find(text='Period')

    myposition = myposition.findParent('tr')

    myposition = myposition.findAllNext('tr')[1]

    current_usage = float(myposition.findAllNext('td')[6].text)

    if current_usage >= args.critical_threshold:
        print "CRITICAL: Bandwidth usage is {0}Gb." \
              " This exceeds critical limit of {1}Gb".format(current_usage, args.critical_threshold)
        return STATE['CRITICAL']

    if current_usage >= args.warning_threshold:
        print "WARNING: Bandwidth usage is {0}Gb." \
              " this exceeds warning limit of {1}Gb".format(current_usage, args.warning_threshold)
        return STATE['WARNING']

    print "Bandwidth usage so far is {0}Gb".format(current_usage)
    return STATE['OK']

# try/except section for main code in order to intercept all errors and fail gracefully
if __name__ == '__main__':
    try:
        exit(main())
    except Exception as e:
        logging.error("check failed for following reason: {0}".format(e.message))
        sys.exit(STATE['UNKNOWN'])
