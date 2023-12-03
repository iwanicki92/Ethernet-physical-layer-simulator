# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rs_register_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_rsRegisterForm(object):
    def setupUi(self, rsRegisterForm):
        rsRegisterForm.setObjectName("rsRegisterForm")
        rsRegisterForm.resize(820, 651)
        rsRegisterForm.setBaseSize(QtCore.QSize(0, 0))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(rsRegisterForm)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.imageLabel = QtWidgets.QLabel(rsRegisterForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageLabel.sizePolicy().hasHeightForWidth())
        self.imageLabel.setSizePolicy(sizePolicy)
        self.imageLabel.setMaximumSize(QtCore.QSize(1000, 500))
        self.imageLabel.setSizeIncrement(QtCore.QSize(0, 0))
        self.imageLabel.setBaseSize(QtCore.QSize(0, 0))
        self.imageLabel.setText("")
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setObjectName("imageLabel")
        self.verticalLayout.addWidget(self.imageLabel)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 20, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(10, 10, 10, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.standardsComboBox = QtWidgets.QComboBox(rsRegisterForm)
        self.standardsComboBox.setObjectName("standardsComboBox")
        self.verticalLayout_2.addWidget(self.standardsComboBox)
        self.poly_repr_checkBox = QtWidgets.QCheckBox(rsRegisterForm)
        self.poly_repr_checkBox.setChecked(False)
        self.poly_repr_checkBox.setObjectName("poly_repr_checkBox")
        self.verticalLayout_2.addWidget(self.poly_repr_checkBox)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(5, -1, -1, 15)
        self.formLayout.setVerticalSpacing(6)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(rsRegisterForm)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.rs_n_spinBox = QtWidgets.QSpinBox(rsRegisterForm)
        self.rs_n_spinBox.setMinimum(2)
        self.rs_n_spinBox.setMaximum(10000)
        self.rs_n_spinBox.setObjectName("rs_n_spinBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.rs_n_spinBox)
        self.label_2 = QtWidgets.QLabel(rsRegisterForm)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.rs_k_spinBox = QtWidgets.QSpinBox(rsRegisterForm)
        self.rs_k_spinBox.setMinimum(2)
        self.rs_k_spinBox.setMaximum(10000)
        self.rs_k_spinBox.setObjectName("rs_k_spinBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.rs_k_spinBox)
        self.label_3 = QtWidgets.QLabel(rsRegisterForm)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.rs_gf_spinBox = QtWidgets.QSpinBox(rsRegisterForm)
        self.rs_gf_spinBox.setMinimum(2)
        self.rs_gf_spinBox.setMaximum(18)
        self.rs_gf_spinBox.setObjectName("rs_gf_spinBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.rs_gf_spinBox)
        self.label_4 = QtWidgets.QLabel(rsRegisterForm)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.rs_primitive_poly_lineEdit = QtWidgets.QLineEdit(rsRegisterForm)
        self.rs_primitive_poly_lineEdit.setObjectName("rs_primitive_poly_lineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.rs_primitive_poly_lineEdit)
        self.label_5 = QtWidgets.QLabel(rsRegisterForm)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.rs_primitive_element_lineEdit = QtWidgets.QLineEdit(rsRegisterForm)
        self.rs_primitive_element_lineEdit.setObjectName("rs_primitive_element_lineEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.rs_primitive_element_lineEdit)
        self.label_11 = QtWidgets.QLabel(rsRegisterForm)
        self.label_11.setObjectName("label_11")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.gen_poly_lineEdit = QtWidgets.QLineEdit(rsRegisterForm)
        self.gen_poly_lineEdit.setReadOnly(True)
        self.gen_poly_lineEdit.setObjectName("gen_poly_lineEdit")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.gen_poly_lineEdit)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, -1, -1, 10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.calculate_gen_poly_pushButton = QtWidgets.QPushButton(rsRegisterForm)
        self.calculate_gen_poly_pushButton.setObjectName("calculate_gen_poly_pushButton")
        self.horizontalLayout_3.addWidget(self.calculate_gen_poly_pushButton)
        self.calculate_primitives_pushButton = QtWidgets.QPushButton(rsRegisterForm)
        self.calculate_primitives_pushButton.setObjectName("calculate_primitives_pushButton")
        self.horizontalLayout_3.addWidget(self.calculate_primitives_pushButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(10, 10, 10, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setContentsMargins(-1, -1, 10, -1)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_6 = QtWidgets.QLabel(rsRegisterForm)
        self.label_6.setObjectName("label_6")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.lineEdit = QtWidgets.QLineEdit(rsRegisterForm)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.label_7 = QtWidgets.QLabel(rsRegisterForm)
        self.label_7.setObjectName("label_7")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.lineEdit_2 = QtWidgets.QLineEdit(rsRegisterForm)
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_2)
        self.label_8 = QtWidgets.QLabel(rsRegisterForm)
        self.label_8.setObjectName("label_8")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.spinBox = QtWidgets.QSpinBox(rsRegisterForm)
        self.spinBox.setMaximum(1)
        self.spinBox.setObjectName("spinBox")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.spinBox)
        self.label_9 = QtWidgets.QLabel(rsRegisterForm)
        self.label_9.setObjectName("label_9")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.spinBox_2 = QtWidgets.QSpinBox(rsRegisterForm)
        self.spinBox_2.setMinimum(1)
        self.spinBox_2.setMaximum(1000)
        self.spinBox_2.setObjectName("spinBox_2")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.spinBox_2)
        self.verticalLayout_3.addLayout(self.formLayout_2)
        self.label_10 = QtWidgets.QLabel(rsRegisterForm)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_3.addWidget(self.label_10)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.next_symbol_pushButton = QtWidgets.QPushButton(rsRegisterForm)
        self.next_symbol_pushButton.setObjectName("next_symbol_pushButton")
        self.horizontalLayout_5.addWidget(self.next_symbol_pushButton)
        self.next_x_symbols_pushButton = QtWidgets.QPushButton(rsRegisterForm)
        self.next_x_symbols_pushButton.setObjectName("next_x_symbols_pushButton")
        self.horizontalLayout_5.addWidget(self.next_x_symbols_pushButton)
        self.whole_message_pushButton = QtWidgets.QPushButton(rsRegisterForm)
        self.whole_message_pushButton.setObjectName("whole_message_pushButton")
        self.horizontalLayout_5.addWidget(self.whole_message_pushButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.scrollArea = QtWidgets.QScrollArea(rsRegisterForm)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 301, 74))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scroll_horizontalLayout = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.scroll_horizontalLayout.setObjectName("scroll_horizontalLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem4)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(rsRegisterForm)
        self.standardsComboBox.currentTextChanged['QString'].connect(rsRegisterForm.comboBoxChanged) # type: ignore
        self.calculate_primitives_pushButton.clicked.connect(rsRegisterForm.calculate_primitives) # type: ignore
        self.next_symbol_pushButton.clicked.connect(rsRegisterForm.next_symbol) # type: ignore
        self.next_x_symbols_pushButton.clicked.connect(rsRegisterForm.next_x_symbols) # type: ignore
        self.calculate_gen_poly_pushButton.clicked.connect(rsRegisterForm.calculate_generating_poly) # type: ignore
        self.whole_message_pushButton.clicked.connect(rsRegisterForm.whole_message) # type: ignore
        self.poly_repr_checkBox.toggled['bool'].connect(rsRegisterForm.poly_repr_checked) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(rsRegisterForm)

    def retranslateUi(self, rsRegisterForm):
        _translate = QtCore.QCoreApplication.translate
        rsRegisterForm.setWindowTitle(_translate("rsRegisterForm", "Form"))
        self.poly_repr_checkBox.setText(_translate("rsRegisterForm", "Write finite field polynomials and elements as numbers"))
        self.label.setText(_translate("rsRegisterForm", "n"))
        self.label_2.setText(_translate("rsRegisterForm", "k"))
        self.label_3.setText(_translate("rsRegisterForm", "<html><head/><body><p>GF(2<span style=\" vertical-align:super;\">m</span>)</p></body></html>"))
        self.label_4.setText(_translate("rsRegisterForm", "Primitive polynomial"))
        self.label_5.setText(_translate("rsRegisterForm", "Primitive element"))
        self.label_11.setText(_translate("rsRegisterForm", "Generating polynomial"))
        self.calculate_gen_poly_pushButton.setText(_translate("rsRegisterForm", "Calculate generating polynomial"))
        self.calculate_primitives_pushButton.setText(_translate("rsRegisterForm", "Calculate primitive poly/element"))
        self.label_6.setText(_translate("rsRegisterForm", "Input"))
        self.label_7.setText(_translate("rsRegisterForm", "Output"))
        self.label_8.setText(_translate("rsRegisterForm", "Fill symbol"))
        self.label_9.setText(_translate("rsRegisterForm", "x symbols per click"))
        self.label_10.setText(_translate("rsRegisterForm", "Calculate next symbol or message:"))
        self.next_symbol_pushButton.setText(_translate("rsRegisterForm", "Next symbol"))
        self.next_x_symbols_pushButton.setText(_translate("rsRegisterForm", "Next x symbols"))
        self.whole_message_pushButton.setText(_translate("rsRegisterForm", "Whole message"))
