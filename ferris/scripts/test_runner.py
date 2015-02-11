#!/usr/bin/env python2.7
import sys
import argparse
import os
import re
import logging

# Fix the path
base_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..', '..'))

sys.path.insert(0, base_dir)


def bootstrap(sdk_path):
    sys.path.insert(0, sdk_path)

    # Force the google module to reload, for some reason on windows this can sometimes point to the one in site-packages.
    import google
    reload(google)

    import dev_appserver
    dev_appserver.fix_sys_path()
    sys.path = [re.sub('webob_0_9', 'webob_1_1_1', x) for x in sys.path]

    import fix_imports
    (fix_imports)

    # Activate a testbed so that httplib2 always knows that it's in app engine
    from google.appengine.ext import testbed
    testbed = testbed.Testbed()
    testbed.activate()
    testbed.init_urlfetch_stub()

    # Remove agressive logging
    rootLogger = logging.getLogger()
    for handler in rootLogger.handlers:
        if isinstance(handler, logging.StreamHandler):
            rootLogger.removeHandler(handler)


def main(sdk_path, package, coverage=False):
    test_path = os.path.join(base_dir, package, 'tests')

    bootstrap(sdk_path)

    import nose

    argv = [
        sys.argv[0],
        '-v',
        '--logging-level=WARNING',
        test_path
    ]

    if coverage:
        argv += [
            '--with-coverage',
            '--cover-package=%s' % package.replace(os.sep, '.'),
        ]

    nose.main(argv=argv)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='The path in which to search for tests. Using ferris or app will automatically run tests for Ferris or your app respectively. Passing in anything else will just use that path exactly.')
    parser.add_argument('--sdk', help='The path to the SDK. Optional if you\'ve set the APPENGINE_SDK_PATH environment variable or if it\'s installed at ~/bin/google_appengine')
    parser.add_argument('--coverage', help='Enable test coverage', action="store_true")
    args = parser.parse_args()

    if not args.sdk:
        args.sdk = os.environ.get('APPENGINE_SDK_PATH', None)
        if not args.sdk:
            default_path = os.path.expanduser('~/bin/google_appengine')
            if os.path.exists(default_path):
                args.sdk = default_path

    if not args.sdk:
        print 'Error: No sdk path provided, see the --sdk option.'
        parser.print_help()
        sys.exit(1)

    main(args.sdk, args.path, args.coverage)
