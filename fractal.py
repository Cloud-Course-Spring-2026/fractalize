import numpy as np
from numba import jit

@jit(nopython=True, fastmath=True)
def compute_mandelbrot(height, width, x_min, x_max, y_min, y_max, max_iter):
    # Create an empty image array (Height x Width)
    img = np.zeros((height, width), dtype=np.uint8)
    
    # Calculate step sizes
    dx = (x_max - x_min) / width
    dy = (y_max - y_min) / height
    
    # Loop over pixels (JIT-compiled by numba)
    for y in range(height):
        for x in range(width):
            # Map pixel coordinate to complex plane
            c_r = x_min + x * dx
            c_i = y_min + y * dy
            z_r = 0.0
            z_i = 0.0
            
            # Escape time algorithm
            for i in range(max_iter):
                # z = z^2 + c
                # (a+bi)^2 = a^2 - b^2 + 2abi
                temp_r = z_r*z_r - z_i*z_i + c_r
                z_i = 2*z_r*z_i + c_i
                z_r = temp_r
                
                # Check escape condition |z| > 2 (z_r^2 + z_i^2 > 4)
                if z_r*z_r + z_i*z_i > 4.0:
                    # Simple coloring: map iterations to 0-255 brightness
                    img[y, x] = int(255 * i / max_iter)
                    break
                    
    return img
