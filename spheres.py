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


def project_sphere_on_camera(camera, sphere):
    # Get the camera matrices
    cam_matrix = camera.matrix_world.inverted()
    projection_matrix = camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get())

    # Transform the sphere location to camera view space
    sphere_location = cam_matrix @ sphere.location
    sphere_location_2d = projection_matrix @ sphere_location.to_4d()

    # Normalize the 2D coordinates
    sphere_location_2d /= sphere_location_2d.w
    sphere_location_2d = (sphere_location_2d.xy + 1) / 2

    # Calculate the projected radius
    sphere_radius = sphere.scale.x * 0.1
    distance_to_camera = (sphere.location - camera.location).length
    projected_radius = sphere_radius / distance_to_camera

    return sphere_location_2d.xy, projected_radius

def is_overlapping_in_camera_view_2d(camera, sphere1, sphere2):
    # Project spheres on camera
    loc1, radius1 = project_sphere_on_camera(camera, sphere1)
    loc2, radius2 = project_sphere_on_camera(camera, sphere2)

    # Check 2D overlap
    distance = (loc1 - loc2).length
    return distance < (radius1 + radius2)



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

    overlapping = False
    for existing_sphere in spheres:
        if is_overlapping_in_camera_view_2d(camera, sphere, existing_sphere):
            overlapping = True
            break
    if overlapping:
        delete_object(sphere)
    else:
        spheres.append(sphere)
