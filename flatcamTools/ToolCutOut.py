from FlatCAMTool import FlatCAMTool
from ObjectCollection import *
from FlatCAMApp import *


class CutOut(FlatCAMTool):

    toolName = "Cutout PCB"

    def __init__(self, app):
        FlatCAMTool.__init__(self, app)

        ## Title
        title_label = QtWidgets.QLabel("%s" % self.toolName)
        title_label.setStyleSheet("""
                        QLabel
                        {
                            font-size: 16px;
                            font-weight: bold;
                        }
                        """)
        self.layout.addWidget(title_label)

        ## Form Layout
        form_layout = QtWidgets.QFormLayout()
        self.layout.addLayout(form_layout)

        ## Type of object to be cutout
        self.type_obj_combo = QtWidgets.QComboBox()
        self.type_obj_combo.addItem("Gerber")
        self.type_obj_combo.addItem("Excellon")
        self.type_obj_combo.addItem("Geometry")

        # we get rid of item1 ("Excellon") as it is not suitable for creating film
        self.type_obj_combo.view().setRowHidden(1, True)
        self.type_obj_combo.setItemIcon(0, QtGui.QIcon("share/flatcam_icon16.png"))
        # self.type_obj_combo.setItemIcon(1, QtGui.QIcon("share/drill16.png"))
        self.type_obj_combo.setItemIcon(2, QtGui.QIcon("share/geometry16.png"))

        self.type_obj_combo_label = QtWidgets.QLabel("Obj Type:")
        self.type_obj_combo_label.setToolTip(
            "Specify the type of object to be cutout.\n"
            "It can be of type: Gerber or Geometry.\n"
            "What is selected here will dictate the kind\n"
            "of objects that will populate the 'Object' combobox."
        )
        form_layout.addRow(self.type_obj_combo_label, self.type_obj_combo)

        ## Object to be cutout
        self.obj_combo = QtWidgets.QComboBox()
        self.obj_combo.setModel(self.app.collection)
        self.obj_combo.setRootModelIndex(self.app.collection.index(0, 0, QtCore.QModelIndex()))
        self.obj_combo.setCurrentIndex(1)

        self.object_label = QtWidgets.QLabel("Object:")
        self.object_label.setToolTip(
            "Object to be cutout.                        "
        )
        form_layout.addRow(self.object_label, self.obj_combo)

        ## Title2
        title_param_label = QtWidgets.QLabel("<font size=4><b>A. Automatic Cutout</b></font>")
        self.layout.addWidget(title_param_label)

        ## Form Layout
        form_layout_2 = QtWidgets.QFormLayout()
        self.layout.addLayout(form_layout_2)

        # Tool Diameter
        self.dia = FCEntry()
        self.dia_label = QtWidgets.QLabel("Tool Dia:")
        self.dia_label.setToolTip(
            "Diameter of the tool used to cutout\n"
            "the PCB shape out of the surrounding material."
        )
        form_layout_2.addRow(self.dia_label, self.dia)

        # Margin
        self.margin = FCEntry()
        self.margin_label = QtWidgets.QLabel("Margin:")
        self.margin_label.setToolTip(
            "Margin over bounds. A positive value here\n"
            "will make the cutout of the PCB further from\n"
            "the actual PCB border"
        )
        form_layout_2.addRow(self.margin_label, self.margin)

        # Gapsize
        self.gapsize = FCEntry()
        self.gapsize_label = QtWidgets.QLabel("Gap size:")
        self.gapsize_label.setToolTip(
            "The size of the gaps in the cutout\n"
            "used to keep the board connected to\n"
            "the surrounding material (the one \n"
            "from which the PCB is cutout)."
        )
        form_layout_2.addRow(self.gapsize_label, self.gapsize)

        ## Title3
        title_ff_label = QtWidgets.QLabel("<b>FreeForm Cutout</b>")
        self.layout.addWidget(title_ff_label)

        ## Form Layout
        form_layout_3 = QtWidgets.QFormLayout()
        self.layout.addLayout(form_layout_3)

        # How gaps wil be rendered:
        # lr    - left + right
        # tb    - top + bottom
        # 4     - left + right +top + bottom
        # 2lr   - 2*left + 2*right
        # 2tb   - 2*top + 2*bottom
        # 8     - 2*left + 2*right +2*top + 2*bottom

        # Gaps
        gaps_ff_label = QtWidgets.QLabel('Gaps FF:      ')
        gaps_ff_label.setToolTip(
            "Number of gaps used for the FreeForm cutout.\n"
            "There can be maximum 8 bridges/gaps.\n"
            "The choices are:\n"
            "- lr    - left + right\n"
            "- tb    - top + bottom\n"
            "- 4     - left + right +top + bottom\n"
            "- 2lr   - 2*left + 2*right\n"
            "- 2tb  - 2*top + 2*bottom\n"
            "- 8     - 2*left + 2*right +2*top + 2*bottom"
        )

        self.gaps = FCComboBox()
        gaps_items = ['LR', 'TB', '4', '2LR', '2TB', '8']
        for it in gaps_items:
            self.gaps.addItem(it)
            self.gaps.setStyleSheet('background-color: rgb(255,255,255)')
        form_layout_3.addRow(gaps_ff_label, self.gaps)

        ## Buttons
        hlay = QtWidgets.QHBoxLayout()
        self.layout.addLayout(hlay)

        hlay.addStretch()
        self.ff_cutout_object_btn = QtWidgets.QPushButton("  FreeForm Cutout Object ")
        self.ff_cutout_object_btn.setToolTip(
            "Cutout the selected object.\n"
            "The cutout shape can be any shape.\n"
            "Useful when the PCB has a non-rectangular shape.\n"
            "But if the object to be cutout is of Gerber Type,\n"
            "it needs to be an outline of the actual board shape."
        )
        hlay.addWidget(self.ff_cutout_object_btn)

        ## Title4
        title_rct_label = QtWidgets.QLabel("<b>Rectangular Cutout</b>")
        self.layout.addWidget(title_rct_label)

        ## Form Layout
        form_layout_4 = QtWidgets.QFormLayout()
        self.layout.addLayout(form_layout_4)

        gapslabel_rect = QtWidgets.QLabel('Type of gaps:')
        gapslabel_rect.setToolTip(
            "Where to place the gaps:\n"
            "- one gap Top / one gap Bottom\n"
            "- one gap Left / one gap Right\n"
            "- one gap on each of the 4 sides."
        )
        self.gaps_rect_radio = RadioSet([{'label': '2(T/B)', 'value': 'TB'},
                                    {'label': '2(L/R)', 'value': 'LR'},
                                    {'label': '4', 'value': '4'}])
        form_layout_4.addRow(gapslabel_rect, self.gaps_rect_radio)

        hlay2 = QtWidgets.QHBoxLayout()
        self.layout.addLayout(hlay2)

        hlay2.addStretch()
        self.rect_cutout_object_btn = QtWidgets.QPushButton("Rectangular Cutout Object")
        self.rect_cutout_object_btn.setToolTip(
            "Cutout the selected object.\n"
            "The resulting cutout shape is\n"
            "always of a rectangle form and it will be\n"
            "the bounding box of the Object."
        )
        hlay2.addWidget(self.rect_cutout_object_btn)

        ## Title5
        title_manual_label = QtWidgets.QLabel("<font size=4><b>B. Manual Cutout</b></font>")
        self.layout.addWidget(title_manual_label)

        ## Form Layout
        form_layout_5 = QtWidgets.QFormLayout()
        self.layout.addLayout(form_layout_4)

        self.layout.addStretch()

        ## Init GUI
        # self.dia.set_value(1)
        # self.margin.set_value(0)
        # self.gapsize.set_value(1)
        # self.gaps.set_value(4)
        # self.gaps_rect_radio.set_value("4")

        ## Signals
        self.ff_cutout_object_btn.clicked.connect(self.on_freeform_cutout)
        self.rect_cutout_object_btn.clicked.connect(self.on_rectangular_cutout)

        self.type_obj_combo.currentIndexChanged.connect(self.on_type_obj_index_changed)

    def on_type_obj_index_changed(self, index):
        obj_type = self.type_obj_combo.currentIndex()
        self.obj_combo.setRootModelIndex(self.app.collection.index(obj_type, 0, QtCore.QModelIndex()))
        self.obj_combo.setCurrentIndex(0)

    def run(self):
        self.app.report_usage("ToolCutOut()")

        # if the splitter is hidden, display it, else hide it but only if the current widget is the same
        if self.app.ui.splitter.sizes()[0] == 0:
            self.app.ui.splitter.setSizes([1, 1])
        else:
            try:
                if self.app.ui.tool_scroll_area.widget().objectName() == self.toolName:
                    self.app.ui.splitter.setSizes([0, 1])
            except AttributeError:
                pass
        FlatCAMTool.run(self)
        self.set_tool_ui()

        self.app.ui.notebook.setTabText(2, "Cutout Tool")

    def install(self, icon=None, separator=None, **kwargs):
        FlatCAMTool.install(self, icon, separator, shortcut='ALT+U', **kwargs)

    def set_tool_ui(self):
        self.reset_fields()

        self.dia.set_value(float(self.app.defaults["tools_cutouttooldia"]))
        self.margin.set_value(float(self.app.defaults["tools_cutoutmargin"]))
        self.gapsize.set_value(float(self.app.defaults["tools_cutoutgapsize"]))
        self.gaps.set_value(4)
        self.gaps_rect_radio.set_value(str(self.app.defaults["tools_gaps_rect"]))

    def on_freeform_cutout(self):

        def subtract_rectangle(obj_, x0, y0, x1, y1):
            pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            obj_.subtract_polygon(pts)

        name = self.obj_combo.currentText()

        # Get source object.
        try:
            cutout_obj = self.app.collection.get_by_name(str(name))
        except:
            self.app.inform.emit("[ERROR_NOTCL]Could not retrieve object: %s" % name)
            return "Could not retrieve object: %s" % name

        if cutout_obj is None:
            self.app.inform.emit("[ERROR_NOTCL]There is no object selected for Cutout.\nSelect one and try again.")
            return

        try:
            dia = float(self.dia.get_value())
        except ValueError:
            # try to convert comma to decimal point. if it's still not working error message and return
            try:
                dia = float(self.dia.get_value().replace(',', '.'))
            except ValueError:
                self.app.inform.emit("[WARNING_NOTCL] Tool diameter value is missing or wrong format. "
                                     "Add it and retry.")
                return

        try:
            margin = float(self.margin.get_value())
        except ValueError:
            # try to convert comma to decimal point. if it's still not working error message and return
            try:
                margin = float(self.margin.get_value().replace(',', '.'))
            except ValueError:
                self.app.inform.emit("[WARNING_NOTCL] Margin value is missing or wrong format. "
                                     "Add it and retry.")
                return

        try:
            gapsize = float(self.gapsize.get_value())
        except ValueError:
            # try to convert comma to decimal point. if it's still not working error message and return
            try:
                gapsize = float(self.gapsize.get_value().replace(',', '.'))
            except ValueError:
                self.app.inform.emit("[WARNING_NOTCL] Gap size value is missing or wrong format. "
                                     "Add it and retry.")
                return

        try:
            gaps = self.gaps.get_value()
        except TypeError:
            self.app.inform.emit("[WARNING_NOTCL] Number of gaps value is missing. Add it and retry.")
            return

        if 0 in {dia}:
            self.app.inform.emit("[WARNING_NOTCL]Tool Diameter is zero value. Change it to a positive integer.")
            return "Tool Diameter is zero value. Change it to a positive integer."

        if gaps not in ['LR', 'TB', '2LR', '2TB', '4', '8']:
            self.app.inform.emit("[WARNING_NOTCL] Gaps value can be only one of: 'lr', 'tb', '2lr', '2tb', 4 or 8. "
                                 "Fill in a correct value and retry. ")
            return

        if cutout_obj.multigeo is True:
            self.app.inform.emit("[ERROR]Cutout operation cannot be done on a multi-geo Geometry.\n"
                                 "Optionally, this Multi-geo Geometry can be converted to Single-geo Geometry,\n"
                                 "and after that perform Cutout.")
            return

        # Get min and max data for each object as we just cut rectangles across X or Y
        xmin, ymin, xmax, ymax = cutout_obj.bounds()
        px = 0.5 * (xmin + xmax) + margin
        py = 0.5 * (ymin + ymax) + margin
        lenghtx = (xmax - xmin) + (margin * 2)
        lenghty = (ymax - ymin) + (margin * 2)

        gapsize = gapsize / 2 + (dia / 2)

        if isinstance(cutout_obj,FlatCAMGeometry):
            # rename the obj name so it can be identified as cutout
            cutout_obj.options["name"] += "_cutout"
        else:
            def geo_init(geo_obj, app_obj):
                geo = cutout_obj.solid_geometry.convex_hull
                geo_obj.solid_geometry = geo.buffer(margin + abs(dia / 2))

            outname = cutout_obj.options["name"] + "_cutout"
            self.app.new_object('geometry', outname, geo_init)

            cutout_obj = self.app.collection.get_by_name(outname)

        if gaps == '8' or gaps == '2LR':
            subtract_rectangle(cutout_obj,
                               xmin - gapsize,  # botleft_x
                               py - gapsize + lenghty / 4,  # botleft_y
                               xmax + gapsize,  # topright_x
                               py + gapsize + lenghty / 4)  # topright_y
            subtract_rectangle(cutout_obj,
                               xmin - gapsize,
                               py - gapsize - lenghty / 4,
                               xmax + gapsize,
                               py + gapsize - lenghty / 4)

        if gaps == '8' or gaps == '2TB':
            subtract_rectangle(cutout_obj,
                               px - gapsize + lenghtx / 4,
                               ymin - gapsize,
                               px + gapsize + lenghtx / 4,
                               ymax + gapsize)
            subtract_rectangle(cutout_obj,
                               px - gapsize - lenghtx / 4,
                               ymin - gapsize,
                               px + gapsize - lenghtx / 4,
                               ymax + gapsize)

        if gaps == '4' or gaps == 'LR':
            subtract_rectangle(cutout_obj,
                               xmin - gapsize,
                               py - gapsize,
                               xmax + gapsize,
                               py + gapsize)

        if gaps == '4' or gaps == 'TB':
            subtract_rectangle(cutout_obj,
                               px - gapsize,
                               ymin - gapsize,
                               px + gapsize,
                               ymax + gapsize)

        cutout_obj.plot()
        self.app.inform.emit("[success] Any form CutOut operation finished.")
        self.app.ui.notebook.setCurrentWidget(self.app.ui.project_tab)
        self.app.should_we_save = True

    def on_rectangular_cutout(self):
        name = self.obj_combo.currentText()

        # Get source object.
        try:
            cutout_obj = self.app.collection.get_by_name(str(name))
        except:
            self.app.inform.emit("[ERROR_NOTCL]Could not retrieve object: %s" % name)
            return "Could not retrieve object: %s" % name

        if cutout_obj is None:
            self.app.inform.emit("[ERROR_NOTCL]Object not found: %s" % cutout_obj)

        try:
            dia = float(self.dia.get_value())
        except ValueError:
            # try to convert comma to decimal point. if it's still not working error message and return
            try:
                dia = float(self.dia.get_value().replace(',', '.'))
            except ValueError:
                self.app.inform.emit("[WARNING_NOTCL] Tool diameter value is missing or wrong format. "
                                     "Add it and retry.")
                return

        try:
            margin = float(self.margin.get_value())
        except ValueError:
            # try to convert comma to decimal point. if it's still not working error message and return
            try:
                margin = float(self.margin.get_value().replace(',', '.'))
            except ValueError:
                self.app.inform.emit("[WARNING_NOTCL] Margin value is missing or wrong format. "
                                     "Add it and retry.")
                return

        try:
            gapsize = float(self.gapsize.get_value())
        except ValueError:
            # try to convert comma to decimal point. if it's still not working error message and return
            try:
                gapsize = float(self.gapsize.get_value().replace(',', '.'))
            except ValueError:
                self.app.inform.emit("[WARNING_NOTCL] Gap size value is missing or wrong format. "
                                     "Add it and retry.")
                return

        try:
            gaps = self.gaps_rect_radio.get_value()
        except TypeError:
            self.app.inform.emit("[WARNING_NOTCL] Number of gaps value is missing. Add it and retry.")
            return

        if 0 in {dia}:
            self.app.inform.emit("[ERROR_NOTCL]Tool Diameter is zero value. Change it to a positive integer.")
            return "Tool Diameter is zero value. Change it to a positive integer."

        if cutout_obj.multigeo is True:
            self.app.inform.emit("[ERROR]Cutout operation cannot be done on a multi-geo Geometry.\n"
                                 "Optionally, this Multi-geo Geometry can be converted to Single-geo Geometry,\n"
                                 "and after that perform Cutout.")
            return

        def geo_init(geo_obj, app_obj):
            real_margin = margin + (dia / 2)
            real_gap_size = gapsize + dia

            minx, miny, maxx, maxy = cutout_obj.bounds()
            minx -= real_margin
            maxx += real_margin
            miny -= real_margin
            maxy += real_margin
            midx = 0.5 * (minx + maxx)
            midy = 0.5 * (miny + maxy)
            hgap = 0.5 * real_gap_size
            pts = [[midx - hgap, maxy],
                   [minx, maxy],
                   [minx, midy + hgap],
                   [minx, midy - hgap],
                   [minx, miny],
                   [midx - hgap, miny],
                   [midx + hgap, miny],
                   [maxx, miny],
                   [maxx, midy - hgap],
                   [maxx, midy + hgap],
                   [maxx, maxy],
                   [midx + hgap, maxy]]
            cases = {"TB": [[pts[0], pts[1], pts[4], pts[5]],
                            [pts[6], pts[7], pts[10], pts[11]]],
                     "LR": [[pts[9], pts[10], pts[1], pts[2]],
                            [pts[3], pts[4], pts[7], pts[8]]],
                     "4": [[pts[0], pts[1], pts[2]],
                           [pts[3], pts[4], pts[5]],
                           [pts[6], pts[7], pts[8]],
                           [pts[9], pts[10], pts[11]]]}
            cuts = cases[gaps]
            geo_obj.solid_geometry = cascaded_union([LineString(segment) for segment in cuts])

        # TODO: Check for None
        self.app.new_object("geometry", name + "_cutout", geo_init)
        self.app.inform.emit("[success] Rectangular CutOut operation finished.")
        self.app.ui.notebook.setCurrentWidget(self.app.ui.project_tab)

    def reset_fields(self):
        self.obj_combo.setRootModelIndex(self.app.collection.index(0, 0, QtCore.QModelIndex()))
