"""
Mario Level Renderer
Converts a character-based level representation into an image using tile PNGs.
"""

from PIL import Image
import os

# The level data as a multi-line string
LEVEL_DATA = """----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------E-----------------------------------------------------------------------------------------------------------------------
----------------------Q---------------------------------------------------------SSSSSSSS---SSSQ--------------?-----------SSS----SQQS--------------------------------------------------------HH------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------HHH------------
-------------------------------------------------------------------------------E----------------------------------------------------------------------------------------------------------HHHH------------
----------------------------------------------------------------S------------------------------------------------------------------------------------------------------------------------HHHHH------------
----------------Q---S?SQS---------------------<>---------<>------------------S?S--------------S-----SS----Q--Q--Q-----S----------SS------H--H----------HH--H------------SSQS------------HHHHHH------------
--------------------------------------<>------[]---------[]-----------------------------------------------------------------------------HH--HH--------HHH--HH--------------------------HHHHHHH------------
----------------------------<>--------[]------[]---------[]----------------------------------------------------------------------------HHH--HHH------HHHH--HHH-----<>--------------<>-HHHHHHHH--------}---
---{-----------------E------[]--------[]-E----[]-----E-E-[]------------------------------------E-E--------E-----------------EE-E-E----HHHH--HHHH----HHHHH--HHHH----[]---------EE---[]HHHHHHHHH--------HH--
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX--XXXXXXXXXXXXXXX---XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX--XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"""


# Default tile size (can be adjusted based on your PNG sizes)
TILE_SIZE = 16

# Character to PNG filename mapping
# Modify these paths to match your actual PNG file locations
CHAR_TO_PNG = {
    '-': '-.png',           # Empty sky/background
    'X': 'X.png',        # Ground block
    'S': 'S.png',         # Brick block
    'Q': 'Q.png',      # Question block (with item)
    '?': '?.png',      # Question block (alternate notation)
    'E': 'E.png',         # Enemy (Goomba)
    'H': 'H.png',          # Hill/decoration
    '<': '<.png', # Pipe top left
    '>': '>.png',# Pipe top right
    '[': '[.png',# Pipe body left
    ']': '].png',# Pipe body right
    '{': '{.png', # Flag pole top / start marker
    '}': '}.png',     # Flag pole / end marker
    'G': 'G.png',        
    'o': 'o.png',
    'P': 'P.png',
    'X': 'X.png',
}


def load_tiles(tiles_folder, char_to_png):
    """
    Load all tile images from the specified folder.
    
    Args:
        tiles_folder: Path to folder containing PNG tiles
        char_to_png: Dictionary mapping characters to PNG filenames
    
    Returns:
        Dictionary mapping characters to PIL Image objects
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
    
    Args:
        tile_size: Size of each tile in pixels
    
    Returns:
        Dictionary mapping characters to PIL Image objects
    """
    from PIL import ImageDraw
    
    tiles = {}
    
    # Color definitions for each tile type (R, G, B, A)
    colors = {
        '-': (135, 206, 235, 255),    # Sky blue
        'X': (139, 69, 19, 255),      # Brown ground
        'S': (205, 133, 63, 255),     # Tan brick
        'Q': (255, 215, 0, 255),      # Gold question block
        '?': (255, 215, 0, 255),      # Gold question block
        'E': (165, 42, 42, 255),      # Brown enemy (Goomba)
        'H': (34, 139, 34, 255),      # Forest green hill
        '<': (0, 128, 0, 255),        # Green pipe
        '>': (0, 128, 0, 255),        # Green pipe
        '[': (0, 100, 0, 255),        # Dark green pipe body
        ']': (0, 100, 0, 255),        # Dark green pipe body
        '{': (128, 128, 128, 255),    # Gray flag pole
        '}': (128, 128, 128, 255),    # Gray flag pole
        ' ': (135, 206, 235, 255),    # Sky blue
    }
    
    for char, color in colors.items():
        img = Image.new('RGBA', (tile_size, tile_size), color)
        
        # Add some visual distinction
        draw = ImageDraw.Draw(img)
        
        if char in ['S', 'X']:
            # Add brick/ground pattern
            draw.rectangle([1, 1, tile_size-2, tile_size-2], outline=(0, 0, 0, 100))
        elif char in ['Q', '?']:
            # Add question mark indicator
            draw.rectangle([1, 1, tile_size-2, tile_size-2], outline=(0, 0, 0, 150))
            draw.text((tile_size//4, 2), "?", fill=(255, 255, 255, 255))
        elif char == 'E':
            # Enemy indicator
            draw.ellipse([2, 2, tile_size-3, tile_size-3], fill=(139, 69, 19, 255))
        elif char in ['<', '>']:
            # Pipe top highlight
            draw.rectangle([0, tile_size//2, tile_size, tile_size], fill=(0, 100, 0, 255))
        
        tiles[char] = img
    
    return tiles


def render_level(level_string, tiles, tile_size=16):
    """
    Render the level from a character string using tile images.
    Handles variable-height sprites by bottom-anchoring them to the grid.
    
    Args:
        level_string: Multi-line string representing the level
        tiles: Dictionary mapping characters to PIL Image objects
        tile_size: Size of each tile in pixels
    
    Returns:
        PIL Image of the rendered level
    """
    lines = level_string.strip().split('\n')
    
    # Calculate dimensions
    height = len(lines)
    width = max(len(line) for line in lines)
    
    print(f"Level dimensions: {width} x {height} tiles")
    print(f"Image dimensions: {width * tile_size} x {height * tile_size} pixels")
    
    # Define which characters are sprites (may have non-standard sizes)
    SPRITE_CHARS = ['E']  # Add other sprite characters here if needed
    
    # Create the output image
    output = Image.new('RGBA', (width * tile_size, height * tile_size), (135, 206, 235, 255))
    
    # First pass: draw background/terrain tiles (sky, ground, bricks, etc.)
    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            # For sprite positions, draw sky background first
            if char in SPRITE_CHARS:
                if '-' in tiles and tiles['-'] is not None:
                    sky = tiles['-']
                    if sky.size != (tile_size, tile_size):
                        sky = sky.resize((tile_size, tile_size), Image.NEAREST)
                    output.paste(sky, (col * tile_size, row * tile_size), sky)
                continue
            
            # Draw normal tiles
            if char in tiles and tiles[char] is not None:
                tile = tiles[char]
                # Resize standard tiles to grid size
                if tile.size != (tile_size, tile_size):
                    tile = tile.resize((tile_size, tile_size), Image.NEAREST)
                output.paste(tile, (col * tile_size, row * tile_size), tile)
            else:
                # Use sky color for unknown characters
                if '-' in tiles and tiles['-'] is not None:
                    sky = tiles['-']
                    if sky.size != (tile_size, tile_size):
                        sky = sky.resize((tile_size, tile_size), Image.NEAREST)
                    output.paste(sky, (col * tile_size, row * tile_size), sky)
    
    # Second pass: draw sprites/entities (may overflow upward from their cell)
    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            if char in SPRITE_CHARS and char in tiles and tiles[char] is not None:
                sprite = tiles[char]
                sprite_width, sprite_height = sprite.size
                
                # Bottom-anchor: sprite's bottom aligns with cell's bottom
                # Horizontally centered in the cell
                x = col * tile_size + (tile_size - sprite_width) // 2
                y = (row + 1) * tile_size - sprite_height
                
                output.paste(sprite, (x, y), sprite)
    
    return output


def main():
    """Main function to render the Mario level."""
    
    # Configuration
    tiles_folder = "./tiles"  # Change this to your tiles folder path
    output_file = "Super Mario Bros/Cleaned/mario-1-1.txt.png"
    tile_size = TILE_SIZE
    
    # Check if tiles folder exists
    if os.path.exists(tiles_folder) and os.listdir(tiles_folder):
        print(f"Loading tiles from: {tiles_folder}")
        tiles = load_tiles(tiles_folder, CHAR_TO_PNG)
    else:
        print("Tiles folder not found or empty. Using placeholder colors.")
        tiles = create_placeholder_tiles(tile_size)
    
    # Render the level
    print("\nRendering level...")
    level_image = render_level(LEVEL_DATA, tiles, tile_size)
    
    # Save the output
    level_image.save(output_file)
    print(f"\nLevel saved to: {output_file}")
    
    return level_image, output_file


if __name__ == "__main__":
    main()