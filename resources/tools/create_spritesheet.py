# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from argparse import ArgumentParser
import Image
import os

if __name__ == '__main__':
    parser = ArgumentParser(description='Convert a set of png images to an png spritesheet')

    parser.add_argument('files', metavar='FILE', type=unicode, nargs='+', help='List of files to be added to spritesheet (patterns allowed).')
    parser.add_argument('--max-tiles-per-row', metavar='TILES', type=int, default=32, nargs='?', help='Number of tiles that will be put on a single row. Defaults to 32.')
    parser.add_argument('--size', metavar=('WIDTH', 'HEIGHT'), type=int, default=None, nargs=2, help='Width and height of basic tile. Defaults to LARGER tile sizes.')
    parser.add_argument('--resize', default=False, action='store_true', help='Resize images to fit into size (not used if --size is not speficied).')
    parser.add_argument('--output', type=unicode, default='spritesheet.png', nargs='?', help='Ouput spritesheet name. Defaults to spritesheet.png.')
    parser.add_argument('--verbose', default=False, action='store_true', help='Print useful information of generation process')
    parser.add_argument('--dry', default=False, action='store_true', help='Runs in dry mode (do not generates output file)')
    
    args = parser.parse_args()
    
    print('Converter of png to sprite sheet')
    
    # First pass gets width/heights of all files

    if args.size is not None:
        width, height = args.size
    else:
        args.resize = False
        width, height = 0, 0
    images = []
    for f in args.files:
        im = Image.open(f)
        
        if args.verbose:
            print('* Processiong {}: {} {}'.format(os.path.basename(f), im.format, im.size))
        
        if args.size is None:
            if width < im.size[0]:
                width = im.size[0]
            if height < im.size[1]:
                height = im.size[1]
        if args.resize:
            if args.verbose:
                print '    - Resizing to {}x{}'.format(width, height)
            im.thumbnail((width, height), Image.ANTIALIAS)
            tmp = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            offset = ((width-im.size[0])/2, (height-im.size[1])/2)
            tmp.paste(im, offset)
            im = tmp
        if args.verbose:
            bbox = im.getbbox()
            print '    - Bounding image box is ({}, {}, {}, {})'.format(
                bbox[0], bbox[1], bbox[2]-bbox[0], bbox[3]-bbox[1]
            )
            print im.size
        images.append(im)
        
    print 'Generating spritesheet {} from list width at most {} tiles in a row, a size of {}x{} pixels {}'.format(
        args.output, args.max_tiles_per_row, width, height, 'and that will be resized' if args.resize else ''
    )

    cols = args.max_tiles_per_row if len(images) > args.max_tiles_per_row else len(images)

    rows = (len(images) + cols - 1) // cols
    
    output = Image.new('RGBA', (cols * width, rows * height), (255, 255, 255, 0))
    
    col, row = 0, 0
    for im in images:
        output.paste(im, (col*width, row*height))
        col += 1
        if col >= cols:
            col = 0
            row += 1
            
    if not args.dry:
        output.save(args.output)
    else:
        print('Output filename not generated (dry run)')