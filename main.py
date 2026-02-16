from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from PIL import Image
from io import BytesIO
import numpy as np
import fractal  # Import our numba module

app = FastAPI()

# Config
WIDTH = 800
HEIGHT = 600
MAX_ITER = 64

@app.get("/")
def index():
    # Simple UI to display the image and handle clicks
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mandelbrot Explorer</title>
        <style>
            body { background: #1a1a1a; color: white; text-align: center; font-family: sans-serif; }
            canvas { border: 1px solid #555; cursor: crosshair; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        </style>
    </head>
    <body>
        <h2>Mandelbrot Explorer</h2>
        <p>Click to Zoom In | Right Click to Zoom Out | R to Reset</p>
        <img id="view" src="/render?xmin=-2.5&xmax=1.5&ymin=-1.5&ymax=1.5" width="800" height="600" />
        
        <script>
            const initialState = { xmin: -2.5, xmax: 1.5, ymin: -1.5, ymax: 1.5 };
            let state = { ...initialState };
            const img = document.getElementById('view');

            function update() {
                img.src = `/render?xmin=${state.xmin}&xmax=${state.xmax}&ymin=${state.ymin}&ymax=${state.ymax}&t=${Date.now()}`;
            }

            function getClickCoords(e) {
                // Calculate where user clicked relative to image
                const rect = img.getBoundingClientRect();
                const xPct = (e.clientX - rect.left) / rect.width;
                const yPct = (e.clientY - rect.top) / rect.height;

                // Map to complex coordinates
                const xWidth = state.xmax - state.xmin;
                const yHeight = state.ymax - state.ymin;
                const clickX = state.xmin + (xPct * xWidth);
                const clickY = state.ymin + (yPct * yHeight);
                return { clickX, clickY, xWidth, yHeight };
            }

            img.addEventListener('click', (e) => {
                const { clickX, clickY, xWidth, yHeight } = getClickCoords(e);

                // Zoom in (0.5x scale)
                const newWidth = xWidth * 0.5;
                const newHeight = yHeight * 0.5;

                state.xmin = clickX - newWidth / 2;
                state.xmax = clickX + newWidth / 2;
                state.ymin = clickY - newHeight / 2;
                state.ymax = clickY + newHeight / 2;
                
                update();
            });

            img.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                const { clickX, clickY, xWidth, yHeight } = getClickCoords(e);

                // Zoom out (2x scale)
                const newWidth = xWidth * 2.0;
                const newHeight = yHeight * 2.0;

                state.xmin = clickX - newWidth / 2;
                state.xmax = clickX + newWidth / 2;
                state.ymin = clickY - newHeight / 2;
                state.ymax = clickY + newHeight / 2;

                update();
            });

            window.addEventListener('keydown', (e) => {
                if (e.key === 'r' || e.key === 'R') {
                    state = { ...initialState };
                    update();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/render")
def render(xmin: float, xmax: float, ymin: float, ymax: float):
    # 1. Run the Number Cruncher
    # We use numpy to create a colorful image from the raw iteration counts
    raw_data = fractal.compute_mandelbrot(HEIGHT, WIDTH, xmin, xmax, ymin, ymax, MAX_ITER)
    
    # 2. Colorize (Apply a simple "Hot" colormap)
    # This turns our 2D array into a 3D array (H, W, 3) for RGB
    # PIL expects uint8 for an RGB image (H, W, 3). Using int32 raises:
    # TypeError: Cannot handle this data type: (1, 1, 3), <i4
    image_rgb = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    image_rgb[..., 0] = raw_data  # Red channel
    image_rgb[..., 1] = raw_data * 2  # Green channel
    image_rgb[..., 2] = raw_data * 4  # Blue channel

    # 3. Convert to PNG
    img = Image.fromarray(image_rgb, mode="RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    
    return Response(content=buf.getvalue(), media_type="image/png")
