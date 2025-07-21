import time
import directpx

# Init overlay with full screen size
w, h = directpx.get_screen_size(1)  # 1 = primary monitor
directpx.init(w, h)

# Draw translucent white box
directpx.clear()
directpx.draw_box(100, 100, 200, 200, 255, 255, 255, 128)
directpx.update()

time.sleep(2)
directpx.close()
