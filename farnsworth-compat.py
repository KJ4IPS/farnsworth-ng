# Farnsworth compatability layer

# Classic farnsworth has the following classes:
# clock
# layer
#  +-- sprite
# sign

# layer:
# is_dirty() - Does the layer need to be redrawn
# blank(optional color) - clear the layer (optionaly with background color)
# get_pixel(x,y) - get a specific pixel 0,0 is bottom left (i think)
# read_pixel(x,y) - see get_pixel(x,y)
# set_pixel(x,y,color) - set the colorof a pixel, tuple  as (r,g,b) where each is ordinal number 0-255
# in_bounds(x,y) - returns true if the position specified is within the layer.
# paint_box(x1,y1,x2,y2,color) - draws a filled-in box
# translatecolor(color) - translate to device colorspace
# load_from_filename(filename,...(scale)) - load pixels from a file (by filename)
# load_from_image(filename,...(scale)) - load pixels from image data
# blit_image(filename,x,y) Blit an image onto the layer, at at specified format.
# serialize_data(), export data as a list of tuples, clear dirty
# blit(destlayer,dx,dy) - blit this layer onto another layer, at x,y
# glyph_witdth - get the width of a specified width
# render_glyph - render the specfied glyph at given position
# measure_string - return the length of a given string in a given font
# render_string - render a specified  string at the specified  location
# scroll_string - render a string, varying position with time
# render_twoline_string - Render two strings, with given fonts, colors, and values

# Sign is the main interface class for a hacklet
# sign:
# clean_shutdown - does it says on the tin
# handle_command_line - parse command line for --register and --time
# setup_properties - intialize properties
# register - print parameters to stdout. Used by the menu.
# locate_file - return the path of this file and the specified filename
# front_layer - return the front_layer
# back_layer - return the back_layer
# rule_clock - return the rule clock, it ticks every 'frame'
# paint_clock - ticks once a 'frame' with a max of 30 per seconde
# flip - swap the front and back layers
# paint - draw the front layer on the display (if needed) reutnrs true if the screen was drawn
# paint_once - draw the front layer, then return True
# paint_from_rule -  draw all pixels, using the output of a function
# fx_glitch_band - Apply  a glitcy effect of a band of  random from bottom to top
# fx_glitch_vsync - apply an  effect looking  like  broken vsync

# clock is a system base inteval timer
# clock:
# tick - returns true of the clock ticked since the last call ofthis function
# set_maximum_count - set the maximum count of the clock
# set_tick_latency - tick every n ms
# set_count_latency - increase the count every n ms, but only when ticking
# get_count - get the counter

# Sprite adds movement and animation to the basic layer
# sprite:




class FarnsworthClassicLayer:

    def __init__(self, width=0, height=0, filename=None, image=None, scale_x_to=None, scale_y_to=None, xparent_color=None):
        self._dirty = True 

