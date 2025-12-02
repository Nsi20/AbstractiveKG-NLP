import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from src.pipeline import AbstractiveKGPipeline
from src.graph_rag import GraphRAG
import PyPDF2
import requests
from bs4 import BeautifulSoup
import io

# Page Config
st.set_page_config(layout="wide", page_title="AbstractiveKG-NLP Explorer", page_icon="🕸️")

# Initialize Session State
if 'nodes' not in st.session_state:
    st.session_state['nodes'] = []
if 'edges' not in st.session_state:
    st.session_state['edges'] = []
if 'kg_data' not in st.session_state:
    st.session_state['kg_data'] = {'entities': [], 'relations': []}
if 'summary' not in st.session_state:
    st.session_state['summary'] = ""
if 'input_text' not in st.session_state:
    st.session_state['input_text'] = """Elon Musk, the CEO of Tesla and SpaceX, announced a new mission to Mars. 
The mission aims to establish a permanent human settlement on the Red Planet. 
SpaceX has been developing the Starship rocket for this purpose. 
NASA is also collaborating with SpaceX on various lunar missions."""

# Initialize Resources
@st.cache_resource
def get_pipeline():
    return AbstractiveKGPipeline()

@st.cache_resource
def get_rag():
    return GraphRAG()

pipeline = get_pipeline()
rag = get_rag()

# Helper Functions
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract paragraphs
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])
        return text
    except Exception as e:
        return f"Error fetching URL: {e}"

def process_text(text):
    with st.spinner("Processing... (Summarizing & Extracting Entities)"):
        summary, kg_data = pipeline.process(text)
        
        # Update Session State
        st.session_state['summary'] = summary
        st.session_state['kg_data'] = kg_data
        
        # Prepare Graph
        nodes = []
        edges = []
        node_ids = set()
        
        for ent in kg_data['entities']:
            if ent['text'] not in node_ids:
                nodes.append(Node(id=ent['text'], 
                                  label=ent['text'], 
                                  size=25, 
                                  shape="dot",
                                  color="#4E88E5" if ent['label'] == "ORG" else "#E54E4E" if ent['label'] == "PERSON" else "#4EE588"))
                node_ids.add(ent['text'])
        
        for rel in kg_data['relations']:
            if rel['head'] not in node_ids:
                nodes.append(Node(id=rel['head'], label=rel['head'], size=15, color="#999"))
                node_ids.add(rel['head'])
            if rel['tail'] not in node_ids:
                nodes.append(Node(id=rel['tail'], label=rel['tail'], size=15, color="#999"))
                node_ids.add(rel['tail'])
                
            edges.append(Edge(source=rel['head'], 
                              target=rel['tail'], 
                              label=rel['type'],
                              type="CURVE_SMOOTH"))

        st.session_state['nodes'] = nodes
        st.session_state['edges'] = edges

# UI Layout
st.title("🕸️ AbstractiveKG-NLP Explorer")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Explorer", "💬 Chat (GraphRAG)", "📂 Upload Data"])

# --- TAB 1: EXPLORER ---
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input Text")
        text_input = st.text_area("Content to Analyze:", height=300, key="main_input", value=st.session_state['input_text'])
        if st.button("🚀 Process Text", type="primary"):
            st.session_state['input_text'] = text_input
            process_text(text_input)
            
        if st.session_state['summary']:
            st.subheader("📄 Abstractive Summary")
            st.info(st.session_state['summary'])

    with col2:
        st.subheader("🕸️ Knowledge Graph")
        if st.session_state['nodes']:
            config = Config(width="100%", height=500, directed=True, physics=True, hierarchical=False)
            agraph(nodes=st.session_state['nodes'], edges=st.session_state['edges'], config=config)
            
            with st.expander("📊 View Data Tables"):
                st.dataframe(st.session_state['kg_data']['relations'])
        else:
            st.info("Run processing to visualize the graph.")

# --- TAB 2: CHAT (GraphRAG) ---
with tab2:
    st.header("💬 Chat with your Knowledge Graph")
    st.markdown("Ask questions about the entities stored in the graph (e.g., *'What is Elon Musk connected to?'*).")
    
    user_question = st.text_input("Ask a question:")
    if user_question:
        with st.spinner("Querying Knowledge Graph..."):
            answer = rag.query(user_question)
            st.markdown(answer)

# --- TAB 3: UPLOAD ---
with tab3:
    st.header("📂 Import Data")
    
    upload_option = st.radio("Source Type", ["PDF Document", "Web URL"])
    
    if upload_option == "PDF Document":
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        if uploaded_file:
            if st.button("Load PDF"):
                text = extract_text_from_pdf(uploaded_file)
                st.session_state['input_text'] = text
                st.success("PDF Loaded! Go to 'Explorer' tab to process it.")
                
    elif upload_option == "Web URL":
        url = st.text_input("Enter URL")
        if url:
            if st.button("Scrape URL"):
                text = extract_text_from_url(url)
                st.session_state['input_text'] = text
                st.success("URL Scraped! Go to 'Explorer' tab to process it.")

# Footer
st.divider()
st.caption("AbstractiveKG-NLP | Built with Streamlit & spaCy")
