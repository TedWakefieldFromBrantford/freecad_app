# TubeDialog.py
try:
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
except ImportError:
    raise ImportError("This script must be run within FreeCAD")

from PySide2 import QtWidgets, QtCore
import json
import jsonpath as jp
import os
from datetime import datetime

class TubeDialog(QtWidgets.QDialog):
    #open .json file
    with open('Tube_database.json') as f:
        data = json.load(f)
        
    def __init__(self, parent=Gui.getMainWindow()):
        super().__init__(parent)
        self.setWindowTitle("Create Parametric Tube")
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumSize(400, 450)
        self.initUI()
    
    def initUI(self):
        layout = QtWidgets.QGridLayout()
        row = 0
        
        # Object Name
        layout.addWidget(QtWidgets.QLabel("Object Name:"), row, 0)
        self.obj_name = QtWidgets.QLineEdit("MyTube")
        layout.addWidget(self.obj_name, row, 1)
        row += 1
        
        # Origin
        layout.addWidget(QtWidgets.QLabel("Origin X:"), row, 0)
        self.origin_x = QtWidgets.QDoubleSpinBox()
        self.origin_x.setValue(0.0)
        layout.addWidget(self.origin_x, row, 1)
        row += 1
        
        layout.addWidget(QtWidgets.QLabel("Origin Y:"), row, 0)
        self.origin_y = QtWidgets.QDoubleSpinBox()
        self.origin_y.setValue(0.0)
        layout.addWidget(self.origin_y, row, 1)
        row += 1
        
        layout.addWidget(QtWidgets.QLabel("Origin Z:"), row, 0)
        self.origin_z = QtWidgets.QDoubleSpinBox()
        self.origin_z.setValue(0.0)
        layout.addWidget(self.origin_z, row, 1)
        row += 1
        
        # Tube Parameters
        layout.addWidget(QtWidgets.QLabel("Outer Radius:"), row, 0)
        self.outer_radius = QtWidgets.QDoubleSpinBox()
        self.outer_radius.setValue(10.0)
        self.outer_radius.setMinimum(0.1)
        layout.addWidget(self.outer_radius, row, 1)
        row += 1
        
        layout.addWidget(QtWidgets.QLabel("Inner Radius:"), row, 0)
        self.inner_radius = QtWidgets.QDoubleSpinBox()
        self.inner_radius.setValue(5.0)
        self.inner_radius.setMinimum(0.1)
        self.inner_radius.setMaximum(self.outer_radius.value() - 0.1)
        layout.addWidget(self.inner_radius, row, 1)
        row += 1
        
        # Connect radius validation
        self.outer_radius.valueChanged.connect(
            lambda: self.inner_radius.setMaximum(self.outer_radius.value() - 0.1)
        )
        self.inner_radius.valueChanged.connect(
            lambda: self.outer_radius.setMinimum(self.inner_radius.value() + 0.1)
        )
        
        layout.addWidget(QtWidgets.QLabel("Height:"), row, 0)
        self.height = QtWidgets.QDoubleSpinBox()
        self.height.setValue(20.0)
        self.height.setMinimum(0.1)
        layout.addWidget(self.height, row, 1)
        row += 1
        
        layout.addWidget(QtWidgets.QLabel("Angle (°):"), row, 0)
        self.angle = QtWidgets.QDoubleSpinBox()
        self.angle.setRange(0, 360)
        self.angle.setValue(360)
        layout.addWidget(self.angle, row, 1)
        row += 1
        
        # Rotation
        layout.addWidget(QtWidgets.QLabel("Rotation X (°):"), row, 0)
        self.rot_x = QtWidgets.QDoubleSpinBox()
        self.rot_x.setRange(-360, 360)
        layout.addWidget(self.rot_x, row, 1)
        row += 1
        
        layout.addWidget(QtWidgets.QLabel("Rotation Y (°):"), row, 0)
        self.rot_y = QtWidgets.QDoubleSpinBox()
        self.rot_y.setRange(-360, 360)
        layout.addWidget(self.rot_y, row, 1)
        row += 1
        
        layout.addWidget(QtWidgets.QLabel("Rotation Z (°):"), row, 0)
        self.rot_z = QtWidgets.QDoubleSpinBox()
        self.rot_z.setRange(-360, 360)
        layout.addWidget(self.rot_z, row, 1)
        row += 1
        
        # Buttons
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons, row, 0, 1, 2)
        
        self.setLayout(layout)
    
    def getValues(self):
        return {
            'type': 'tube',
            'name': self.obj_name.text(),
            'origin': (self.origin_x.value(), self.origin_y.value(), self.origin_z.value()),
            'outer_radius': self.outer_radius.value(),
            'inner_radius': self.inner_radius.value(),
            'height': self.height.value(),
            'angle': self.angle.value(),
            'rotation': (self.rot_x.value(), self.rot_y.value(), self.rot_z.value())
        }

    @staticmethod
    def append_to_database(entry):
        """Append tube parameters to a JSON database in current directory"""
        db_path = os.path.join(os.getcwd(), "Tube_database.json")
        try:
            entry_data = {
                'timestamp': datetime.now().isoformat(),
                'data': entry
            }
            
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    data = json.load(f)
            else:
                data = []
            
            data.append(entry_data)
            
            with open(db_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, "Database Error", 
                                        f"Failed to save to database:\n{str(e)}")

def create_parametric_tube():
    if not App.GuiUp:
        QtWidgets.QMessageBox.critical(None, "Error", "This script requires FreeCAD's GUI mode!")
        return
    
    dialog = TubeDialog()
    if not dialog.exec_():
        return
    
    values = dialog.getValues()
    
    try:
        # Validate radii
        if values['inner_radius'] >= values['outer_radius']:
            raise ValueError("Inner radius must be smaller than outer radius")
            
        doc = App.ActiveDocument or App.newDocument("ParametricTube")
        
        # Create outer cylinder
        outer_cyl = doc.addObject("Part::Cylinder", "OuterCylinder")
        outer_cyl.Radius = values['outer_radius']
        outer_cyl.Height = values['height']
        outer_cyl.Angle = values['angle']
        
        # Create inner cylinder
        inner_cyl = doc.addObject("Part::Cylinder", "InnerCylinder")
        inner_cyl.Radius = values['inner_radius']
        inner_cyl.Height = values['height'] + 2
        inner_cyl.Angle = values['angle']
        
        # Create rotation using Euler angles (ZYX)
        rotation = App.Rotation(
            values['rotation'][2],  # Z
            values['rotation'][1],  # Y
            values['rotation'][0]   # X
        )
        placement = App.Placement(
            App.Vector(*values['origin']),
            rotation
        )
        
        # Apply placement
        outer_cyl.Placement = placement
        inner_cyl.Placement = placement
        
        # Create boolean cut
        tube = doc.addObject("Part::Cut", values['name'])
        tube.Base = outer_cyl
        tube.Tool = inner_cyl
        
        # Hide original cylinders
        outer_cyl.ViewObject.hide()
        inner_cyl.ViewObject.hide()
        
        doc.recompute()
        Gui.SendMsgToActiveView("ViewFit")
        TubeDialog.append_to_database(values)
        
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Error", f"Failed to create tube:\n{str(e)}")
if __name__ == "__main__":
    create_parametric_tube()