import streamlit as st # type: ignore
import numpy as np
import cv2
import requests # type: ignore
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions # type: ignore
from PIL import Image # type: ignore

# --- PAGE CONFIG ---
st.set_page_config(page_title="WildLens AI", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/616/616408.png", width=100)
    st.title("WildLens AI 🧠")
    st.markdown("""
    Upload an image of any animal to:
    - 🧠 Identify the animal  
    - 📚 Learn fun facts from Wikipedia  
    """)
    st.markdown("---")
    st.markdown("📍 *Powered by VGG16 + Streamlit*")
    st.markdown("👨‍💻 Developed by **Vinodh**")

# --- Load Model ---
@st.cache_resource
def load_model():
    return VGG16(weights="imagenet")

model = load_model()

# --- Wikipedia Facts Function ---
def get_wikipedia_facts(keyword, num_facts=5):
    url = "https://en.wikipedia.org/w/api.php"
    search_keyword = keyword.replace('_', ' ')

    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search_keyword
    }

    search_response = requests.get(url, params=search_params)
    search_data = search_response.json()

    if 'query' in search_data and 'search' in search_data['query']:
        search_results = search_data['query']['search']
        if search_results:
            page_title = search_results[0]['title']
            page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
            extract_params = {
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "titles": page_title
            }

            extract_response = requests.get(url, params=extract_params)
            extract_data = extract_response.json()
            pages = extract_data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                if "extract" in page:
                    extract = page["extract"]
                    facts = [s.strip() for s in extract.split('. ') if len(s.strip()) > 40 and 'may refer to' not in s]
                    return facts[:num_facts], page_url

    return ["No facts found."], None

# --- MAIN UI ---
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>WildLens AI - Animal Identifier 🦁</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Upload an animal image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Identify Animal", use_container_width=True):
        with st.spinner("Analyzing the image and predicting..."):
            img_array = np.array(image)
            if img_array.shape[-1] == 4:
                img_array = img_array[:, :, :3]
            img_array = cv2.resize(img_array, (224, 224))
            img_array = preprocess_input(img_array)
            img_array = np.expand_dims(img_array, axis=0)

            prediction = model.predict(img_array)
            top_pred = decode_predictions(prediction, top=1)[0][0]
            predicted_class = top_pred[1].replace("_", " ")
            confidence = top_pred[2] * 100

        st.success(f"🎯 Predicted Animal: **{predicted_class.title()}** ({confidence:.2f}% confidence)")

        # Wikipedia Facts
        with st.spinner("Fetching facts from Wikipedia..."):
            facts, wiki_link = get_wikipedia_facts(predicted_class)

        st.subheader("📚 Did You Know?")
        for fact in facts:
            st.markdown(f"✅ {fact}.")

        if wiki_link:
            st.markdown(f"[🌐 Read more on Wikipedia]({wiki_link})")

else:
    st.info("👈 Please upload an animal image to get started.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align:center;color:gray;'>Made with ❤️ by Vinodh • Powered by Streamlit & TensorFlow</p>", unsafe_allow_html=True)
