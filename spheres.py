import bpy
import random
import mathutils

# Function to delete all objects in a specified collection
def delete_objects_in_collection(collection_name):
    # Check if the collection exists in the current scene
    if collection_name in bpy.data.collections:
        # Get the collection
        collection = bpy.data.collections[collection_name]
        
        # Select all objects in the collection
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

# Call the function to delete objects in the 'Spheres' collection
delete_objects_in_collection('Spheres')

# Create a sphere
def create_sphere(location, collection):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=location)
    sphere = bpy.context.object
    collection.objects.link(sphere)
    bpy.context.scene.collection.objects.unlink(sphere)
    return sphere

# Generate a random position within the domain
def random_position_within_domain(domain):
    # Get the scale of the domain
    domain_scale = domain.scale
    return (random.uniform(-domain_scale.x / 2, domain_scale.x / 2), 
            random.uniform(-domain_scale.y / 2, domain_scale.y / 2), 
            random.uniform(-domain_scale.z / 2, domain_scale.z / 2))


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
location = random_position_within_domain(bpy.data.objects['Domain'])
spheres = []
camera = bpy.data.objects['AdditionalCamera1']  # Assuming this camera already exists

# Erstellen Sie die 'Spheres' Collection, wenn sie nicht existiert
if 'Spheres' not in bpy.data.collections:
    spheres_collection = bpy.data.collections.new('Spheres')
    bpy.context.scene.collection.children.link(spheres_collection)
else:
    spheres_collection = bpy.data.collections['Spheres']


while len(spheres) < 100:
    location = random_position_within_domain(bpy.data.objects['Domain'])
    sphere = create_sphere(location, spheres_collection)

    if is_overlapping_in_camera_view(camera, sphere, spheres):
        delete_object(sphere)
    else:
        spheres.append(sphere)
