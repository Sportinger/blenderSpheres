import bpy
import math

# Erase everything in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete() 

# Delete all collections
for collection in bpy.data.collections:
    bpy.data.collections.remove(collection)

# Create a circle curve
bpy.ops.curve.primitive_bezier_circle_add(radius=3)
circle_curve = bpy.context.object

# Create collections
main_camera_collection = bpy.data.collections.new('MainCamera')
bpy.context.scene.collection.children.link(main_camera_collection)

additional_cameras_collection = bpy.data.collections.new('AdditionalCameras')
bpy.context.scene.collection.children.link(additional_cameras_collection)

spheres_collection = bpy.data.collections.new('Spheres')
bpy.context.scene.collection.children.link(spheres_collection)

domain_collection = bpy.data.collections.new('Domain')
bpy.context.scene.collection.children.link(domain_collection)

def create_cube(collection):
    # Create a cube
    bpy.ops.mesh.primitive_cube_add(size=1)
    cube = bpy.context.object
    cube.name = 'Domain'

    # Link the cube to the specified collection ('Domain' in this case)
    collection.objects.link(cube)

    # Unlink the cube from the scene's default collection
    bpy.context.scene.collection.objects.unlink(cube)

    # Set the cube's display type to wireframe
    cube.display_type = 'WIRE'

    return cube

create_cube(domain_collection)

def create_camera(name, collection, path, offset, main_camera=None):
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = name
    camera.location = (0, 0, 0)  # Set location to origin
    collection.objects.link(camera)
    bpy.context.scene.collection.objects.unlink(camera)
    
    # Constrain camera to follow path
    follow_path_constraint = camera.constraints.new(type='FOLLOW_PATH')
    follow_path_constraint.target = path
    follow_path_constraint.use_curve_follow = True
    # Set offset based on the fraction of the path's length
    follow_path_constraint.offset = offset
    bpy.context.view_layer.update()

    # Point camera to center
    track_to_constraint = camera.constraints.new(type='TRACK_TO')
    track_to_constraint.target = path
    track_to_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    track_to_constraint.up_axis = 'UP_Y'
    bpy.context.view_layer.update()

    # Link focal length to main camera
    if main_camera is not None:
        camera.data.driver_add("lens")
        driver = camera.data.animation_data.drivers[0]
        var = driver.driver.variables.new()
        var.name = 'main_camera_lens'
        var.type = 'SINGLE_PROP'
        var.targets[0].id = main_camera  # Pass the main camera object
        var.targets[0].data_path = 'data.lens'  # Access the lens property of the camera data
        driver.driver.expression = 'main_camera_lens'
    
    # Update the scene to apply the changes
    bpy.context.view_layer.update()

    return camera

# Create main camera
main_camera = create_camera('MainCamera', main_camera_collection, circle_curve, 0)

# Create additional cameras
for i in range(4):
    camera_name = f'AdditionalCamera{i+1}'
    offset = i * 25  # Offset each additional camera by 25 units along the path
    create_camera(camera_name, additional_cameras_collection, circle_curve, offset, main_camera)