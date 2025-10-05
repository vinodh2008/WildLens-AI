from flask import Flask, request, jsonify, render_template
import numpy as np
import cv2
import requests
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from PIL import Image
import io

app = Flask(__name__)

# --- Load Model ---
def load_model():
    return VGG16(weights="imagenet")

model = load_model()

def extract_relevant_facts(text, animal_name):
    """Extracts key facts, and only shows a danger warning if it is confirmed and not negated."""
    sentences = text.split('. ')
    
    habitat_keywords = ["habitat", "range", "found in", "lives in", "native to", "distribution"]
    danger_keywords = ["dangerous", "venom", "poisonous", "attack", "threat", "aggressive"]
    negation_keywords = ["not", "no ", "isn't", "aren't", "non-venomous", "non-aggressive", "harmless", "rarely attack"]
    first_aid_keywords = ["first aid", "bite treatment", "if bitten", "antivenom", "envenomation"]

    facts = {}

    for s in sentences:
        s_lower = s.lower()
        
        # Find the first CONFIRMED danger fact
        if 'danger' not in facts and any(keyword in s_lower for keyword in danger_keywords):
            # Important: Check that the sentence does NOT contain a negation
            if not any(negation in s_lower for negation in negation_keywords):
                facts['danger'] = f" Danger: {s.strip()}."

        # Find the first habitat fact
        if 'habitat' not in facts and any(keyword in s_lower for keyword in habitat_keywords):
            facts['habitat'] = f"🌳 Habitat: {s.strip()}."

        # Find the first first-aid fact (only for snakes)
        if "snake" in animal_name.lower() and 'first_aid' not in facts and any(keyword in s_lower for keyword in first_aid_keywords):
            facts['first_aid'] = f"🚑 First Aid: {s.strip()}."

    # Build the list of facts in a specific order of importance
    ordered_facts = []
    if 'danger' in facts:
        ordered_facts.append(facts['danger'])
    if 'first_aid' in facts:
        ordered_facts.append(facts['first_aid'])
    if 'habitat' in facts:
        ordered_facts.append(facts['habitat'])

    if ordered_facts:
        return ordered_facts

    # Fallback if no specific facts are found
    return [s.strip() for s in sentences if len(s.strip()) > 40][:2]


# --- Wikipedia Facts Function (Updated) ---
def get_wikipedia_facts(keyword, num_facts=5):
    url = "https://en.wikipedia.org/w/api.php"
    search_keyword = keyword.replace('_', ' ')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    search_params = {
        "action": "query", "format": "json", "list": "search", "srsearch": search_keyword
    }

    try:
        search_response = requests.get(url, params=search_params, headers=headers)
        search_response.raise_for_status()
        search_data = search_response.json()

        if search_data.get('query', {}).get('search'):
            page_title = search_data['query']['search'][0]['title']
            page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
            
            extract_params = {
                "action": "query", "format": "json", "prop": "extracts", "explaintext": True, "titles": page_title
            }

            extract_response = requests.get(url, params=extract_params, headers=headers)
            extract_response.raise_for_status()
            extract_data = extract_response.json()
            
            page_id = list(extract_data['query']['pages'].keys())[0]
            extract = extract_data['query']['pages'][page_id].get('extract', '')
            
            if extract:
                facts = extract_relevant_facts(extract, keyword)
                return facts, page_url

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikipedia data: {e}")
        return ["Could not fetch facts from Wikipedia."], None

    return ["No facts found for this topic."], None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        try:
            img_bytes = file.read()
            image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            
            img_array = np.array(image)
            img_array = cv2.resize(img_array, (224, 224))
            img_array = preprocess_input(img_array)
            img_array = np.expand_dims(img_array, axis=0)

            prediction = model.predict(img_array)
            top_pred = decode_predictions(prediction, top=1)[0][0]
            predicted_class = top_pred[1].replace("_", " ")
            confidence = float(top_pred[2] * 100)

            facts, wiki_link = get_wikipedia_facts(predicted_class)

            return jsonify({
                'prediction': predicted_class.title(),
                'confidence': confidence,
                'facts': facts,
                'wiki_link': wiki_link
            })
        except Exception as e:
            print(f"An error occurred during prediction: {e}")
            return jsonify({'error': 'Failed to process the image.'}), 500

    return jsonify({'error': 'An unknown error occurred.'}), 500


if __name__ == '__main__':
    app.run(debug=True)


###3333333333333333333333333##################################################################################################33
# from flask import Flask, request, jsonify, render_template
# import numpy as np
# import cv2
# import requests
# from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
# from PIL import Image
# import io

# app = Flask(__name__)

# # --- Load Model ---
# # Note: In a production environment, you might want to handle model loading more robustly.
# def load_model():
#     return VGG16(weights="imagenet")

# model = load_model()

# # --- Wikipedia Facts Function ---
# def get_wikipedia_facts(keyword, num_facts=5):
#     url = "https://en.wikipedia.org/w/api.php"
#     search_keyword = keyword.replace('_', ' ')

#     search_params = {
#         "action": "query",
#         "format": "json",
#         "list": "search",
#         "srsearch": search_keyword
#     }

#     try:
#         search_response = requests.get(url, params=search_params)
#         search_response.raise_for_status()  # Raise an exception for bad status codes
#         search_data = search_response.json()

#         if 'query' in search_data and 'search' in search_data['query']:
#             search_results = search_data['query']['search']
#             if search_results:
#                 page_title = search_results[0]['title']
#                 page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
#                 extract_params = {
#                     "action": "query",
#                     "format": "json",
#                     "prop": "extracts",
#                     "exintro": True,
#                     "explaintext": True,
#                     "titles": page_title
#                 }

#                 extract_response = requests.get(url, params=extract_params)
#                 extract_response.raise_for_status()
#                 extract_data = extract_response.json()
#                 pages = extract_data.get("query", {}).get("pages", {})
#                 for page_id, page in pages.items():
#                     if "extract" in page:
#                         extract = page["extract"]
#                         facts = [s.strip() for s in extract.split('. ') if len(s.strip()) > 40 and 'may refer to' not in s]
#                         return facts[:num_facts], page_url
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching Wikipedia data: {e}")
#         return ["Could not fetch facts from Wikipedia."], None


#     return ["No facts found."], None

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#     if file:
#         try:
#             img_bytes = file.read()
#             image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            
#             # Preprocess the image
#             img_array = np.array(image)
#             img_array = cv2.resize(img_array, (224, 224))
#             img_array = preprocess_input(img_array)
#             img_array = np.expand_dims(img_array, axis=0)

#             # Make prediction
#             prediction = model.predict(img_array)
#             top_pred = decode_predictions(prediction, top=1)[0][0]
#             predicted_class = top_pred[1].replace("_", " ")
#             confidence = float(top_pred[2] * 100) # Ensure confidence is a standard float

#             # Get Wikipedia facts
#             facts, wiki_link = get_wikipedia_facts(predicted_class)

#             # Return JSON response
#             return jsonify({
#                 'prediction': predicted_class.title(),
#                 'confidence': confidence,
#                 'facts': facts,
#                 'wiki_link': wiki_link
#             })
#         except Exception as e:
#             # If any error occurs during prediction, return a server error.
#             print(f"An error occurred during prediction: {e}")
#             return jsonify({'error': 'Failed to process the image.'}), 500

#     return jsonify({'error': 'An unknown error occurred.'}), 500


# if __name__ == '__main__':
#     app.run(debug=True)
######################################################################3
# from flask import Flask, request, jsonify, render_template
# import numpy as np
# import cv2
# import requests
# from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
# from PIL import Image
# import io

# app = Flask(__name__)

# # --- Load Model ---
# def load_model():
#     return VGG16(weights="imagenet")

# model = load_model()

# # --- Wikipedia Facts Function ---
# def get_wikipedia_facts(keyword, num_facts=5):
#     url = "https://en.wikipedia.org/w/api.php"
#     search_keyword = keyword.replace('_', ' ')

#     # Set a User-Agent header to mimic a web browser
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
#     }

#     search_params = {
#         "action": "query",
#         "format": "json",
#         "list": "search",
#         "srsearch": search_keyword
#     }

#     try:
#         # Make the request with the headers
#         search_response = requests.get(url, params=search_params, headers=headers)
#         search_response.raise_for_status()
#         search_data = search_response.json()

#         if 'query' in search_data and 'search' in search_data['query']:
#             search_results = search_data['query']['search']
#             if search_results:
#                 page_title = search_results[0]['title']
#                 page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
#                 extract_params = {
#                     "action": "query",
#                     "format": "json",
#                     "prop": "extracts",
#                     "exintro": True,
#                     "explaintext": True,
#                     "titles": page_title
#                 }

#                 # Make the second request with the same headers
#                 extract_response = requests.get(url, params=extract_params, headers=headers)
#                 extract_response.raise_for_status()
#                 extract_data = extract_response.json()
#                 pages = extract_data.get("query", {}).get("pages", {})
#                 for page_id, page in pages.items():
#                     if "extract" in page:
#                         extract = page["extract"]
#                         facts = [s.strip() for s in extract.split('. ') if len(s.strip()) > 40 and 'may refer to' not in s]
#                         return facts[:num_facts], page_url
    
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching Wikipedia data: {e}")
#         return ["Could not fetch facts from Wikipedia."], None

#     return ["No facts found for this topic."], None


# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#     if file:
#         try:
#             img_bytes = file.read()
#             image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            
#             img_array = np.array(image)
#             img_array = cv2.resize(img_array, (224, 224))
#             img_array = preprocess_input(img_array)
#             img_array = np.expand_dims(img_array, axis=0)

#             prediction = model.predict(img_array)
#             top_pred = decode_predictions(prediction, top=1)[0][0]
#             predicted_class = top_pred[1].replace("_", " ")
#             confidence = float(top_pred[2] * 100)

#             facts, wiki_link = get_wikipedia_facts(predicted_class)

#             return jsonify({
#                 'prediction': predicted_class.title(),
#                 'confidence': confidence,
#                 'facts': facts,
#                 'wiki_link': wiki_link
#             })
#         except Exception as e:
#             print(f"An error occurred during prediction: {e}")
#             return jsonify({'error': 'Failed to process the image.'}), 500

#     return jsonify({'error': 'An unknown error occurred.'}), 500


# if __name__ == '__main__':
#     app.run(debug=True)