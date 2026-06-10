from flask import Flask, render_template, Response, request, jsonify
import cv2

app = Flask(__name__)

camera = cv2.VideoCapture(0)

current_settings = {
    "width": 640,
    "height": 480,
    "fps": 15
}

def apply_camera_settings():
    """Pushes the current dictionary settings to the camera hardware."""
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, current_settings["width"])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, current_settings["height"])
    camera.set(cv2.CAP_PROP_FPS, current_settings["fps"])

apply_camera_settings()

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """API endpoint to receive and apply new settings from the frontend."""
    data = request.json
    
    if 'resolution' in data:
        res = data['resolution'].split('x')
        if len(res) == 2:
            current_settings["width"] = int(res[0])
            current_settings["height"] = int(res[1])
            
    if 'fps' in data:
        current_settings["fps"] = int(data['fps'])
        
    apply_camera_settings()
    
    return jsonify({"status": "success", "settings": current_settings})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
