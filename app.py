import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import time
import requests
import base64
from io import BytesIO

# Configure the app
st.set_page_config(
    page_title="Multi-Platform Horror Shorts Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stApp {
        background: linear-gradient(135deg, #0a0a0a, #1a1a1a);
    }
    .stButton > button {
        background: linear-gradient(135deg, #ff4444, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 68, 68, 0.4);
    }
    .platform-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }
    .character-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }
    .scene-card {
        background: rgba(139, 92, 246, 0.1);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #8b5cf6;
        margin-bottom: 1rem;
    }
    .header-title {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #ff4444, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .platform-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    .status-connected {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }
    .status-disconnected {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'characters' not in st.session_state:
    st.session_state.characters = {}
if 'scripts' not in st.session_state:
    st.session_state.scripts = {}
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {
        'runwayml': '',
        'kling': '',
        'pika': '',
        'stable_video': '',
        'luma': ''
    }
if 'activity' not in st.session_state:
    st.session_state.activity = []
if 'video_tasks' not in st.session_state:
    st.session_state.video_tasks = {}

def add_activity(message):
    """Add activity to the activity log"""
    st.session_state.activity.insert(0, {
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message
    })
    st.session_state.activity = st.session_state.activity[:10]

def image_to_base64(image_path):
    """Convert image to base64 string for API"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        st.error(f"Error converting image: {e}")
        return None

# Video Generation API Functions
def generate_video_runwayml(api_key, character_image_path, prompt, narration):
    """Generate video using RunwayML API"""
    try:
        character_base64 = image_to_base64(character_image_path)
        if not character_base64:
            return None, "Failed to process character image"
        
        url = "https://api.runwayml.com/v1/image_to_video"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        full_prompt = f"{prompt}. {narration}. Horror aesthetic, cinematic lighting, electronic dance music video style."
        
        payload = {
            "model": "gen3a_turbo",
            "prompt_image": f"data:image/png;base64,{character_base64}",
            "prompt_text": full_prompt,
            "duration": 5,
            "ratio": "9:16",
            "watermark": False
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('id'), "Success"
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_video_kling(api_key, character_image_path, prompt, narration):
    """Generate video using Kling AI API"""
    try:
        character_base64 = image_to_base64(character_image_path)
        if not character_base64:
            return None, "Failed to process character image"
        
        url = "https://api.klingai.com/v1/videos/image2video"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        full_prompt = f"{prompt}. {narration}. Dark horror atmosphere, cinematic quality, high detail."
        
        payload = {
            "model": "kling-v1",
            "image": f"data:image/png;base64,{character_base64}",
            "prompt": full_prompt,
            "duration": 5,
            "aspect_ratio": "9:16",
            "cfg_scale": 0.5,
            "camera_control": {
                "type": "none"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('id'), "Success"
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_video_pika(api_key, character_image_path, prompt, narration):
    """Generate video using Pika Labs API"""
    try:
        character_base64 = image_to_base64(character_image_path)
        if not character_base64:
            return None, "Failed to process character image"
        
        url = "https://api.pika.art/generate/video"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        full_prompt = f"{prompt}. {narration}. Horror movie style, dramatic lighting."
        
        payload = {
            "prompt": full_prompt,
            "image": f"data:image/png;base64,{character_base64}",
            "aspectRatio": "9:16",
            "duration": 3,
            "fps": 24
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('id'), "Success"
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_video_luma(api_key, character_image_path, prompt, narration):
    """Generate video using Luma Dream Machine API"""
    try:
        character_base64 = image_to_base64(character_image_path)
        if not character_base64:
            return None, "Failed to process character image"
        
        url = "https://api.lumalabs.ai/dream-machine/v1/generations"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        full_prompt = f"{prompt}. {narration}. Cinematic horror aesthetic, high quality."
        
        payload = {
            "prompt": full_prompt,
            "keyframes": {
                "frame0": {
                    "type": "image",
                    "url": f"data:image/png;base64,{character_base64}"
                }
            },
            "aspect_ratio": "9:16",
            "loop": False
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            result = response.json()
            return result.get('id'), "Success"
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def check_video_status(platform, api_key, task_id):
    """Check video generation status across platforms"""
    try:
        if platform == "runwayml":
            url = f"https://api.runwayml.com/v1/tasks/{task_id}"
        elif platform == "kling":
            url = f"https://api.klingai.com/v1/videos/{task_id}"
        elif platform == "pika":
            url = f"https://api.pika.art/jobs/{task_id}"
        elif platform == "luma":
            url = f"https://api.lumalabs.ai/dream-machine/v1/generations/{task_id}"
        else:
            return 'error', None
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Normalize status across platforms
            if platform == "runwayml":
                status = result.get('status', 'unknown')
                output = result.get('output')
            elif platform == "kling":
                status = result.get('status', 'unknown')
                output = result.get('works', [{}])[0].get('resource')
            elif platform == "pika":
                status = result.get('status', 'unknown')
                output = result.get('result', {}).get('videos', [])
            elif platform == "luma":
                status = result.get('state', 'unknown')
                output = result.get('assets', {}).get('video')
            
            return status, output
        else:
            return 'error', None
            
    except Exception as e:
        return 'error', str(e)

def save_data():
    """Save data to local JSON files"""
    try:
        os.makedirs('horror_shorts_data', exist_ok=True)
        
        with open('horror_shorts_data/characters.json', 'w') as f:
            json.dump(st.session_state.characters, f)
        
        with open('horror_shorts_data/scripts.json', 'w') as f:
            json.dump(st.session_state.scripts, f)
        
        with open('horror_shorts_data/api_keys.json', 'w') as f:
            json.dump(st.session_state.api_keys, f)
        
        with open('horror_shorts_data/video_tasks.json', 'w') as f:
            json.dump(st.session_state.video_tasks, f)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def load_data():
    """Load data from local JSON files"""
    try:
        if os.path.exists('horror_shorts_data/characters.json'):
            with open('horror_shorts_data/characters.json', 'r') as f:
                st.session_state.characters = json.load(f)
        
        if os.path.exists('horror_shorts_data/scripts.json'):
            with open('horror_shorts_data/scripts.json', 'r') as f:
                st.session_state.scripts = json.load(f)
        
        if os.path.exists('horror_shorts_data/api_keys.json'):
            with open('horror_shorts_data/api_keys.json', 'r') as f:
                st.session_state.api_keys = json.load(f)
        
        if os.path.exists('horror_shorts_data/video_tasks.json'):
            with open('horror_shorts_data/video_tasks.json', 'r') as f:
                st.session_state.video_tasks = json.load(f)
    except Exception as e:
        st.write(f"Note: Loading fresh data (no previous save found)")

# Load data on startup
load_data()

# Sidebar Navigation
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem;">
    <h1 style="color: #ff4444;">🎬 Multi-Platform Studio</h1>
    <p style="color: #8b5cf6;">Horror Shorts Generator</p>
</div>
""", unsafe_allow_html=True)

# Platform status in sidebar
st.sidebar.markdown("### 🔗 Platform Status")
platforms = {
    "RunwayML": st.session_state.api_keys.get('runwayml', ''),
    "Kling AI": st.session_state.api_keys.get('kling', ''),
    "Pika Labs": st.session_state.api_keys.get('pika', ''),
    "Luma AI": st.session_state.api_keys.get('luma', '')
}

for platform, api_key in platforms.items():
    status = "🟢 Connected" if api_key else "🔴 Not Connected"
    st.sidebar.write(f"**{platform}**: {status}")

page = st.sidebar.selectbox(
    "Navigate",
    ["🏠 Dashboard", "👥 Characters", "📝 Scripts", "🎬 Scene Builder", "🎥 Video Generation", "🔗 API Settings", "⚙️ Settings"]
)

# Dashboard Page
if page == "🏠 Dashboard":
    st.markdown('<h1 class="header-title">🎬 Multi-Platform Horror Shorts Studio</h1>', unsafe_allow_html=True)
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Characters", len(st.session_state.characters))
    
    with col2:
        st.metric("Scripts", len(st.session_state.scripts))
    
    with col3:
        total_scenes = sum(len(script.get('scenes', [])) for script in st.session_state.scripts.values())
        st.metric("Scenes", total_scenes)
    
    with col4:
        connected_platforms = sum(1 for key in st.session_state.api_keys.values() if key)
        st.metric("Connected Platforms", connected_platforms)
    
    # Platform Overview
    st.subheader("🚀 Supported Platforms")
    
    platform_info = {
        "RunwayML": {
            "description": "High-quality realistic videos, excellent character consistency",
            "best_for": "Professional-grade horror shorts",
            "speed": "Medium",
            "quality": "⭐⭐⭐⭐⭐"
        },
        "Kling AI": {
            "description": "Great motion and character fidelity, good for action scenes",
            "best_for": "Dynamic horror sequences",
            "speed": "Fast",
            "quality": "⭐⭐⭐⭐"
        },
        "Pika Labs": {
            "description": "Creative effects and transitions, good for atmospheric scenes",
            "best_for": "Cinematic horror effects",
            "speed": "Fast",
            "quality": "⭐⭐⭐"
        },
        "Luma AI": {
            "description": "Smooth motion and natural movements",
            "best_for": "Character-focused scenes",
            "speed": "Medium",
            "quality": "⭐⭐⭐⭐"
        }
    }
    
    cols = st.columns(2)
    for i, (platform, info) in enumerate(platform_info.items()):
        with cols[i % 2]:
            with st.container():
                st.markdown('<div class="platform-card">', unsafe_allow_html=True)
                is_connected = st.session_state.api_keys.get(platform.lower().replace(' ', '_'), '')
                status_class = "status-connected" if is_connected else "status-disconnected"
                status_text = "🟢 Connected" if is_connected else "🔴 Setup Required"
                
                st.markdown(f'<div class="platform-status {status_class}">{status_text}</div>', unsafe_allow_html=True)
                st.subheader(platform)
                st.write(info['description'])
                st.write(f"**Best for:** {info['best_for']}")
                st.write(f"**Speed:** {info['speed']} | **Quality:** {info['quality']}")
                st.markdown('</div>', unsafe_allow_html=True)

# Characters Page (same as before)
elif page == "👥 Characters":
    st.title("Character Database")
    
    char_count = len(st.session_state.characters)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Your Characters ({char_count}/6)")
    with col2:
        if char_count < 6:
            st.success("✅ Can add more")
        else:
            st.warning("⚠️ Limit reached")
    
    if char_count < 6:
        with st.expander("➕ Add New Character", expanded=(char_count == 0)):
            with st.form("add_character_form"):
                char_name = st.text_input("Character Name", placeholder="Enter character name")
                char_description = st.text_area("Description", placeholder="Describe your character's appearance, personality, etc.", height=100)
                char_image = st.file_uploader("Reference Image", type=['png', 'jpg', 'jpeg'])
                
                submitted = st.form_submit_button("Save Character", use_container_width=True)
                
                if submitted:
                    if not char_name or not char_description:
                        st.error("Please fill in character name and description")
                    elif char_name in st.session_state.characters:
                        st.error("Character name already exists")
                    else:
                        character_data = {
                            'name': char_name,
                            'description': char_description,
                            'created': datetime.now().isoformat()
                        }
                        
                        if char_image:
                            os.makedirs('horror_shorts_data/images', exist_ok=True)
                            image_path = f"horror_shorts_data/images/{char_name.replace(' ', '_')}.png"
                            image = Image.open(char_image)
                            image.save(image_path)
                            character_data['image_path'] = image_path
                        
                        st.session_state.characters[char_name] = character_data
                        save_data()
                        add_activity(f"Added character: {char_name}")
                        st.success(f"Character '{char_name}' saved successfully!")
                        st.rerun()
    
    if st.session_state.characters:
        characters = list(st.session_state.characters.items())
        for i in range(0, len(characters), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(characters):
                    char_name, char_data = characters[i + j]
                    with col:
                        with st.container():
                            st.markdown('<div class="character-card">', unsafe_allow_html=True)
                            
                            if 'image_path' in char_data and os.path.exists(char_data['image_path']):
                                image = Image.open(char_data['image_path'])
                                st.image(image, width=200)
                            else:
                                st.write("📷 No image uploaded")
                            
                            st.subheader(char_name)
                            st.write(char_data['description'])
                            
                            if st.button(f"🗑️ Delete {char_name}", key=f"del_{char_name}"):
                                del st.session_state.characters[char_name]
                                save_data()
                                add_activity(f"Deleted character: {char_name}")
                                st.rerun()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No characters added yet. Add your first character above!")

# Scripts Page (same as before with minor updates)
elif page == "📝 Scripts":
    st.title("Script Manager")
    
    with st.expander("➕ Add New Script", expanded=(len(st.session_state.scripts) == 0)):
        with st.form("add_script_form"):
            script_title = st.text_input("Script Title", placeholder="Enter script title")
            script_content = st.text_area("Script Content", placeholder="Enter your YouTube Short script here...", height=200)
            
            submitted = st.form_submit_button("Save Script", use_container_width=True)
            
            if submitted:
                if not script_title or not script_content:
                    st.error("Please fill in script title and content")
                elif script_title in st.session_state.scripts:
                    st.error("Script title already exists")
                else:
                    st.session_state.scripts[script_title] = {
                        'content': script_content,
                        'created': datetime.now().isoformat(),
                        'scenes': []
                    }
                    save_data()
                    add_activity(f"Added script: {script_title}")
                    st.success(f"Script '{script_title}' saved successfully!")
                    st.rerun()
    
    if st.session_state.scripts:
        st.subheader(f"Your Scripts ({len(st.session_state.scripts)})")
        
        for script_title, script_data in st.session_state.scripts.items():
            with st.expander(f"📜 {script_title}"):
                st.text_area("Content", script_data['content'], height=150, disabled=True, key=f"view_{script_title}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🎬 Generate Scenes", key=f"gen_{script_title}"):
                        sentences = [s.strip() + '.' for s in script_data['content'].split('.') if s.strip()]
                        scenes = []
                        for i, sentence in enumerate(sentences):
                            scenes.append({
                                'scene_number': i + 1,
                                'narration': sentence,
                                'assigned_character': None,
                                'visual_description': '',
                                'status': 'pending'
                            })
                        
                        st.session_state.scripts[script_title]['scenes'] = scenes
                        save_data()
                        add_activity(f"Generated {len(scenes)} scenes for: {script_title}")
                        st.success(f"Generated {len(scenes)} scenes!")
                        st.rerun()
                
                with col2:
                    scene_count = len(script_data.get('scenes', []))
                    if scene_count > 0:
                        st.info(f"📊 {scene_count} scenes")
                    else:
                        st.warning("No scenes generated")
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"del_script_{script_title}"):
                        del st.session_state.scripts[script_title]
                        save_data()
                        add_activity(f"Deleted script: {script_title}")
                        st.rerun()
    else:
        st.info("No scripts added yet. Add your first script above!")

# Scene Builder Page (same as before)
elif page == "🎬 Scene Builder":
    st.title("Scene Builder")
    
    if not st.session_state.scripts:
        st.warning("Please add some scripts first in the Script Manager!")
    elif not st.session_state.characters:
        st.warning("Please add some characters first in the Character Database!")
    else:
        script_options = list(st.session_state.scripts.keys())
        selected_script = st.selectbox("Select Script", script_options)
        
        if selected_script:
            script_data = st.session_state.scripts[selected_script]
            
            if not script_data.get('scenes'):
                st.info("No scenes generated yet. Go to Script Manager and click 'Generate Scenes'.")
            else:
                st.subheader(f"Scenes for '{selected_script}'")
                
                total_scenes = len(script_data['scenes'])
                ready_scenes = len([s for s in script_data['scenes'] if s.get('assigned_character') and s.get('visual_description')])
                progress = ready_scenes / total_scenes if total_scenes > 0 else 0
                
                st.progress(progress, text=f"Scene Progress: {ready_scenes}/{total_scenes} scenes ready")
                
                for i, scene in enumerate(script_data['scenes']):
                    with st.expander(f"Scene {scene['scene_number']}", expanded=(not scene.get('assigned_character'))):
                        st.markdown('<div class="scene-card">', unsafe_allow_html=True)
                        
                        st.write(f"**Narration:** {scene['narration']}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            char_options = [""] + list(st.session_state.characters.keys())
                            current_char = scene.get('assigned_character', '')
                            selected_char = st.selectbox(
                                "Assign Character",
                                char_options,
                                index=char_options.index(current_char) if current_char in char_options else 0,
                                key=f"char_{selected_script}_{i}"
                            )
                            
                            if selected_char != scene.get('assigned_character'):
                                st.session_state.scripts[selected_script]['scenes'][i]['assigned_character'] = selected_char
                                save_data()
                        
                        with col2:
                            visual_desc = st.text_area(
                                "Visual Description",
                                scene.get('visual_description', ''),
                                height=100,
                                key=f"visual_{selected_script}_{i}",
                                placeholder="Describe what should be shown in this scene..."
                            )
                            
                            if visual_desc != scene.get('visual_description'):
                                st.session_state.scripts[selected_script]['scenes'][i]['visual_description'] = visual_desc
                                save_data()
                        
                        if scene.get('assigned_character') and scene.get('visual_description'):
                            st.success("✅ Ready for video generation")
                        elif scene.get('assigned_character'):
                            st.warning("⚠️ Missing visual description")
                        elif scene.get('visual_description'):
                            st.warning("⚠️ No character assigned")
                        else:
                            st.error("❌ Incomplete - needs character and visual description")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

# Video Generation Page
elif page == "🎥 Video Generation":
    st.title("Multi-Platform Video Generation")
    
    # Check if any API keys are configured
    connected_platforms = [k for k, v in st.session_state.api_keys.items() if v]
    
    if not connected_platforms:
        st.warning("Please configure at least one API key in API Settings first!")
        st.stop()
    
    # Find ready projects
    ready_projects = []
    for script_title, script_data in st.session_state.scripts.items():
        if script_data.get('scenes'):
            ready_scenes = [s for s in script_data['scenes'] if s.get('assigned_character') and s.get('visual_description')]
            if ready_scenes:
                ready_projects.append({
                    'title': script_title,
                    'total_scenes': len(script_data['scenes']),
                    'ready_scenes': len(ready_scenes),
                    'scenes': ready_scenes
                })
    
    if ready_projects:
        st.subheader("🎬 Ready for Video Generation")
        
        for project in ready_projects:
            with st.expander(f"📝 {project['title']} ({project['ready_scenes']} scenes ready)"):
                
                # Platform selection
                available_platforms = []
                if st.session_state.api_keys.get('runwayml'):
                    available_platforms.append("RunwayML")
                if st.session_state.api_keys.get('kling'):
                    available_platforms.append("Kling AI")
                if st.session_state.api_keys.get('pika'):
                    available_platforms.append("Pika Labs")
                if st.session_state.api_keys.get('luma'):
                    available_platforms.append("Luma AI")
                
                selected_platform = st.selectbox(
                    "Choose Video Generation Platform",
                    available_platforms,
                    key=f"platform_{project['title']}"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"👀 Preview Project", key=f"preview_{project['title']}"):
                        st.subheader("Project Preview")
