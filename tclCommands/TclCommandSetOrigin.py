# ##########################################################
# FlatCAM: 2D Post-processing for Manufacturing            #
# File Author: Marius Adrian Stanciu (c)                   #
# Date: 8/17/2019                                          #
# MIT Licence                                              #
# ##########################################################

from tclCommands.TclCommand import TclCommand
from ObjectCollection import *

from camlib import get_bounds

import gettext
import FlatCAMTranslation as fcTranslate
import builtins

fcTranslate.apply_language('strings')
if '_' not in builtins.__dict__:
    _ = gettext.gettext


class TclCommandSetOrigin(TclCommand):
    """
    Tcl shell command to set the origin to zero or to a specified location for all loaded objects in FlatCAM.

    example:

    """

    # List of all command aliases, to be able use old names for backward compatibility (add_poly, add_polygon)
    aliases = ['set_origin', 'origin']

    # Dictionary of types from Tcl command, needs to be ordered
    arg_names = collections.OrderedDict([
        ('loc', str)
    ])

    # Dictionary of types from Tcl command, needs to be ordered , this  is  for options  like -optionname value
    option_types = collections.OrderedDict([
        ('auto', bool)
    ])

    # array of mandatory options for current Tcl command: required = {'name','outname'}
    required = []

    # structured help for current command, args needs to be ordered
    help = {
        'main': "Will set the origin at the specified x,y location.",
        'args': collections.OrderedDict([
            ('loc', 'Location to offset all the selected objects. No spaces between x and y pair. Use like this: 2,3'),
            ('auto', 'If set to 1 it will set the origin to the minimum x, y of the object selection bounding box.'
                     '-auto=1 is not correct but -auto 1 or -auto True is correct.')
        ]),
        'examples': ['set_origin 3,2', 'set_origin -auto 1']
    }

    def execute(self, args, unnamed_args):
        """

        :param args:
        :param unnamed_args:
        :return:
        """

        loc = list()
        if 'auto' in args:
            if args['auto'] == 1:
                objs = self.app.collection.get_list()
                minx, miny, __, ___ = get_bounds(objs)

                loc.append(0 - minx)
                loc.append(0 - miny)
            else:
                loc = [0, 0]
        elif 'loc' in args:
            try:
                location = [float(eval(coord)) for coord in str(args['loc']).split(",") if coord != '']
            except AttributeError as e:
                log.debug("TclCommandSetOrigin.execute --> %s" % str(e))
                location = (0, 0)

            loc.append(location[0])
            loc.append(location[1])

            if len(location) != 2:
                self.raise_tcl_error('%s: %s' % (
                    _("Expected a pair of (x, y) coordinates. Got"), str(len(location))))
                return 'fail'
        else:
            loc = [0, 0]

        self.app.on_set_zero_click(event=None, location=loc, noplot=True, use_thread=False)
        self.app.inform.emit('[success] Tcl %s: %s' %
                             (_('Origin set by offsetting all loaded objects with '),
                              '{0:.4f}, {0:.4f}'.format(loc[0], loc[1])))