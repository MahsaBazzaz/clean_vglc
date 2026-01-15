"""
Mario Level Renderer
Converts character-based level representations into images using tile PNGs.
Reads level files from a directory using glob.
"""

from PIL import Image
import os
import glob

# Default tile size (can be adjusted based on your PNG sizes)
TILE_SIZE = 16

# Character to PNG filename mapping
CHAR_TO_PNG = {
    '-': '-.png',
    'X': 'X.png',
    'S': 'S.png',
    'Q': 'Q.png',
    '?': '?.png',
    'E': 'E.png',
    'H': 'H.png',
    '<': '<.png',
    '>': '>.png',
    '[': '[.png',
    ']': '].png',
    '{': '{.png',
    '}': '}.png',
    'G': 'G.png',
    'o': 'o.png',
    'P': 'P.png',
}


def load_tiles(tiles_folder, char_to_png):
    """
    Load all tile images from the specified folder.
    """
    tiles = {}
    
    for char, filename in char_to_png.items():
        filepath = os.path.join(tiles_folder, filename)
        if os.path.exists(filepath):
            tiles[char] = Image.open(filepath).convert('RGBA')
            print(f"Loaded tile for '{char}': {filename}")
        else:
            print(f"Warning: Missing tile for '{char}': {filepath}")
            tiles[char] = None
    
    return tiles


def create_placeholder_tiles(tile_size=16):
    """
    Create placeholder colored tiles for demonstration when PNGs are not available.
    """
    from PIL import ImageDraw
    
    tiles = {}
    
    colors = {
        '-': (135, 206, 235, 255),
        'X': (139, 69, 19, 255),
        'S': (205, 133, 63, 255),
        'Q': (255, 215, 0, 255),
        '?': (255, 215, 0, 255),
        'E': (165, 42, 42, 255),
        'H': (34, 139, 34, 255),
        '<': (0, 128, 0, 255),
        '>': (0, 128, 0, 255),
        '[': (0, 100, 0, 255),
        ']': (0, 100, 0, 255),
        '{': (128, 128, 128, 255),
        '}': (128, 128, 128, 255),
        ' ': (135, 206, 235, 255),
    }
    
    for char, color in colors.items():
        img = Image.new('RGBA', (tile_size, tile_size), color)
        draw = ImageDraw.Draw(img)
        
        if char in ['S', 'X']:
            draw.rectangle([1, 1, tile_size-2, tile_size-2], outline=(0, 0, 0, 100))
        elif char in ['Q', '?']:
            draw.rectangle([1, 1, tile_size-2, tile_size-2], outline=(0, 0, 0, 150))
            draw.text((tile_size//4, 2), "?", fill=(255, 255, 255, 255))
        elif char == 'E':
            draw.ellipse([2, 2, tile_size-3, tile_size-3], fill=(139, 69, 19, 255))
        elif char in ['<', '>']:
            draw.rectangle([0, tile_size//2, tile_size, tile_size], fill=(0, 100, 0, 255))
        
        tiles[char] = img
    
    return tiles


def render_level(level_string, tiles, tile_size=16):
    """
    Render the level from a character string using tile images.
    """
    lines = level_string.strip().split('\n')
    
    height = len(lines)
    width = max(len(line) for line in lines)
    
    print(f"  Level dimensions: {width} x {height} tiles")
    print(f"  Image dimensions: {width * tile_size} x {height * tile_size} pixels")
    
    SPRITE_CHARS = ['E']
    
    output = Image.new('RGBA', (width * tile_size, height * tile_size), (135, 206, 235, 255))
    
    # First pass: draw background/terrain tiles
    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            if char in SPRITE_CHARS:
                if '-' in tiles and tiles['-'] is not None:
                    sky = tiles['-']
                    if sky.size != (tile_size, tile_size):
                        sky = sky.resize((tile_size, tile_size), Image.NEAREST)
                    output.paste(sky, (col * tile_size, row * tile_size), sky)
                continue
            
            if char in tiles and tiles[char] is not None:
                tile = tiles[char]
                if tile.size != (tile_size, tile_size):
                    tile = tile.resize((tile_size, tile_size), Image.NEAREST)
                output.paste(tile, (col * tile_size, row * tile_size), tile)
            else:
                if '-' in tiles and tiles['-'] is not None:
                    sky = tiles['-']
                    if sky.size != (tile_size, tile_size):
                        sky = sky.resize((tile_size, tile_size), Image.NEAREST)
                    output.paste(sky, (col * tile_size, row * tile_size), sky)
    
    # Second pass: draw sprites/entities
    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            if char in SPRITE_CHARS and char in tiles and tiles[char] is not None:
                sprite = tiles[char]
                sprite_width, sprite_height = sprite.size
                
                x = col * tile_size + (tile_size - sprite_width) // 2
                y = (row + 1) * tile_size - sprite_height
                
                output.paste(sprite, (x, y), sprite)
    
    return output


def render_level_files(input_pattern: str, tiles_folder: str = "./tiles", 
                        output_dir: str = "out/images", tile_size: int = TILE_SIZE) -> None:
    """
    Read level files matching the pattern, render them, and save as images.
    
    Args:
        input_pattern: Glob pattern to match level txt files (e.g., "out/*.txt")
        tiles_folder: Path to folder containing PNG tiles
        output_dir: Directory to save rendered images
        tile_size: Size of each tile in pixels
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load tiles
    if os.path.exists(tiles_folder) and os.listdir(tiles_folder):
        print(f"Loading tiles from: {tiles_folder}")
        tiles = load_tiles(tiles_folder, CHAR_TO_PNG)
    else:
        print("Tiles folder not found or empty. Using placeholder colors.")
        tiles = create_placeholder_tiles(tile_size)
    
    # Find all level files
    level_files = sorted(glob.glob(input_pattern))
    
    if not level_files:
        print(f"No files found matching pattern: {input_pattern}")
        return
    
    print(f"\nFound {len(level_files)} level files to render")
    
    # Process each level file
    for file_path in level_files:
        print(f"\nProcessing: {file_path}")
        
        # Read level from file
        with open(file_path, 'r') as f:
            level_string = f.read()
        
        # Render the level
        level_image = render_level(level_string, tiles, tile_size)
        
        # Generate output filename (same name but .png extension)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.png")
        
        # Save the image
        level_image.save(output_path)
        print(f"  Saved: {output_path}")


def main():
    """Main function to render all Mario level files."""
    
    # Configuration
    # input_pattern = "out/*.txt"      # Pattern to match split level files
    # tiles_folder = "./tiles"          # Folder containing tile PNGs
    # output_dir = "out/images"         # Output folder for rendered images
    tile_size = TILE_SIZE

    input_pattern = "selected_levels/*.txt"      # Pattern to match split level files
    tiles_folder = "./tiles"          # Folder containing tile PNGs
    output_dir = "selected_levels/images"         # Output folder for rendered images
    
    render_level_files(input_pattern, tiles_folder, output_dir, tile_size)


if __name__ == "__main__":
    main()