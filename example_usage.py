"""
Example script showing how to use RunChat Blender nodes programmatically.
Run this script in Blender's text editor to create and configure RunChat nodes.
"""

import bpy

def create_runchat_example():
    """Create an example RunChat node setup"""
    
    # Clear existing node trees or create new one
    if "RunChatExample" in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups["RunChatExample"])
    
    # Create a new RunChat node tree
    node_tree = bpy.data.node_groups.new("RunChatExample", "RunChatNodeTree")
    
    # Create RunChat Executor node
    executor_node = node_tree.nodes.new("RunChatExecutorNode")
    executor_node.location = (0, 0)
    executor_node.workflow_id = "your_workflow_id_here"  # Replace with actual ID
    
    # Create Image Send node
    image_send = node_tree.nodes.new("RunChatImageSendNode")
    image_send.location = (-300, 100)
    image_send.image_path = "//path/to/your/image.png"  # Replace with actual path
    
    # Create Image Receive node
    image_receive = node_tree.nodes.new("RunChatImageReceiveNode")
    image_receive.location = (300, 100)
    image_receive.save_path = "//output/images/"
    
    # Create Model Loader node
    model_loader = node_tree.nodes.new("RunChatModelLoaderNode")
    model_loader.location = (-300, -100)
    model_loader.model_url = "https://example.com/model.obj"  # Replace with actual URL
    model_loader.import_format = 'OBJ'
    
    # Example: Connect nodes (this would be done manually in the UI normally)
    # You could programmatically create links if needed:
    # node_tree.links.new(image_send.outputs[0], executor_node.inputs[1])
    
    print("RunChat example node tree created!")
    print("Switch to the Shader Editor and select 'RunChatExample' to see the nodes.")
    return node_tree

def setup_runchat_workspace():
    """Set up a workspace optimized for RunChat workflows"""
    
    # Create a new workspace
    workspace_name = "RunChat Workflow"
    
    # Remove existing workspace if it exists
    if workspace_name in bpy.data.workspaces:
        bpy.data.workspaces.remove(bpy.data.workspaces[workspace_name])
    
    # Create new workspace based on Shading workspace
    shading_workspace = bpy.data.workspaces.get("Shading")
    if shading_workspace:
        new_workspace = shading_workspace.copy()
        new_workspace.name = workspace_name
        
        # Switch to the new workspace
        bpy.context.window.workspace = new_workspace
        
        print(f"Created '{workspace_name}' workspace for RunChat development")
    else:
        print("Could not find Shading workspace to copy from")

def render_and_send_to_runchat():
    """Example function showing how to render and send to RunChat"""
    
    # Ensure we have a camera and object to render
    if not bpy.context.scene.camera:
        print("No camera found, creating one...")
        bpy.ops.object.camera_add(location=(7, -7, 5))
        bpy.context.scene.camera = bpy.context.object
    
    # Quick render
    print("Rendering current scene...")
    bpy.ops.render.render()
    
    # Get the render result as base64 (using our utils)
    try:
        from . import utils
        render_base64 = utils.get_active_render_image()
        if render_base64:
            print(f"Render captured, size: {len(render_base64)} characters")
            # This could then be sent to a RunChat workflow
        else:
            print("Failed to capture render")
    except ImportError:
        print("RunChat addon not loaded, cannot access utils")

def test_image_workflow():
    """Test image input/output workflow"""
    
    # Create a test image in Blender
    test_image = bpy.data.images.new("TestImage", 512, 512)
    test_image.generated_type = 'UV_GRID'
    test_image.generated_width = 512
    test_image.generated_height = 512
    
    print("Created test image for workflow testing")
    
    # You could save this and use it with the Image Send node
    test_path = "/tmp/runchat_test_image.png"
    test_image.filepath_raw = test_path
    test_image.file_format = 'PNG'
    test_image.save()
    
    print(f"Saved test image to: {test_path}")
    return test_path

def inspect_runchat_nodes():
    """Inspect available RunChat node types"""
    
    try:
        # This would work if the addon is loaded
        import nodeitems_utils
        
        print("Available RunChat Node Categories:")
        categories = nodeitems_utils._node_categories.get("RUNCHAT_NODES", [])
        
        for category in categories:
            print(f"  Category: {category.name}")
            for item in category.items(None):
                print(f"    - {item.label} ({item.nodetype})")
                
    except Exception as e:
        print(f"Could not inspect nodes: {e}")
        print("Make sure the RunChat addon is enabled")

def main():
    """Main function to run all examples"""
    print("=== RunChat Blender Addon Examples ===")
    
    # Check if addon is enabled
    addon_name = "runchat_blender"  # This should match your addon's module name
    if addon_name not in bpy.context.preferences.addons:
        print(f"Warning: {addon_name} addon not found or not enabled")
        print("Please enable the RunChat Blender addon first")
        return
    
    print("RunChat addon detected!")
    
    # Run examples
    inspect_runchat_nodes()
    print()
    
    setup_runchat_workspace()
    print()
    
    create_runchat_example()
    print()
    
    test_path = test_image_workflow()
    print()
    
    render_and_send_to_runchat()
    
    print("\n=== Examples Complete ===")
    print("Check the RunChat Workflow workspace and RunChatExample node tree")

if __name__ == "__main__":
    main() 