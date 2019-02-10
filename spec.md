# Png-parser

## Nomenclature

 - PNG
 - Chunks ID
 - Chunks
 - Scanline (Pass)
 - Filter ID
 - Image Data
    + Image Row
    + Encoded Pixel
 - Real Image
    + Pixel


## PNG Loading

 - Open file
    + check Magic number
 - Read chunks
 - Load PNG metadata:
    + Header
    + Palette
    + ...
 - Load Image Data
    + Image Row
    + Image and Pixels

### Saving

 - Image to Image Data
    + Update palette if needed
 - Image Data to bytes
 - bytes to IDAT chunk(s)
 - Update chunks
 - Save all chunks in bytes to a file
