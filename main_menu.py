import FreeCAD
import FreeCADGui
from PySide import QtGui
from make_cube import *
from make_cylinder import *

def show_main_dialog():
    main_options = ['Make Primitive', 'Do Operation', 'Quit']
    main_choice, ok = QtGui.QInputDialog.getItem(
        FreeCADGui.getMainWindow(),
        "Main Menu",
        "Select an action:",
        main_options,
        0,
        False
    )
    
    if not ok:
        return
    
    if main_choice == 'Make Primitive':
        show_primitive_dialog()
    elif main_choice == 'Do Operation':
        show_operation_dialog()
    elif main_choice == 'Quit':
        return

def show_primitive_dialog():
    primitives = ['Box', 'Sphere', 'Cylinder', 'Cone', 'Torus', 'Prism', 'Wedge']
    primitive, ok = QtGui.QInputDialog.getItem(
        FreeCADGui.getMainWindow(),
        "Create Primitive",
        "Select primitive type:",
        primitives,
        0,
        False
    )
    
    if ok and primitive:
        create_primitive(primitive)

def create_primitive(primitive_type):
    doc = FreeCAD.ActiveDocument
    if not doc:
        doc = FreeCAD.newDocument()
    
    if primitive_type == 'Box':
        create_parametric_cube()
    elif primitive_type == 'Sphere':
        doc.addObject("Part::Sphere", "Sphere")
    elif primitive_type == 'Cylinder':
        create_parametric_cylinder()
    elif primitive_type == 'Cone':
        doc.addObject("Part::Cone", "Cone")
    elif primitive_type == 'Torus':
        doc.addObject("Part::Torus", "Torus")
    
    doc.recompute()
    FreeCADGui.SendMsgToActiveView("ViewFit")

def show_operation_dialog():
    operations = [
        'Boolean Union', 'Boolean Difference', 'Boolean Intersection',
        'Join', 'Split', 'Compound', 'Extrude', 'Chamfer', 'Fillet'
    ]
    operation, ok = QtGui.QInputDialog.getItem(
        FreeCADGui.getMainWindow(),
        "Select Operation",
        "Choose an operation:",
        operations,
        0,
        False
    )
    
    if ok and operation:
        execute_operation(operation)

def execute_operation(operation):
    command_map = {
        'Boolean Union': 'Part_Fuse',
        'Boolean Difference': 'Part_Cut',
        'Boolean Intersection': 'Part_Common',
        'Join': 'Part_JoinConnect',
        'Split': 'Part_Split',
        'Compound': 'Part_Compound',
        'Extrude': 'Part_Extrude',
        'Chamfer': 'Part_Chamfer',
        'Fillet': 'Part_Fillet'
    }
    
    FreeCADGui.runCommand(command_map.get(operation, ''))

show_main_dialog()