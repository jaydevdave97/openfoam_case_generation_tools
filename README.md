# Boundary File Converter for OpenFOAM

This Python script (`01_boudry file_match_wall_to_cyclic.py`) converts internal wall boundaries to cyclic patches in OpenFOAM boundary files created from Fluent meshes.

## Introduction

When users import a Fluent mesh with multiple bodies and internal faces into OpenFOAM using `fluent3DToFoam`, the converter creates shadow faces for internal walls, but sets all boundaries to type "wall" by default. This script automatically:

1. Identifies internal wall boundaries (named with "inner_wall" prefix)
2. Changes them from type "wall" to type "cyclic"
3. Adds appropriate "neighbourPatch" entries to matching pairs
4. Formats the entries correctly with OpenFOAM syntax

## Context

When working with Fluent meshes that have multiple bodies and internal faces:
- Fluent creates shadow faces for internal boundaries using the TUI "slit face" command
- These shadow faces are named with a "-slit" suffix in the mesh
- When converted to OpenFOAM using `fluent3DToFoam`, all boundaries are set as "wall" type
- For proper OpenFOAM simulation, internal faces should be "cyclic" type with proper "neighbourPatch" connections

## Dependencies

- Python 3.x
- No external libraries required

## Usage

1. Copy the script to the directory containing your OpenFOAM boundary file
2. Run the script:

```bash
python "02_boudry file_match_cyclic.py"
```

By default, the script looks for a file named "boundary" in the current directory. You can specify a different file path as a command-line argument:

```bash
python "02_boudry file_match_cyclic.py" path/to/your/boundary/file
```

## What the Script Does

The script performs these operations:

1. Creates a backup of your original boundary file as "original_boundary"
2. Scans the file for blocks that start with "inner_wall"
3. For each matching pair of blocks (with/without "-slit" suffix):
   - Changes "type wall" to "type cyclic"
   - Removes "inGroups 1(wall);" line
   - Adds "neighbourPatch" entry pointing to the matching block
   - Adds/maintains "matchTolerance 2;" and "transform unknown;" entries
4. Formats all entries with consistent spacing and alignment
5. Preserves all other blocks unchanged
6. Saves the modified file back to the original location

## Example Transformation

**Before:**
```
inner_wall_filter_clean_gas_1_a-slit
{
    type            wall;
    inGroups        1(wall);
    nFaces          17076;
    startFace       19902924;
}
```

**After:**
```
inner_wall_filter_clean_gas_1_a-slit
{
    type            cyclic;
    neighbourPatch  inner_wall_filter_clean_gas_1_a;
    nFaces          17076;
    startFace       19902924;
    matchTolerance  2;
    transform       unknown;
}
```

## Naming Conventions

The script relies on specific naming conventions:
- All internal faces must have names starting with "inner_wall"
- Fluent shadow faces must have "-slit" suffix in their names
- Each "-slit" face must have a corresponding face without the suffix

## Note

Always verify the modified boundary file before running your OpenFOAM case to ensure boundaries are correctly configured.
