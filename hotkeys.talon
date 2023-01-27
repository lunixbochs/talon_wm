# split screen
key(ctrl-alt-cmd-up):    user.snap_split('top')
key(ctrl-alt-cmd-down):  user.snap_split('bottom')
key(ctrl-alt-cmd-left):  user.snap_split('left')
key(ctrl-alt-cmd-right): user.snap_split('right')

key(ctrl-alt-cmd-pageup):   user.snap_split('top-left')
key(ctrl-alt-cmd-pagedown): user.snap_split('bottom-right')
key(ctrl-alt-cmd-home):     user.snap_split('bottom-left')
key(ctrl-alt-cmd-end):      user.snap_split('top-right')

# maximize / center
key(ctrl-alt-cmd-f): user.snap_toggle_fullscreen()
key(ctrl-alt-cmd-m): user.snap_toggle_maximize()
key(ctrl-alt-cmd-c): user.snap_toggle_center()

# send to screen
key(ctrl-alt-left):  user.snap_next_screen()
key(ctrl-alt-right): user.snap_prev_screen()

# snap to grid
key(ctrl-alt-cmd-;): user.snap_grid()
key(ctrl-alt-cmd-'): user.snap_all()

# grid resizing
key(ctrl-alt-cmd-h): user.snap_shift('left')
key(ctrl-alt-cmd-k): user.snap_shift('up')
key(ctrl-alt-cmd-j): user.snap_shift('down')
key(ctrl-alt-cmd-l): user.snap_shift('right')

key(ctrl-alt-cmd-y): user.snap_grow('left')
key(ctrl-alt-cmd-u): user.snap_grow('down')
key(ctrl-alt-cmd-i): user.snap_grow('up')
key(ctrl-alt-cmd-o): user.snap_grow('right')

key(ctrl-alt-cmd-shift-y): user.snap_shrink('left')
key(ctrl-alt-cmd-shift-u): user.snap_shrink('down')
key(ctrl-alt-cmd-shift-i): user.snap_shrink('up')
key(ctrl-alt-cmd-shift-o): user.snap_shrink('right')
