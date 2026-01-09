import os


def split_level(level_string: str, width: int) -> list[str]:
    """
    Split a Mario level string vertically into partial levels of a given width.
    
    The level is trimmed to the playable area (between { and } markers),
    split by width, and then each part gets the start/end columns added back.
    Partial levels that don't reach the full width are discarded.
    
    Args:
        level_string: The full level as a multi-line string
        width: The width of each partial level (for the middle section)
    
    Returns:
        List of partial level strings with consistent start/end columns
    """
    lines = level_string.strip('\n').split('\n')
    
    # Find the maximum width of the level
    max_width = max(len(line) for line in lines)
    
    # Pad all lines to the same width
    padded_lines = [line.ljust(max_width) for line in lines]
    
    # Find the column containing '{' (start marker)
    start_col = None
    for line in padded_lines:
        if '{' in line:
            start_col = line.index('{')
            break
    
    # Find the column containing '}' (end marker)
    end_col = None
    for line in padded_lines:
        if '}' in line:
            end_col = line.index('}')
            break
    
    if start_col is None or end_col is None:
        raise ValueError("Level must contain both '{' and '}' markers")
    
    # Extract prefix (columns up to and including '{')
    prefix_lines = [line[:start_col + 1] for line in padded_lines]
    
    # Extract suffix (columns from '}' to end)
    suffix_lines = [line[end_col:] for line in padded_lines]
    
    # Extract middle section (between '{' and '}')
    middle_lines = [line[start_col + 1:end_col] for line in padded_lines]
    middle_width = end_col - start_col - 1
    
    # Split middle section by width
    partial_levels = []
    
    for start in range(0, middle_width, width):
        end = start + width
        
        # Discard splits that don't make the full width
        if end > middle_width:
            break
        
        # Combine prefix + middle_chunk + suffix for each line
        combined_lines = [
            prefix_lines[i] + middle_lines[i][start:end] + suffix_lines[i]
            for i in range(len(padded_lines))
        ]
        partial_levels.append('\n'.join(combined_lines))
    
    return partial_levels


def process_level_files(file_paths: list[str], width: int, output_dir: str = "out") -> None:
    """
    Read levels from txt files, split them, and save to output directory.
    
    Args:
        file_paths: List of paths to level txt files
        width: The width of each partial level (for the middle section)
        output_dir: Directory to save output files (default: "out")
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    for file_path in file_paths:
        # Read level from file
        with open(file_path, 'r') as f:
            level_string = f.read()
        
        # Get the base filename without extension
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Split the level
        try:
            parts = split_level(level_string, width)
        except ValueError as e:
            print(f"Skipping {file_path}: {e}")
            continue
        
        if not parts:
            print(f"Skipping {file_path}: No splits of width {width} possible")
            continue
        
        # Save each part
        for i, part in enumerate(parts, 1):
            output_filename = f"{base_name}_split_{i}.txt"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w') as f:
                f.write(part)
            
            print(f"Saved: {output_path}")


# Example usage
if __name__ == "__main__":
    # List of level files to process
    # level_files = [
    #     "level1.txt",
    #     "level2.txt",
    #     "level3.txt",
    # ]
    
    import glob
    level_files = glob.glob("Super Mario Bros/Cleaned/*.txt")
    # level_files = glob.glob("Super Mario Bros 2 (Japan)/Cleaned/*.txt")
    
    # Process all files with width of 50
    process_level_files(level_files, width=50, output_dir="out")