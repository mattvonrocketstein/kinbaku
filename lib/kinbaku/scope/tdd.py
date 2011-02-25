""" kinbaku.scope.tdd
"""

def main():
    """ SRC: copied nearly verbatim from pythoscope.__init__.py
    """
    appname = os.path.basename(sys.argv[0])

    try:
        options, args = getopt.getopt(sys.argv[1:], "fhit:qvV",
                        ["force", "help", "init", "template=", "quiet", "verbose", "version"])
    except getopt.GetoptError, err:
        log.error("%s\n" % err)
        print USAGE % appname
        sys.exit(1)

    force = False
    init = False
    template = "unittest"

    for opt, value in options:
        if opt in ("-f", "--force"):
            force = True
        elif opt in ("-h", "--help"):
            print USAGE % appname
            sys.exit()
        elif opt in ("-i", "--init"):
            init = True
        elif opt in ("-t", "--template"):
            template = value
        elif opt in ("-q", "--quiet"):
            log.level = logger.ERROR
        elif opt in ("-v", "--verbose"):
            log.level = logger.DEBUG
        elif opt in ("-V", "--version"):
            print "%s %s" % (appname, __version__)
            sys.exit()

    try:
        if init:
            if args:
                project_path = args[0]
            else:
                project_path = "."
            init_project(project_path)
        else:
            if not args:
                log.error("You didn't specify any modules for test generation.\n")
                print USAGE % appname
            else:
                generate_tests(args, force, template)

    except KeyboardInterrupt:
        log.info("Interrupted by the user.")
    except Exception: # SystemExit gets through
        log.error("Oops, it seems that an internal Pythoscope error occurred. Please file a bug report at %s\n" % BUGTRACKER_URL)
        raise
