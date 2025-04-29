#!/usr/bin/env python3
import bpy
import time
import math
from xarm.wrapper import XArmAPI

# Initialize the xArm
arm = XArmAPI("192.168.1.240")  # Replace with your robot's IP
arm.connect()

# Robot scaling factor
robotscale = 1000  # Convert Blender units to millimeters

# Get initial xarm position
xarm_position = arm.get_position()
current_position = xarm_position[1]
print(f"Initial robot position: {current_position}")

# Set safety boundaries (in mm)
x_max, x_min = 600, 205
y_max, y_min = 300, -300
z_max, z_min = 600, 100
arm.set_reduced_tcp_boundary([x_max, x_min, y_max, y_min, z_max, z_min])

# Add a property to store the streaming state
bpy.types.Scene.xarm_streaming = bpy.props.BoolProperty(
    name="Streaming",
    description="Toggle real-time streaming to robot",
    default=False
)

class XArmController(bpy.types.Operator):
    bl_idname = "wm.xarm_controller"
    bl_label = "XArm Controller"
    
    _timer = None
    _empty_name = "tcp_target"  # Updated name
    _last_position = None
    
    def get_world_position_rotation(self, obj):
        """Get object's world space position and rotation"""
        matrix_world = obj.matrix_world
        location = matrix_world.translation
        rotation = matrix_world.to_euler()
        
        return location, rotation
    
    def validate_position(self, pos):
        """Check if position values are valid (not NaN or infinite)"""
        return all(isinstance(v, (int, float)) and math.isfinite(v) for v in pos)
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            # Only process movement if streaming is enabled
            if not context.scene.xarm_streaming:
                context.scene.xarm_status = "Streaming Paused"
                return {'PASS_THROUGH'}
                
            # Get the Empty object
            empty = bpy.data.objects.get(self._empty_name)
            if empty is None:
                print(f"Error: Empty object '{self._empty_name}' not found")
                return {'CANCELLED'}
            
            try:
                # Get world space position and rotation
                location, rotation = self.get_world_position_rotation(empty)
                
                # Calculate new target position with orientation
                robot_x = location.x * robotscale
                robot_y = location.y * robotscale
                robot_z = location.z * robotscale
                robot_rx = math.degrees(rotation.x)
                robot_ry = math.degrees(rotation.y)
                robot_rz = math.degrees(rotation.z)
                
                # Create position array for validation
                new_pos = [robot_x, robot_y, robot_z, robot_rx, robot_ry, robot_rz]
                
                # Validate position values
                if not self.validate_position(new_pos):
                    print("Invalid position values detected")
                    if self._last_position is not None:
                        new_pos = self._last_position
                    else:
                        return {'PASS_THROUGH'}
                
                # Clamp position values to safety boundaries
                robot_x = max(min(robot_x, x_max), x_min)
                robot_y = max(min(robot_y, y_max), y_min)
                robot_z = max(min(robot_z, z_max), z_min)
                
                # Store last valid position
                self._last_position = [robot_x, robot_y, robot_z, robot_rx, robot_ry, robot_rz]
                
                # Enable motion and set mode
                arm.motion_enable(enable=True)
                arm.set_mode(1)  # Change to mode 1 for servo_cartesian
                arm.set_state(0)
                
                # Stream position and orientation using servo_cartesian
                arm.set_servo_cartesian(
                    [robot_x, robot_y, robot_z, robot_rx, robot_ry, robot_rz],
                    speed=5,
                    mvacc=2000
                )
                
                # Update status and display current values
                context.scene.xarm_status = (
                    f"Streaming: X:{robot_x:.1f} Y:{robot_y:.1f} Z:{robot_z:.1f} "
                    f"RX:{robot_rx:.1f} RY:{robot_ry:.1f} RZ:{robot_rz:.1f}"
                )
                
            except Exception as e:
                print(f"Error during position update: {str(e)}")
                context.scene.xarm_status = f"Error: {str(e)}"
                return {'PASS_THROUGH'}
            
        elif event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}
            
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        if not hasattr(context.scene, 'xarm_status'):
            bpy.types.Scene.xarm_status = bpy.props.StringProperty(
                name="XArm Status",
                default="Initializing..."
            )
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.02, window=context.window)  # 50Hz update rate
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        context.scene.xarm_status = "Stopped"

class XArmStreamToggle(bpy.types.Operator):
    bl_idname = "wm.xarm_stream_toggle"
    bl_label = "Toggle Streaming"
    
    def execute(self, context):
        error_message = check_setup()
        if error_message:
            self.report({'ERROR'}, error_message)
            return {'CANCELLED'}
        
        context.scene.xarm_streaming = not context.scene.xarm_streaming
        return {'FINISHED'}

class XArmPanel(bpy.types.Panel):
    bl_label = "XArm Control"
    bl_idname = "VIEW3D_PT_xarm_control"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'XArm'
    
    def draw(self, context):
        layout = self.layout
        
        # Check for proper setup
        error_message = check_setup()
        if error_message:
            layout.label(text="Setup Error:", icon='ERROR')
            layout.label(text=error_message)
            layout.separator()
            layout.label(text="Instructions:")
            layout.label(text="1. Add an Empty object")
            layout.label(text="2. Name it 'tcp_target'")
            layout.label(text="3. Position it safely")
            return
        
        # Add the streaming toggle button
        row = layout.row()
        if context.scene.xarm_streaming:
            row.operator("wm.xarm_stream_toggle", text="Stop Streaming", icon='PAUSE')
        else:
            row.operator("wm.xarm_stream_toggle", text="Start Streaming", icon='PLAY')
        
        layout.separator()
        
        # Status and position information
        layout.label(text="Status:")
        layout.label(text=context.scene.xarm_status)
        
        if hasattr(context.scene, 'xarm_status'):
            layout.separator()
            pos = arm.get_position()[1]
            layout.label(text=f"X: {pos[0]:.1f}mm")
            layout.label(text=f"Y: {pos[1]:.1f}mm")
            layout.label(text=f"Z: {pos[2]:.1f}mm")
            layout.label(text=f"Roll: {pos[3]:.1f}°")
            layout.label(text=f"Pitch: {pos[4]:.1f}°")
            layout.label(text=f"Yaw: {pos[5]:.1f}°")

def register():
    bpy.utils.register_class(XArmController)
    bpy.utils.register_class(XArmStreamToggle)
    bpy.utils.register_class(XArmPanel)

def unregister():
    bpy.utils.unregister_class(XArmController)
    bpy.utils.unregister_class(XArmStreamToggle)
    bpy.utils.unregister_class(XArmPanel)

def check_setup():
    """Check if the required Empty object exists and return error message if not"""
    if "tcp_target" not in bpy.data.objects:
        return "Error: Required Empty object 'tcp_target' not found. Please create an Empty object named 'tcp_target' at a safe position."
    empty = bpy.data.objects["tcp_target"]
    if empty.type != 'EMPTY':
        return "Error: Object 'tcp_target' must be an Empty object."
    return None

if __name__ == "__main__":
    error_message = check_setup()
    if error_message:
        print(error_message)
    else:
        register()
        # Start the operator
        bpy.ops.wm.xarm_controller()