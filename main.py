#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import os
import sys

class CrosshairOverlay(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Crosshair Overlay")
        
        # Set up the window
        self.set_keep_above(True)  # Keep window on top
        self.set_decorated(False)  # Remove window decorations
        self.set_app_paintable(True)  # Allow custom drawing
        self.set_position(Gtk.WindowPosition.CENTER)  # Center on screen
        
        # Load the crosshair image
        self.crosshair_path = os.path.abspath("crosshair.png")
        if not os.path.exists(self.crosshair_path):
            print(f"Error: Crosshair image not found at {self.crosshair_path}")
            sys.exit(1)
        
        # Try to load the image
        try:
            self.original_pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.crosshair_path)
            self.current_size = 100  # Default size percentage
            self.image = Gtk.Image()
            self.update_image_size()
        except Exception as e:
            print(f"Error loading image: {e}")
            sys.exit(1)
            
        # Set up the window for transparency
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        
        # Set up a container for the image
        self.box = Gtk.Box()
        self.add(self.box)
        self.box.pack_start(self.image, True, True, 0)
        
        # Connect signals for movement and scrolling
        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("scroll-event", self.on_scroll)
        
        # Setup for window dragging
        self.dragging = False
        self.drag_x = 0
        self.drag_y = 0
        
        # Set up keyboard shortcuts
        self.connect("key-press-event", self.on_key_press)
        
        # Show all window components
        self.show_all()
    
    def update_image_size(self):
        # Calculate new dimensions based on current_size percentage
        orig_width = self.original_pixbuf.get_width()
        orig_height = self.original_pixbuf.get_height()
        new_width = int(orig_width * self.current_size / 100)
        new_height = int(orig_height * self.current_size / 100)
        
        # Scale the image
        scaled_pixbuf = self.original_pixbuf.scale_simple(new_width, new_height, 
                                                         GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(scaled_pixbuf)
        
        # Resize the window to fit the image
        self.resize(new_width, new_height)
    
    def on_scroll(self, widget, event):
        # Change size on scroll
        if event.direction == Gdk.ScrollDirection.UP:
            # Increase size
            self.current_size += 5
        elif event.direction == Gdk.ScrollDirection.DOWN:
            # Decrease size, but don't go below 10%
            self.current_size = max(10, self.current_size - 5)
        
        self.update_image_size()
        return True
    
    def on_button_press(self, widget, event):
        if event.button == 1:  # Left mouse button
            self.dragging = True
            self.drag_x = event.x
            self.drag_y = event.y
        return True
    
    def on_button_release(self, widget, event):
        if event.button == 1:  # Left mouse button
            self.dragging = False
        return True
    
    def on_motion_notify(self, widget, event):
        if self.dragging:
            x, y = self.get_position()
            self.move(int(x + event.x - self.drag_x), int(y + event.y - self.drag_y))
        return True
    
    def on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Escape':
            Gtk.main_quit()
        elif keyname == 'plus' or keyname == 'equal':
            # Increase size
            self.current_size += 10
            self.update_image_size()
        elif keyname == 'minus':
            # Decrease size
            self.current_size = max(10, self.current_size - 10)
            self.update_image_size()
        return True

def main():
    # Create and show the window
    win = CrosshairOverlay()
    win.connect("destroy", Gtk.main_quit)
    
    # Set up transparency
    win.set_app_paintable(True)
    win.set_visual(win.get_screen().get_rgba_visual())
    
    # Make the window receive events
    win.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | 
                  Gdk.EventMask.BUTTON_RELEASE_MASK | 
                  Gdk.EventMask.POINTER_MOTION_MASK |
                  Gdk.EventMask.SCROLL_MASK)
    
    # Run the application
    Gtk.main()

if __name__ == "__main__":
    main()