import cairo
from hashlib import md5
from latex2svg import latex2svg as l2s, default_params
from gi.repository import Rsvg
import subprocess
from math import ceil
from transition import Constant
from os.path import isfile

class Manager:
    def __init__(s, width, height, fps=30):
        s.width = width
        s.height = height
        s.fps = fps
        s.frame = 0
        s.clear_renderables()
        
    def clear_renderables(s):
        s.renderable_list = []
        
    def add(s, renderable, transition=None):
        s.renderable_list.append(renderable)
        renderable.t_0 = s.frame

    def clear_frame(s, color=None):
        s.clear_renderables()
        if color is not None:
            s.background_color = color
    
    def render(s, length):
        starting_frame = s.frame
        while starting_frame + length * s.fps > s.frame:
            s.render_frame()
            s.frame += 1
    
    def render_frame(s):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, s.width, s.height)
        ctx = cairo.Context(surface)

        ctx.scale(s.width, s.height)  # Normalizing the canvas
        
        ctx.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)
        ctx.set_source_rgb(*s.background_color)
        ctx.fill()
        
        for renderable in s.renderable_list:
            renderable.render(ctx, s.frame / float(s.fps))
        
        filename = "./tmp/fake_{:0>5}.png".format(s.frame)
        surface.write_to_png(filename)  # Output to PNG
        surface.finish()
    
    def convert_to_video(s, out):
        # command is "ffmpeg -i fake_%05d.png video.mp4"
        # overwrite out with -y
        subprocess.call(["ffmpeg", "-i", "./tmp/fake_%05d.png", "-y", out])
        
class Latex:
    def __init__(s, latex_source, cpos=(0, 0), height=1, alpha=1, color=(0,0,0)):
        s.latex_source = latex_source
        s.cpos = s.sanitize_constant(cpos)
        s.height = s.sanitize_constant(height)
        s.alpha = s.sanitize_constant(alpha)
        s.color = s.sanitize_constant(color)
        s.make_svg()
    
    def sanitize_constant(s, val):
        if not hasattr(val, '__call__'):
            return Constant(val)
        else:
            return val
    
    def make_svg(s):
        m = md5()
        m.update(s.latex_source.encode('utf-8'))
        s.hexdigest = m.hexdigest()
        # if it already exists, don't make it again.
        # oh wait i need the parsed data... hmm..
        #if isfile("./tmp/" + s.hexdigest + ".svg"):
        #    return
        s.my_params = default_params
        s.my_params['filename'] = s.hexdigest
        s.svg_out = l2s(s.latex_source, params=s.my_params, working_directory="./tmp")
        
    def render(s, ctx, t):
        ctx.save()
        ctx.identity_matrix()
        
        # first, collect the information on the height and width
        # not sure what the 1.25 means but it's good
        svg_height = s.my_params['fontsize'] * s.svg_out['height'] * 1.25
        svg_width = s.my_params['fontsize'] * s.svg_out['width'] * 1.25
        
        # then, determine the scaling factor
        clip_x, clip_y, clip_w, clip_h = ctx.clip_extents()
        scaling_factor = s.height(t) * clip_h / float(svg_height)
        
        # render the svg
        ltx_surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32,
            ceil(svg_width * scaling_factor),
            ceil(svg_height * scaling_factor)
        )

        ltx_context = cairo.Context(ltx_surface)
        ltx_context.scale(scaling_factor, scaling_factor)
        
        handle = Rsvg.Handle()
        svg = handle.new_from_file("./tmp/" + s.hexdigest + ".svg")
        svg.render_cairo(ltx_context)
        svg.close()
        
        # render bounding box too.
        #ltx_context.rectangle(0, 0, svg_width, svg_height)
        #ltx_context.set_source_rgb(0.3, 0.2, 0.5)  # Solid color
        #ltx_context.set_line_width(1)
        #ltx_context.stroke()
        
        # calculate the source offset, in pixels
        # the target cposx times pixesl minus width in ctx pixels divided by two
        x_offset = clip_w * s.cpos(t)[0] - (svg_width * scaling_factor)/2.
        y_offset = clip_h * s.cpos(t)[1] - (svg_height * scaling_factor)/2.
        
        r, g, b = s.color(t)
        ctx.set_source_rgba(r, g, b, s.alpha(t))
        ctx.mask_surface(ltx_surface, x_offset, y_offset)
        
        #ctx.set_source_surface(ltx_surface, x_offset, y_offset)
        #ctx.paint_with_alpha(s.alpha(t))

        ctx.restore()
    
    def add_transition(s, **transition):
        for k in transition:
            setattr(s, k, transition[k])
        

class Rectangle:
    def __init__(s, cpos=(0,0), height=1, width=1, alpha=1,
                 equiaxial=None, color=(0,0,0), linewidth=0.01,
                 fill=False, rot=0):
        s.cpos = s.sanitize_constant(cpos)
        s.height = s.sanitize_constant(height)
        s.width = s.sanitize_constant(width)
        s.alpha = s.sanitize_constant(alpha)
        s.equiaxial = equiaxial
        s.color = color
        s.linewidth = linewidth
        s.fill = fill
        s.rot = s.sanitize_constant(rot)
    
    def add_transition(s, **transition):
        for k in transition:
            setattr(s, k, transition[k])
        
    def sanitize_constant(s, val):
        if not hasattr(val, '__call__'):
            return Constant(val)
        else:
            return val
    
    def render(s, ctx, t):
        ctx.save()
        ctx.identity_matrix()
        
        clip_x, clip_y, clip_w, clip_h = ctx.clip_extents()
        
        if s.equiaxial == 'smaller':
            # scale by the smaller value and translate.
            smaller = min(clip_w, clip_h)
            ctx.translate((clip_w-smaller)/2., (clip_h-smaller)/2.)
            ctx.scale(smaller, smaller)
            
        # maybe rotate some too, but also try to keep cpos in the same spot.
        ctx.translate(s.cpos(t)[0], s.cpos(t)[1])
        ctx.rotate(s.rot(t))
        ctx.translate(-s.cpos(t)[0], -s.cpos(t)[1])
        
            
        ctx.rectangle(
            s.cpos(t)[0] - s.width(t)/2.,
            s.cpos(t)[1] - s.height(t)/2.,
            s.width(t),
            s.height(t)
        )
        
        r, g, b = s.color
        ctx.set_source_rgba(r, g, b, s.alpha(t))  # Solid color
        if s.fill:
            ctx.fill()
        else:
            ctx.set_line_width(s.linewidth)
            ctx.stroke()
            
        
        ctx.restore()
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        