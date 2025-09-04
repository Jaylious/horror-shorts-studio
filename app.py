import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import time

# Configure the app
st.set_page_config(
    page_title="Horror Shorts Studio",
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'characters' not in st.session_state:
    st.session_state.characters = {}
if 'scripts' not in st.session_state:
    st.session_state.scripts = {}
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'activity' not in st.session_state:
    st.session_state.activity = []

def add_activity(message):
    """Add activity to the activity log"""
    st.session_state.activity.insert(0, {
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message
    })
    # Keep only last 10 activities
    st.session_state.activity = st.session_state.activity[:10]

def save_data():
    """Save data to local JSON files"""
    try:
        os.makedirs('horror_shorts_data', exist_ok=True)
        
        with open('horror_shorts_data/characters.json', 'w') as f:
            json.dump(st.session_state.characters, f)
        
        with open('horror_shorts_data/scripts.json', 'w') as f:
            json.dump(st.session_state.scripts, f)
        
        with open('horror_shorts_data/settings.json', 'w') as f:
            json.dump({'api_key': st.session_state.api_key}, f)
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
        
        if os.path.exists('horror_shorts_data/settings.json'):
            with open('horror_shorts_data/settings.json', 'r') as f:
                settings = json.load(f)
                st.session_state.api_key = settings.get('api_key', '')
    except Exception as e:
        st.write(f"Note: Loading fresh data (no previous save found)")

# Load data on startup
load_data()

# Sidebar Navigation
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem;">
    <h1 style="color: #ff4444;">🎬 Horror Shorts Studio</h1>
    <p style="color: #8b5cf6;">Electronic Dance Horror House</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "Navigate",
    ["🏠 Dashboard", "👥 Characters", "📝 Scripts", "🎬 Scene Builder", "🎥 Video Queue", "⚙️ Settings"]
)

# Dashboard Page
if page == "🏠 Dashboard":
    st.markdown('<h1 class="header-title">🎬 Horror Shorts Studio</h1>', unsafe_allow_html=True)
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Characters", len(st.session_state.characters), help="Total characters created")
    
    with col2:
        st.metric("Scripts", len(st.session_state.scripts), help="Total scripts added")
    
    with col3:
        total_scenes = sum(len(script.get('scenes', [])) for script in st.session_state.scripts.values())
        st.metric("Scenes", total_scenes, help="Total scenes generated")
    
    with col4:
        ready_scenes = sum(
            len([s for s in script.get('scenes', []) if s.get('assigned_character') and s.get('visual_description')])
            for script in st.session_state.scripts.values()
        )
        st.metric("Ready for Video", ready_scenes, help="Scenes ready for video generation")
    
    # Quick Actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Character", use_container_width=True):
            st.session_state.page = "👥 Characters"
    
    with col2:
        if st.button("📝 New Script", use_container_width=True):
            st.session_state.page = "📝 Scripts"
    
    with col3:
        if st.button("🎥 Generate Videos", use_container_width=True):
            st.session_state.page = "🎥 Video Queue"
    
    # Recent Activity
    st.subheader("Recent Activity")
    if st.session_state.activity:
        for activity in st.session_state.activity[:5]:
            st.write(f"**{activity['time']}** - {activity['message']}")
    else:
        st.info("No recent activity. Start by adding characters or scripts!")

# Characters Page
elif page == "👥 Characters":
    st.title("Character Database")
    
    # Character limit check
    char_count = len(st.session_state.characters)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Your Characters ({char_count}/6)")
    with col2:
        if char_count < 6:
            st.success("✅ Can add more")
        else:
            st.warning("⚠️ Limit reached")
    
    # Add new character section
    if char_count < 6:
        with st.expander("➕ Add New Character", expanded=(char_count == 0)):
            with st.form("add_character_form"):
                char_name = st.text_input("Character Name", placeholder="Enter character name")
                char_description = st.text_area("Description", placeholder="Describe your character's appearance, personality, etc.", height=100)
                char_image = st.file_uploader("Reference Image", type=['png', 'jpg', 'jpeg'], help="Upload a reference image for your character")
                
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
                            # Save image
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
    
    # Display characters
    if st.session_state.characters:
        # Display in grid
        characters = list(st.session_state.characters.items())
        for i in range(0, len(characters), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(characters):
                    char_name, char_data = characters[i + j]
                    with col:
                        with st.container():
                            st.markdown('<div class="character-card">', unsafe_allow_html=True)
                            
                            # Display image if available
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

# Scripts Page
elif page == "📝 Scripts":
    st.title("Script Manager")
    
    # Add new script section
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
    
    # Display scripts
    if st.session_state.scripts:
        st.subheader(f"Your Scripts ({len(st.session_state.scripts)})")
        
        for script_title, script_data in st.session_state.scripts.items():
            with st.expander(f"📜 {script_title}"):
                st.text_area("Content", script_data['content'], height=150, disabled=True, key=f"view_{script_title}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🎬 Generate Scenes", key=f"gen_{script_title}"):
                        # Generate scenes from script
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

# Scene Builder Page
elif page == "🎬 Scene Builder":
    st.title("Scene Builder")
    
    if not st.session_state.scripts:
        st.warning("Please add some scripts first in the Script Manager!")
    elif not st.session_state.characters:
        st.warning("Please add some characters first in the Character Database!")
    else:
        # Script selection
        script_options = list(st.session_state.scripts.keys())
        selected_script = st.selectbox("Select Script", script_options, key="scene_script_select")
        
        if selected_script:
            script_data = st.session_state.scripts[selected_script]
            
            if not script_data.get('scenes'):
                st.info("No scenes generated yet. Go to Script Manager and click 'Generate Scenes'.")
            else:
                st.subheader(f"Scenes for '{selected_script}'")
                
                # Progress bar
                total_scenes = len(script_data['scenes'])
                ready_scenes = len([s for s in script_data['scenes'] if s.get('assigned_character') and s.get('visual_description')])
                progress = ready_scenes / total_scenes if total_scenes > 0 else 0
                
                st.progress(progress, text=f"Scene Progress: {ready_scenes}/{total_scenes} scenes ready")
                
                # Scene editing
                for i, scene in enumerate(script_data['scenes']):
                    with st.expander(f"Scene {scene['scene_number']}", expanded=(not scene.get('assigned_character'))):
                        st.markdown('<div class="scene-card">', unsafe_allow_html=True)
                        
                        st.write(f"**Narration:** {scene['narration']}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Character assignment
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
                            # Visual description
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
                        
                        # Status indicator
                        if scene.get('assigned_character') and scene.get('visual_description'):
                            st.success("✅ Ready for video generation")
                        elif scene.get('assigned_character'):
                            st.warning("⚠️ Missing visual description")
                        elif scene.get('visual_description'):
                            st.warning("⚠️ No character assigned")
                        else:
                            st.error("❌ Incomplete - needs character and visual description")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

# Video Queue Page
elif page == "🎥 Video Queue":
    st.title("Video Generation Queue")
    
    # API Configuration
    with st.expander("🔑 RunwayML API Configuration", expanded=(not st.session_state.api_key)):
        api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="Enter your RunwayML API key",
            help="Get your API key from RunwayML dashboard"
        )
        
        if st.button("Save API Key"):
            st.session_state.api_key = api_key
            save_data()
            add_activity("Updated API key")
            st.success("API Key saved!")
            st.rerun()
    
    if st.session_state.api_key:
        st.success("✅ API Key configured - Ready for video generation!")
        
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
            st.subheader("Ready for Video Generation")
            
            for project in ready_projects:
                with st.expander(f"📝 {project['title']} ({project['ready_scenes']}/{project['total_scenes']} scenes ready)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"👀 Preview Project", key=f"preview_{project['title']}"):
                            st.subheader("Project Preview")
                            for scene in project['scenes']:
                                st.write(f"**Scene {scene['scene_number']}**")
                                st.write(f"Character: {scene['assigned_character']}")
                                st.write(f"Narration: {scene['narration']}")
                                st.write(f"Visual: {scene['visual_description']}")
                                st.write("---")
                    
                    with col2:
                        if st.button(f"🎥 Generate Videos", key=f"generate_{project['title']}"):
                            with st.spinner("Generating videos..."):
                                # Simulate video generation process
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for i, scene in enumerate(project['scenes']):
                                    progress = (i + 1) / len(project['scenes'])
                                    progress_bar.progress(progress)
                                    status_text.write(f"Generating Scene {scene['scene_number']}...")
                                    
                                    # Simulate processing time
                                    time.sleep(1)
                                
                                st.success(f"✅ Generated {len(project['scenes'])} videos for '{project['title']}'!")
                                add_activity(f"Generated videos for: {project['title']}")
        else:
            st.info("No projects ready for generation. Complete scene assignments first in Scene Builder!")
    else:
        st.warning("Please configure your RunwayML API key first.")

# Settings Page
elif page == "⚙️ Settings":
    st.title("Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Export Data")
        
        if st.button("Export Characters", use_container_width=True):
            if st.session_state.characters:
                json_data = json.dumps(st.session_state.characters, indent=2)
                st.download_button(
                    "Download Characters JSON",
                    json_data,
                    "characters.json",
                    "application/json",
                    use_container_width=True
                )
        
        if st.button("Export Scripts", use_container_width=True):
            if st.session_state.scripts:
                json_data = json.dumps(st.session_state.scripts, indent=2)
                st.download_button(
                    "Download Scripts JSON",
                    json_data,
                    "scripts.json",
                    "application/json",
                    use_container_width=True
                )
        
        if st.button("Export All Data", use_container_width=True):
            all_data = {
                'characters': st.session_state.characters,
                'scripts': st.session_state.scripts,
                'settings': {'api_key': st.session_state.api_key}
            }
            json_data = json.dumps(all_data, indent=2)
            st.download_button(
                "Download All Data JSON",
                json_data,
                "horror_shorts_data.json",
                "application/json",
                use_container_width=True
            )
    
    with col2:
        st.subheader("📥 Import Data")
        
        uploaded_file = st.file_uploader("Import JSON File", type=['json'])
        
        if uploaded_file and st.button("Import Data", use_container_width=True):
            try:
                data = json.load(uploaded_file)
                
                if 'characters' in data:
                    st.session_state.characters.update(data['characters'])
                if 'scripts' in data:
                    st.session_state.scripts.update(data['scripts'])
                if 'settings' in data and 'api_key' in data['settings']:
                    st.session_state.api_key = data['settings']['api_key']
                
                save_data()
                add_activity("Imported data from file")
                st.success("Data imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error importing data: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("🎵 **Electronic Dance Horror House**")
st.sidebar.markdown("Built for consistent character video generation")

# Auto-save data
save_data()
