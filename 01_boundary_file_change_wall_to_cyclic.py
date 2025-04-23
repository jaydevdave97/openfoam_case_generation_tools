#!/usr/bin/env python3
"""
Script to read an OpenFOAM boundary file and:
1. Add neighbourPatch entries to matching blocks with -slit suffix and their corresponding non-slit blocks
2. Change the type from 'wall' to 'cyclic' for blocks starting with 'inner_wall'
3. Add matchTolerance and transform lines to inner_wall blocks
4. Remove inGroups line from inner_wall blocks
5. Only modify inner_wall* blocks, not wall_* blocks
6. Properly align all property values
"""

import re
import os
import sys
import shutil

def process_boundary_file(file_path):
    """
    Process the boundary file to:
    1. Add neighbourPatch entries to matching blocks
    2. Change the type from 'wall' to 'cyclic' for inner_wall blocks
    3. Add matchTolerance and transform lines
    4. Remove inGroups line
    5. Ensure proper alignment of all values
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False
    
    # Create a backup of the original file
    backup_file = "original_boundary"
    print(f"Creating backup of original file as: {backup_file}")
    shutil.copy2(file_path, backup_file)
    
    # Read the boundary file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Regular expression to find and capture the entire block
    block_pattern = r'(\s*)([a-zA-Z0-9_.-]+)(\s*\n\s*{)([^}]*)(\s*}\s*)'
    
    # Process each block
    blocks = re.findall(block_pattern, content, re.DOTALL)
    modified_content = content
    
    changes_made = []
    
    # Process each block
    for indent, block_name, block_start, block_content, block_end in blocks:
        # Only process inner_wall* blocks
        if not block_name.startswith('inner_wall'):
            continue
            
        block_original = indent + block_name + block_start + block_content + block_end
        
        # Check if this is a slit block or a potential matching non-slit block
        is_slit = block_name.endswith('-slit')
        non_slit_name = block_name[:-5] if is_slit else None
        matching_slit_name = block_name + "-slit" if not is_slit else None
        
        # Determine the matching block name
        matching_name = non_slit_name if is_slit else matching_slit_name
        
        # Skip if there's no matching name (not a -slit or potential matching block)
        if matching_name is None:
            continue
        
        # 3. Extract nFaces and startFace values to preserve them
        nfaces_match = re.search(r'nFaces\s+(\d+);', block_content)
        startface_match = re.search(r'startFace\s+(\d+);', block_content)
        
        nfaces_value = nfaces_match.group(1) if nfaces_match else ""
        startface_value = startface_match.group(1) if startface_match else ""
        
        # 4. Create new block content with all the required elements in correct order AND proper alignment
        new_block_content = f"""
        type            cyclic;
        neighbourPatch  {matching_name};
        nFaces          {nfaces_value};
        startFace       {startface_value};
        matchTolerance  2;
        transform       unknown;
"""
        
        # 5. Create the new block
        new_block = indent + block_name + block_start + new_block_content + block_end
        
        # 6. Replace the old block with the new one
        modified_content = modified_content.replace(block_original, new_block)
        changes_made.append(f"Updated block {block_name} with proper alignment and formatting")
    
    # Write the modified content back to the file
    with open(file_path, 'w') as f:
        f.write(modified_content)
    
    # Print changes
    if changes_made:
        print(f"Successfully modified boundary file: {file_path}")
        print("Changes made:")
        for change in changes_made:
            print(f"- {change}")
    else:
        print("No changes were needed.")
    
    return True

def main():
    # Default boundary file path
    boundary_file = 'boundary'
    
    # Allow specifying a different file path as command-line argument
    if len(sys.argv) > 1:
        boundary_file = sys.argv[1]
    
    print(f"Processing boundary file: {boundary_file}")
    process_boundary_file(boundary_file)

if __name__ == "__main__":
    main()
