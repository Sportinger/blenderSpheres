import bpy
import math

# Erase everything in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete() 

# Delete all collections
for collection in bpy.data.collections:
    bpy.data.collections.remove(collection)

# Create a circle curve
bpy.ops.curve.primitive_bezier_circle_add(radius=1)
circle_curve = bpy.context.object

# Create collections
main_camera_collection = bpy.data.collections.new('MainCamera')
bpy.context.scene.collection.children.link(main_camera_collection)

additional_cameras_collection = bpy.data.collections.new('AdditionalCameras')
bpy.context.scene.collection.children.link(additional_cameras_collection)

# Function to create a camera, set its location to (0,0,0) and assign to a collection
def create_camera(name, collection):
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = name
    camera.location = (0, 0, 0)  # Set location to origin
    collection.objects.link(camera)
    bpy.context.scene.collection.objects.unlink(camera)
    return camera

# Create main camera
main_camera = create_camera('MainCamera', main_camera_collection)

# Create and position additional cameras
additional_cameras = []
for i in range(4):
    angle = 90 * i
    camera_name = f'AdditionalCamera{i+1}'
    camera = create_camera(camera_name, additional_cameras_collection)
    additional_cameras.append(camera)

# Constrain cameras to follow path
def constrain_to_path(camera, path):
    follow_path_constraint = camera.constraints.new(type='FOLLOW_PATH')
    follow_path_constraint.target = path
    follow_path_constraint.offset_factor = angle / 360
    bpy.context.view_layer.update()

# Point cameras to center
def point_to_center(camera):
    track_to_constraint = camera.constraints.new(type='TRACK_TO')
    track_to_constraint.target = circle_curve
    track_to_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    track_to_constraint.up_axis = 'UP_Y'
    bpy.context.view_layer.update()

# Apply constraints to main camera and additional cameras
for i, camera in enumerate([main_camera] + additional_cameras):
    angle = 90 * i
    constrain_to_path(camera, circle_curve)
    point_to_center(camera)

# Link camera settings (focal length)
def link_focal_length(from_camera, to_camera):
    to_camera.data.driver_add("lens")
    driver = to_camera.data.animation_data.drivers[-1]
    driver.driver.type = 'AVERAGE'
    var = driver.driver.variables.new()
    var.name = "var"
    var.targets[0].id = from_camera.data
    var.targets[0].data_path = "lens"
    driver.expression = "var"

# Apply linking
for camera in additional_cameras:
    link_focal_length(main_camera, camera)
