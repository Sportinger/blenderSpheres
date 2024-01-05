import bpy
import random
import mathutils

# Create a new collection
def create_collection(collection_name):
    if collection_name not in bpy.data.collections:
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(new_collection)
    else:
        new_collection = bpy.data.collections[collection_name]
    return new_collection

# Create a cube with transparent material
def create_cube(collection):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cube = bpy.context.object
    collection.objects.link(cube)
    bpy.context.scene.collection.objects.unlink(cube)

    # Create a transparent material
    mat = bpy.data.materials.new(name="TransparentMaterial")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.2
    mat.blend_method = 'BLEND'

    # Assign material to cube
    if cube.data.materials:
        cube.data.materials[0] = mat
    else:
        cube.data.materials.append(mat)

    return cube

# Create a sphere
def create_sphere(location, collection):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=location)
    sphere = bpy.context.object
    collection.objects.link(sphere)
    bpy.context.scene.collection.objects.unlink(sphere)
    return sphere

# Generate a random position within the cube
def random_position_within_cube(cube):
    return (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))

# Check if a sphere is in the camera's view
def is_sphere_in_camera_view(camera, sphere):
    # Transform sphere location to camera view space
    cam_matrix = camera.matrix_world.inverted()
    sphere_location = cam_matrix @ sphere.location
    
    # Camera parameters
    cam_data = camera.data
    frame = [mathutils.Vector(corner) for corner in cam_data.view_frame(scene=bpy.context.scene)]
    
    # Check if sphere is in the camera frustum
    for corner in frame:
        if (corner.x - sphere_location.x) * sphere_location.x > 0:
            return False
        if (corner.y - sphere_location.y) * sphere_location.y > 0:
            return False
        if (corner.z - sphere_location.z) * sphere_location.z > 0:
            return False

    return True

# Check for overlapping spheres in camera view
def is_overlapping_in_camera_view(camera, sphere, other_spheres):
    if not is_sphere_in_camera_view(camera, sphere):
        return False

    for other in other_spheres:
        distance = (sphere.location - other.location).length
        if distance < (sphere.scale.x + other.scale.x) * 0.1:
            return True

    return False

# Delete an object
def delete_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)

# Main execution
domain_collection = create_collection("Domain")
spheres_collection = create_collection("Spheres")

create_cube(domain_collection)
spheres = []
camera = bpy.data.objects['AdditionalCamera1']  # Assuming this camera already exists

while len(spheres) < 10:
    location = random_position_within_cube(bpy.data.objects['Cube'])
    sphere = create_sphere(location, spheres_collection)

    if is_overlapping_in_camera_view(camera, sphere, spheres):
        delete_object(sphere)
    else:
        spheres.append(sphere)
