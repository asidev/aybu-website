#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """

"""Setup the aybu application"""

from pyramid.util import DottedNameResolver
from paste.script.command import BadCommand
from paste.script.command import Command
import ConfigParser
import os


class SetupApp(Command):

    min_args = 0
    usage = 'CONFIG_FILE'
    takes_config_file = 1
    summary = "Run the described application setup routine."
    description = """\
    This command runs the setup routine of an application 
    that uses a paste.deploy configuration file.
    """   

    parser = Command.standard_parser(verbose=True)
    """
    parser.add_option('-n', '--app-name',
                      dest='app_name',
                      metavar='NAME',
                      help="Load the named application (default main)")
    parser.add_option("-u", "--dburi",
                      action="store",
                      dest="dburi",
                      default=None,
                      help="URI for database connection")
    """

    def command(self):

        if not self.args:
            raise BadCommand('You must give a configuration file.')

        """
        if not "VIRTUAL_ENV" in os.environ:
            raise BadCommand('You cannot run this command' +\
                             'outside a virtual enviroment.')

        if self.verbose:
            logging.basicConfig(level=logging.DEBUG)

        else:
            logging.basicConfig(level=logging.WARN)

        self.log = logging.getLogger(__name__)

        self.log.debug("Setting up database")
        """

        file_name = self.args[0]
        if not file_name.startswith("/"):
            file_name = os.path.join(os.getcwd(), file_name)

        # Setup logging via the logging module's fileConfig function
        # with the specified 'config_file', if applicable.
        self.logging_file_config(file_name)

        config = ConfigParser.ConfigParser()
        config.read([file_name])

        try:
            option = config.get('commands', 'setup-app')
            # Load a callable using 'setup-app' option as fully qualified name.
            setup_app = DottedNameResolver(None).resolve(option)

        except Exception as e:

            raise ValueError('Unable to find any command ' + \
                             'to setup the application ')

        args = []

        try:

            for arg in config.get('commands',
                                  'setup-app-args').replace(' ', '').split(','):

                if not arg:
                    continue

                start = arg.find('[')
                stop = arg.find(']')

                if start >= 0 and stop >= 0:

                    section = arg[start+1:stop]
                    arg = arg[stop+1:]

                else:

                    section = None

                try:
                    args.append(config.get(section, arg))

                except Exception as e:

                    found = False
                    # Search 'arg' in all sections of the configuration file.
                    for section in config.sections():

                        for option in config.options(section):

                            if option == arg:
                                args.append(config.get(section, option))
                                found = True
                                break

                        if found:
                            break

                    if not found:
                        msg = 'Unable to find argument: %s, ' + \
                              'in the given configuration file.' % arg
                        raise ValueError(msg)

        except Exception as e:

           # Call the setup_app callable without any arguments.
           args = []

        setup_app(*args)
