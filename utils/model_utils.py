# utils/model_utils.py

import bpy
import base64
import os
import tempfile
import bmesh
from typing import Any, Dict, Optional


def mesh_to_obj_string(obj_name: str) -> Optional[str]:
    """Convert a Blender mesh object to OBJ format string"""
    try:
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != 'MESH':
            return None
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.obj', mode='w+', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Store current selection
        original_selection = bpy.context.selected_objects.copy()
        original_active = bpy.context.view_layer.objects.active
        
        # Select only this object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Export to OBJ
        bpy.ops.export_scene.obj(
            filepath=temp_path,
            use_selection=True,
            use_materials=False,
            use_uvs=True,
            use_normals=True
        )
        
        # Read the OBJ file content
        with open(temp_path, 'r') as f:
            obj_content = f.read()
        
        # Restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for original_obj in original_selection:
            original_obj.select_set(True)
        bpy.context.view_layer.objects.active = original_active
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return obj_content
    except Exception as e:
        print(f"Error converting mesh to OBJ: {e}")
        return None


def import_gltf_from_base64(base64_string: str, filename: str = "runchat_model.gltf") -> bool:
    """Import GLTF model from base64 data"""
    temp_path = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.gltf', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Decode base64 to file
        model_data = base64.b64decode(base64_string)
        with open(temp_path, 'wb') as f:
            f.write(model_data)
        
        # Import the GLTF file
        try:
            bpy.ops.import_scene.gltf(filepath=temp_path)
        except:
            # Fallback for older Blender versions
            bpy.ops.import_scene.gltf2(filepath=temp_path)
        
        print(f"Successfully imported GLTF model: {filename}")
        return True
        
    except Exception as e:
        print(f"Error importing GLTF model: {e}")
        return False
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as e:
                print(f"Warning: Could not delete temp file {temp_path}: {e}")


def get_material_from_image(image_name: str) -> Optional[bpy.types.Material]:
    """Create or get a material that uses the specified image"""
    try:
        image = bpy.data.images.get(image_name)
        if not image:
            print(f"Image '{image_name}' not found")
            return None
        
        # Check if material already exists
        material_name = f"RunChat_{image_name}"
        material = bpy.data.materials.get(material_name)
        
        if material:
            return material
        
        # Create new material with image
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        
        # Clear default nodes
        material.node_tree.nodes.clear()
        
        # Add output node
        output_node = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (400, 0)
        
        # Add principled BSDF
        bsdf_node = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_node.location = (0, 0)
        
        # Add image texture node
        texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
        texture_node.location = (-400, 0)
        texture_node.image = image
        
        # Connect nodes
        material.node_tree.links.new(texture_node.outputs['Color'], bsdf_node.inputs['Base Color'])
        material.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
        
        print(f"Created material: {material_name}")
        return material
        
    except Exception as e:
        print(f"Error creating material: {e}")
        return None


def apply_material_to_selected():
    """Apply the most recent RunChat material to selected objects"""
    try:
        # Find the most recent RunChat material
        runchat_materials = [mat for mat in bpy.data.materials if mat.name.startswith("RunChat_")]
        if not runchat_materials:
            print("No RunChat materials found")
            return False
        
        # Get the most recently created material
        latest_material = max(runchat_materials, key=lambda mat: mat.name)
        
        # Apply to selected objects
        applied_count = 0
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                # Clear existing materials
                obj.data.materials.clear()
                # Add the new material
                obj.data.materials.append(latest_material)
                applied_count += 1
        
        print(f"Applied material '{latest_material.name}' to {applied_count} objects")
        return applied_count > 0
        
    except Exception as e:
        print(f"Error applying material: {e}")
        return False


def create_plane_with_image(image_name: str, name: str = "RunChat_Plane") -> Optional[bpy.types.Object]:
    """Create a plane object with the specified image as material"""
    try:
        image = bpy.data.images.get(image_name)
        if not image:
            print(f"Image '{image_name}' not found")
            return None
        
        # Create plane
        bpy.ops.mesh.primitive_plane_add(size=2)
        plane = bpy.context.active_object
        plane.name = name
        
        # Create and assign material
        material = get_material_from_image(image_name)
        if material:
            plane.data.materials.append(material)
        
        # Scale plane to match image aspect ratio
        if image.size[0] > 0 and image.size[1] > 0:
            aspect_ratio = image.size[0] / image.size[1]
            if aspect_ratio > 1:
                # Wider than tall
                plane.scale = (aspect_ratio, 1, 1)
            else:
                # Taller than wide
                plane.scale = (1, 1/aspect_ratio, 1)
        
        print(f"Created plane '{name}' with image '{image_name}'")
        return plane
        
    except Exception as e:
        print(f"Error creating plane with image: {e}")
        return None


def export_selected_as_gltf(filepath: str) -> bool:
    """Export selected objects as GLTF file"""
    try:
        if not bpy.context.selected_objects:
            print("No objects selected for export")
            return False
        
        # Ensure filepath has correct extension
        if not filepath.lower().endswith(('.gltf', '.glb')):
            filepath += '.gltf'
        
        # Export selected objects
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            use_selection=True,
            export_format='GLTF_SEPARATE' if filepath.endswith('.gltf') else 'GLB',
            export_materials='EXPORT',
            export_textures=True
        )
        
        print(f"Exported selected objects to: {filepath}")
        return True
        
    except Exception as e:
        print(f"Error exporting GLTF: {e}")
        return False 