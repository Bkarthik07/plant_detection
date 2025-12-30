import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image
import io

# Set up Flask app
app = Flask(__name__)

# Configure the API key for Google Generative AI (Gemini)
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Define the route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define the route to process the uploaded image and get information
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided!"}), 400

    image_file = request.files['image']

    # Read and process the image
    image = Image.open(image_file.stream)

    # Convert the image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Create a prompt for the Gemini model
    prompt = ["Given the image of the plant, identify its name, description, rarity, medical properties, physical properties, smell, usage, and any fun facts or interesting details about it.", image]

    try:
        # Send the prompt to the Gemini API
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        plant_info = (response.text).replace("**", "")  # The plant's detailed description

        return jsonify({"plant_info": plant_info})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel serverless function handler
def vercel_handler(request):
    with app.app_context():
        response = app.test_client().get(request.path, query_string=request.args)
        return response.get_data(), response.status_code, response.headers.items()

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=False)
