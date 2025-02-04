try:
    import FreeCAD as App
    import FreeCADGui as Gui
except ImportError:
    raise ImportError("This script must be run within FreeCAD")

from PySide2 import QtWidgets, QtCore
import json
import os
from datetime import datetime

class CubeDialog(QtWidgets.QDialog):
    def __init__(self, parent=Gui.getMainWindow()):
        super().__init__(parent)
        self.setWindowTitle("Create Parametric Cube")
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumSize(400, 500)  # Ensure dialog is large enough
        self.initUI()
    
    def initUI(self):
        layout = QtWidgets.QGridLayout()
        row = 0
        
        # Object Name Input - now at top and visible
        layout.addWidget(QtWidgets.QLabel("Object Name:"), row, 0)
        self.obj_name = QtWidgets.QLineEdit("MyCube")
        layout.addWidget(self.obj_name, row, 1)
        row += 1
        
        # Origin Inputs
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
        
        # Dimensions Inputs
        layout.addWidget(QtWidgets.QLabel("Length:"), row, 0)
        self.length = QtWidgets.QDoubleSpinBox()
        self.length.setValue(10.0)
        self.length.setMinimum(0.1)
        layout.addWidget(self.length, row, 1)
        row += 1
        
        layout.addWidget(QtWidgets.QLabel("Width:"), row, 0)
        self.width = QtWidgets.QDoubleSpinBox()
        self.width.setValue(10.0)
        self.width.setMinimum(0.1)
        layout.addWidget(self.width, row, 1)
        row += 1
        
        layout.addWidget(QtWidgets.QLabel("Height:"), row, 0)
        self.height = QtWidgets.QDoubleSpinBox()
        self.height.setValue(10.0)
        self.height.setMinimum(0.1)
        layout.addWidget(self.height, row, 1)
        row += 1
        
        # Rotation Inputs
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
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons, row, 0, 1, 2)
        
        self.setLayout(layout)
    
    def getValues(self):
        return {
            'name': self.obj_name.text(),
            'origin': (self.origin_x.value(), self.origin_y.value(), self.origin_z.value()),
            'dimensions': (self.length.value(), self.width.value(), self.height.value()),
            'rotation': (self.rot_x.value(), self.rot_y.value(), self.rot_z.value())
        }

def append_to_database(entry):
    """Append cube parameters to a JSON database in current directory"""
    db_path = os.path.join(os.getcwd(), "cube_database.json")
    
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

def create_parametric_cube():
    if not App.GuiUp:
        QtWidgets.QMessageBox.critical(None, "Error", "This script requires FreeCAD's GUI mode!")
        return
    
    doc = App.ActiveDocument or App.newDocument("ParametricCube")
    dialog = CubeDialog()
    
    if not dialog.exec_():
        return
    
    values = dialog.getValues()
    
    try:
        cube = doc.addObject("Part::Box", values['name'])
        cube.Label = values['name']
        cube.Length = values['dimensions'][0]
        cube.Width = values['dimensions'][1]
        cube.Height = values['dimensions'][2]
        
        rot_x = App.Rotation(App.Vector(1, 0, 0), values['rotation'][0])
        rot_y = App.Rotation(App.Vector(0, 1, 0), values['rotation'][1])
        rot_z = App.Rotation(App.Vector(0, 0, 1), values['rotation'][2])
        
        cube.Placement = App.Placement(
            App.Vector(*values['origin']),
            rot_z * rot_y * rot_x
        )
        
        doc.recompute()
        Gui.Selection.addSelection(cube)
        Gui.SendMsgToActiveView("ViewFit")
        append_to_database(values)
        
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Error", f"Failed to create cube:\n{str(e)}")

if __name__ == "__main__":
    create_parametric_cube()