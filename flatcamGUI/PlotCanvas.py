# ##########################################################
# FlatCAM: 2D Post-processing for Manufacturing            #
# Author: Dennis Hayrullin (c)                             #
# Date: 2016                                               #
# MIT Licence                                              #
# ##########################################################

from PyQt5 import QtCore

import logging
from flatcamGUI.VisPyCanvas import VisPyCanvas, time, Color
from flatcamGUI.VisPyVisuals import ShapeGroup, ShapeCollection, TextCollection, TextGroup, Cursor
from vispy.scene.visuals import InfiniteLine, Line

import numpy as np
from vispy.geometry import Rect

log = logging.getLogger('base')


class PlotCanvas(QtCore.QObject, VisPyCanvas):
    """
    Class handling the plotting area in the application.
    """

    def __init__(self, container, fcapp):
        """
        The constructor configures the VisPy figure that
        will contain all plots, creates the base axes and connects
        events to the plotting area.

        :param container: The parent container in which to draw plots.
        :rtype: PlotCanvas
        """

        super(PlotCanvas, self).__init__()
        # VisPyCanvas.__init__(self)

        # VisPyCanvas does not allow new attributes. Override.
        self.unfreeze()

        self.fcapp = fcapp

        # Parent container
        self.container = container

        settings = QtCore.QSettings("Open Source", "FlatCAM")
        if settings.contains("theme"):
            theme = settings.value('theme', type=str)
        else:
            theme = 'white'

        if theme == 'white':
            self.line_color = (0.3, 0.0, 0.0, 1.0)
        else:
            self.line_color = (0.4, 0.4, 0.4, 1.0)

        # workspace lines; I didn't use the rectangle because I didn't want to add another VisPy Node,
        # which might decrease performance
        # self.b_line, self.r_line, self.t_line, self.l_line = None, None, None, None
        self.workspace_line = None

        self.pagesize_dict = dict()
        self.pagesize_dict.update(
            {
                'A0': (841, 1189),
                'A1': (594, 841),
                'A2': (420, 594),
                'A3': (297, 420),
                'A4': (210, 297),
                'A5': (148, 210),
                'A6': (105, 148),
                'A7': (74, 105),
                'A8': (52, 74),
                'A9': (37, 52),
                'A10': (26, 37),

                'B0': (1000, 1414),
                'B1': (707, 1000),
                'B2': (500, 707),
                'B3': (353, 500),
                'B4': (250, 353),
                'B5': (176, 250),
                'B6': (125, 176),
                'B7': (88, 125),
                'B8': (62, 88),
                'B9': (44, 62),
                'B10': (31, 44),

                'C0': (917, 1297),
                'C1': (648, 917),
                'C2': (458, 648),
                'C3': (324, 458),
                'C4': (229, 324),
                'C5': (162, 229),
                'C6': (114, 162),
                'C7': (81, 114),
                'C8': (57, 81),
                'C9': (40, 57),
                'C10': (28, 40),

                # American paper sizes
                'LETTER': (8.5*25.4, 11*25.4),
                'LEGAL': (8.5*25.4, 14*25.4),
                'ELEVENSEVENTEEN': (11*25.4, 17*25.4),

                # From https://en.wikipedia.org/wiki/Paper_size
                'JUNIOR_LEGAL': (5*25.4, 8*25.4),
                'HALF_LETTER': (5.5*25.4, 8*25.4),
                'GOV_LETTER': (8*25.4, 10.5*25.4),
                'GOV_LEGAL': (8.5*25.4, 13*25.4),
                'LEDGER': (17*25.4, 11*25.4),
            }
        )

        # <VisPyCanvas>
        self.create_native()
        self.native.setParent(self.fcapp.ui)

        # <QtCore.QObject>
        self.container.addWidget(self.native)

        # ## AXIS # ##
        self.v_line = InfiniteLine(pos=0, color=(0.70, 0.3, 0.3, 0.8), vertical=True,
                                   parent=self.view.scene)

        self.h_line = InfiniteLine(pos=0, color=(0.70, 0.3, 0.3, 0.8), vertical=False,
                                   parent=self.view.scene)

        # draw a rectangle made out of 4 lines on the canvas to serve as a hint for the work area
        # all CNC have a limited workspace
        if self.fcapp.defaults['global_workspace'] is True:
            self.draw_workspace(workspace_size=self.fcapp.defaults["global_workspaceT"])

        self.line_parent = None
        self.cursor_v_line = InfiniteLine(pos=None, color=self.line_color, vertical=True,
                                          parent=self.line_parent)

        self.cursor_h_line = InfiniteLine(pos=None, color=self.line_color, vertical=False,
                                          parent=self.line_parent)

        # if self.app.defaults['global_workspace'] is True:
        #     if self.app.ui.general_defaults_form.general_app_group.units_radio.get_value().upper() == 'MM':
        #         self.wkspace_t = Line(pos=)

        self.shape_collections = []

        self.shape_collection = self.new_shape_collection()
        self.fcapp.pool_recreated.connect(self.on_pool_recreated)
        self.text_collection = self.new_text_collection()

        # TODO: Should be setting to show/hide CNC job annotations (global or per object)
        self.text_collection.enabled = True

        self.c = None
        self.big_cursor = None
        # Keep VisPy canvas happy by letting it be "frozen" again.
        self.freeze()

        self.graph_event_connect('mouse_wheel', self.on_mouse_scroll)

    def draw_workspace(self, workspace_size):
        """
        Draw a rectangular shape on canvas to specify our valid workspace.
        :param workspace_size: the workspace size; tuple
        :return:
        """
        try:
            if self.fcapp.defaults['units'].upper() == 'MM':
                dims = self.pagesize_dict[workspace_size]
            else:
                dims = (self.pagesize_dict[workspace_size][0]/25.4, self.pagesize_dict[workspace_size][1]/25.4)
        except Exception as e:
            log.debug("PlotCanvas.draw_workspace() --> %s" % str(e))
            return

        if self.fcapp.defaults['global_workspace_orientation'] == 'l':
            dims = (dims[1], dims[0])

        a = np.array([(0, 0), (dims[0], 0), (dims[0], dims[1]), (0, dims[1])])

        if not self.workspace_line:
            self.workspace_line = Line(pos=np.array((a[0], a[1], a[2], a[3], a[0])), color=(0.70, 0.3, 0.3, 0.7),
                                       antialias=True, method='agg', parent=self.view.scene)
        else:
            self.workspace_line.parent = self.view.scene

    def delete_workspace(self):
        try:
            self.workspace_line.parent = None
        except Exception:
            pass

    # redraw the workspace lines on the plot by re adding them to the parent view.scene
    def restore_workspace(self):
        try:
            self.workspace_line.parent = self.view.scene
        except Exception:
            pass

    def graph_event_connect(self, event_name, callback):
        return getattr(self.events, event_name).connect(callback)

    def graph_event_disconnect(self, event_name, callback=None):
        if callback is None:
            getattr(self.events, event_name).disconnect()
        else:
            getattr(self.events, event_name).disconnect(callback)

    def zoom(self, factor, center=None):
        """
        Zooms the plot by factor around a given
        center point. Takes care of re-drawing.

        :param factor: Number by which to scale the plot.
        :type factor: float
        :param center: Coordinates [x, y] of the point around which to scale the plot.
        :type center: list
        :return: None
        """
        self.view.camera.zoom(factor, center)

    def new_shape_group(self, shape_collection=None):
        if shape_collection:
            return ShapeGroup(shape_collection)
        return ShapeGroup(self.shape_collection)

    def new_shape_collection(self, **kwargs):
        # sc = ShapeCollection(parent=self.view.scene, pool=self.app.pool, **kwargs)
        # self.shape_collections.append(sc)
        # return sc
        return ShapeCollection(parent=self.view.scene, pool=self.fcapp.pool, **kwargs)

    def new_cursor(self, big=None):
        """
        Will create a mouse cursor pointer on canvas

        :param big: if True will create a mouse cursor made out of infinite lines
        :return: the mouse cursor object
        """
        if big is True:
            self.big_cursor = True
            self.c = CursorBig()

            # in case there are multiple new_cursor calls, best to disconnect first the signals
            try:
                self.c.mouse_state_updated.disconnect(self.on_mouse_state)
            except (TypeError, AttributeError):
                pass
            try:
                self.c.mouse_position_updated.disconnect(self.on_mouse_position)
            except (TypeError, AttributeError):
                pass

            self.c.mouse_state_updated.connect(self.on_mouse_state)
            self.c.mouse_position_updated.connect(self.on_mouse_position)
        else:
            self.big_cursor = False
            self.c = Cursor(pos=np.empty((0, 2)), parent=self.view.scene)
            self.c.antialias = 0

        return self.c

    def on_mouse_state(self, state):
        if state:
            self.cursor_h_line.parent = self.view.scene
            self.cursor_v_line.parent = self.view.scene
        else:
            self.cursor_h_line.parent = None
            self.cursor_v_line.parent = None

    def on_mouse_position(self, pos):
        # self.line_color = color

        self.cursor_h_line.set_data(pos=pos[1], color=self.line_color)
        self.cursor_v_line.set_data(pos=pos[0], color=self.line_color)
        self.view.scene.update()

    def on_mouse_scroll(self, event):
        # key modifiers
        modifiers = event.modifiers
        pan_delta_x = self.fcapp.defaults["global_gridx"]
        pan_delta_y = self.fcapp.defaults["global_gridy"]
        curr_pos = event.pos

        # Controlled pan by mouse wheel
        if 'Shift' in modifiers:
            p1 = np.array(curr_pos)[:2]

            if event.delta[1] > 0:
                curr_pos[0] -= pan_delta_x
            else:
                curr_pos[0] += pan_delta_x
            p2 = np.array(curr_pos)[:2]
            self.view.camera.pan(p2 - p1)
        elif 'Control' in modifiers:
            p1 = np.array(curr_pos)[:2]

            if event.delta[1] > 0:
                curr_pos[1] += pan_delta_y
            else:
                curr_pos[1] -= pan_delta_y
            p2 = np.array(curr_pos)[:2]
            self.view.camera.pan(p2 - p1)

        if self.fcapp.grid_status() == True:
            pos_canvas = self.translate_coords(curr_pos)
            pos = self.fcapp.geo_editor.snap(pos_canvas[0], pos_canvas[1])

            # Update cursor
            self.fcapp.app_cursor.set_data(np.asarray([(pos[0], pos[1])]),
                                           symbol='++', edge_color=self.fcapp.cursor_color_3D,
                                           size=self.fcapp.defaults["global_cursor_size"])

    def new_text_group(self, collection=None):
        if collection:
            return TextGroup(collection)
        else:
            return TextGroup(self.text_collection)

    def new_text_collection(self, **kwargs):
        return TextCollection(parent=self.view.scene, **kwargs)

    def fit_view(self, rect=None):

        # Lock updates in other threads
        self.shape_collection.lock_updates()

        if not rect:
            rect = Rect(-1, -1, 20, 20)
            try:
                rect.left, rect.right = self.shape_collection.bounds(axis=0)
                rect.bottom, rect.top = self.shape_collection.bounds(axis=1)
            except TypeError:
                pass

        # adjust the view camera to be slightly bigger than the bounds so the shape colleaction can be seen clearly
        # otherwise the shape collection boundary will have no border
        rect.left *= 0.96
        rect.bottom *= 0.96
        rect.right *= 1.01
        rect.top *= 1.01

        self.view.camera.rect = rect

        self.shape_collection.unlock_updates()

    def fit_center(self, loc, rect=None):

        # Lock updates in other threads
        self.shape_collection.lock_updates()

        if not rect:
            try:
                rect = Rect(loc[0]-20, loc[1]-20, 40, 40)
            except TypeError:
                pass

        self.view.camera.rect = rect

        self.shape_collection.unlock_updates()

    def clear(self):
        pass

    def redraw(self):
        self.shape_collection.redraw([])
        self.text_collection.redraw()

    def on_pool_recreated(self, pool):
        self.shape_collection.pool = pool


class CursorBig(QtCore.QObject):
    """
    This is a fake cursor to ensure compatibility with the OpenGL engine (VisPy).
    This way I don't have to chane (disable) things related to the cursor all over when
    using the low performance Matplotlib 2D graphic engine.
    """

    mouse_state_updated = QtCore.pyqtSignal(bool)
    mouse_position_updated = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self._enabled = None

    @property
    def enabled(self):
        return True if self._enabled else False

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        self.mouse_state_updated.emit(value)

    def set_data(self, pos, **kwargs):
        """Internal event handler to draw the cursor when the mouse moves."""
        if 'edge_color' in kwargs:
            color = kwargs['edge_color']
        else:
            if self.app.defaults['global_theme'] == 'white':
                color = '#000000FF'
            else:
                color = '#FFFFFFFF'

        position = [pos[0][0], pos[0][1]]
        self.mouse_position_updated.emit(position)
