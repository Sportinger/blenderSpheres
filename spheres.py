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
    sphere_location_2d = (sphere_location_2d.xy + mathutils.Vector((1, 1))) / 2

    # Calculate the projected radius
    # Project two points on the sphere's circumference onto the camera's view
    point1 = cam_matrix @ (sphere.location + mathutils.Vector((sphere.scale.x, 0, 0)))
    point2 = cam_matrix @ (sphere.location - mathutils.Vector((sphere.scale.x, 0, 0)))
    point1_2d = projection_matrix @ point1.to_4d()
    point2_2d = projection_matrix @ point2.to_4d()
    # Normalize the 2D coordinates
    point1_2d /= point1_2d.w
    point2_2d /= point2_2d.w
    point1_2d = (point1_2d.xy + mathutils.Vector((1, 1))) / 2
    point2_2d = (point2_2d.xy + mathutils.Vector((1, 1))) / 2
    # The projected radius is half the distance between the projected points
    projected_radius = (point1_2d - point2_2d).length / 2

    return sphere_location_2d.xy, projected_radius

def is_overlapping_in_camera_view_2d(camera, sphere1, sphere2):
    # Project spheres on camera
    loc1, radius1 = project_sphere_on_camera(camera, sphere1)
    loc2, radius2 = project_sphere_on_camera(camera, sphere2)

    # Check 2D overlap
    distance = (loc1 - loc2).length
    return distance < (radius1 + radius2)

def is_within_domain(location, domain):
    domain_scale = domain.scale
    return (-domain_scale.x / 2 <= location.x <= domain_scale.x / 2 and 
            -domain_scale.y / 2 <= location.y <= domain_scale.y / 2 and 
            -domain_scale.z / 2 <= location.z <= domain_scale.z / 2)

# Delete an object
def delete_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.context.view_layer.update() 

# Main execution
location = random_position_within_domain(bpy.data.objects['Domain'])
spheres = []
camera = bpy.data.objects['AdditionalCamera1']  # Assuming this camera already exists

# Create the 'Spheres' collection if it doesn't exist
if 'Spheres' not in bpy.data.collections:
    spheres_collection = bpy.data.collections.new('Spheres')
    bpy.context.scene.collection.children.link(spheres_collection)
else:
    spheres_collection = bpy.data.collections['Spheres']

attempts = 0
while len(spheres) < 100 and attempts < 1000:
    location = random_position_within_domain(bpy.data.objects['Domain'])
    sphere = create_sphere(location, spheres_collection)
    bpy.context.view_layer.update()

    overlapping = True
    while overlapping and attempts < 1000:
        overlapping = False
        for existing_sphere in spheres:
            if is_overlapping_in_camera_view_2d(camera, sphere, existing_sphere):
                overlapping = True
                attempts += 1
                print(f"Overlap detected between sphere at {sphere.location} and sphere at {existing_sphere.location}. Attempting to reposition...")
                # Calculate a vector that points from the existing sphere to the new sphere
                direction = sphere.location - existing_sphere.location
                # Normalize the direction vector and scale it by a small amount
                direction.normalize()
                direction *= 0.1
                # Move the sphere in the direction of the vector
                new_location = sphere.location + direction
                # Check if the new location is within the domain
                if is_within_domain(new_location, bpy.data.objects['Domain']):
                    sphere.location = new_location
                    print(f"Sphere repositioned to {new_location}.")
                bpy.context.view_layer.update()
                break

    if not overlapping:
        spheres.append(sphere)
        print(f"No overlap detected for sphere at {sphere.location}. Sphere added to list.")
        attempts = 0  # Reset the attempts counter
        bpy.context.view_layer.update()  # Update the viewport after adding