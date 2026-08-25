import socket
import imaplib
import email
import threading
import pyttsx3
from email.header import decode_header
import json
import streamlit as st
import ollama
import psutil
import logging
import smtplib
from email.mime.text import MIMEText
import pyautogui
import subprocess
import os
import time
from PIL import Image
import numpy as np


logging.getLogger("asyncio").setLevel(logging.CRITICAL)

MEMORY_FILE_PATH = "Chatbot/diamond_memory.json"





def save_convo_memory(messages_array) -> None:
    """Saves the current active conversation array state directly to disk."""
    try:
        with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(messages_array, file, ensure_ascii=False, indent=4)
    except Exception:
        pass

def load_convo_memory() -> list:
    """Reads historical conversations back from the storage file on system boot."""
    if os.path.exists(MEMORY_FILE_PATH):
        try:
            with open(MEMORY_FILE_PATH, "r", encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            return []
    return []

def send_email_message(recipient: str, subject: str, body: str) -> str:
    """Dispatches a secure text email message via Gmail's SMTP server network gateway."""
    SENDER_EMAIL = "Your_Email_Here"
    APP_PASSWORD = "your app password here"
    try:
        msg = MIMEText(body)
        msg['subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        with smtplib.SMTP_SSL("://gmail.com", 465, timeout=10) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        return f"Successfully sent your email message to {recipient}"
    except Exception as e:
        return f"Failed to send email. Server error details: {str(e)}"

def get_unread_emails(max_emails: int = 3) -> str:
    """
    connects to your email provider via IMAP and gets unread email summaries.
    """
    IMAP_SERVER = "://gmail.com"
    EMAIL = "Your_email_here"
    APP_PASSWORD = "YOUR_PASSWORD_HERE" 

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, APP_PASSWORD)
        mail.select("inbox", readonly=True)

        status, response_data = mail.search(None, 'UNSEEN')
        email_ids = response_data[0].split()

        if not email_ids:
            return "your inbox is all clear. No unread emails found"
        
        recent_ids = email_ids[-max_emails:]
        email_summaries = []

        for e_id in recent_ids:
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):

                    msg = email.message_from_bytes(response_part[1])


                    subject_parts = decode_header(msg["Subject"])
                    subject, encoding = subject_parts[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")


                    from_parts = decode_header(msg["From"])
                    from_sender, encoding = from_parts[0]
                    if isinstance(from_sender, bytes):
                        from_sender = from_sender.decode(encoding or "utf-8", errors="ignore")

                    email_summaries.append(f"📬 FROM: {from_sender}\nSUBJECT: {subject}\n---")
        

        mail.close()
        mail.logout()
        return "\n".join(email_summaries)
        
    except Exception as error_msg:
        return f"Could not access emails. Error details: {str(error_msg)}"

def get_cpu_status() -> str:
    """Reads the computer's current CPU utilization across all cores."""
    try:
        cpu_usage = psutil.cpu_percent(interval=1.0)
        core_count = psutil.cpu_count(logical=True)
        return f"Current CPU Usage: {cpu_usage}%\nTotal Logical CPU Cores: {core_count}"
    except Exception as e:
        return f"Failed to retrieve hardware metrics: {str(e)}"
    
def control_laptop_task(action_type: str, details: str) -> str:
    """Controls basic OS desktop tasks like opening an app or automatically typing a sentence."""
    try:
        if action_type.lower() == "open":
            app_map = {"notepad": "notepad.exe", "calculator": "calc.exe", "explorer": "explorer.exe"}
            if "diamondapps" in details.lower() or details.lower().endswith(".py"):
                clean_path = details.replace("/", "\\")
                subprocess.Popen(
                    ["Chatbot\\.venv\\Scripts\\python.exe", "-m", "streamlit", "run", clean_path, "--server.port", "8502"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                return f"Successfully launched your isolated app background worker: {details} on port 8502!"
            target = app_map.get(details.lower())
            if target:
                subprocess.Popen(target)
                return f"Successfully popped open {details} on your screen!"
            else:
                return f"I don't have a system shortcut mapped for '{details}' yet."
        elif action_type.lower() == "type":
            pyautogui.sleep(1)
            pyautogui.write(details, interval=0.05)
            return f"Finished typing out the text sequence: '{details}'"
        return f"Unknown laptop action command requested: '{action_type}'"
    except Exception as e:
        return f"Laptop control task failed. Error: {str(e)}"

def generate_local_app(app_filename: str, python_code_content: str) -> str:
    """Creates and saves a new standalone Python application file inside a dedicated folder."""
    try:
        output_directory = "DiamondApps"
        if not os.path.exists(output_directory): os.makedirs(output_directory)
        if not app_filename.endswith(".py"): app_filename += ".py"
        for marker in ["```python", "```"]:
            python_code_content = python_code_content.replace(marker, "")
        python_code_content = python_code_content.strip()
        file_path = os.path.join(output_directory, app_filename)
        with open(file_path, "w", encoding="utf-8") as f: f.write(python_code_content)
        return f"Successfully generated app! Saved at: {file_path}. Use laptop controller tool to 'open' it."
    except Exception as e:
        return f"Failed to generate application file. Error: {str(e)}"

def code_update(new_code_snippet: str = "", **kwargs) -> str:
    """Safely appends a new code block to dimaond.py without text chopping bugs."""
    try:
        script_path = "Chatbot/dimaond.py"
        if "new_full_script_content" in kwargs:
            new_code_snippet = kwargs["new_full_script_content"]
        for marker in ["```python", "```"]:
            new_code_snippet = new_code_snippet.replace(marker, "")
        new_code_snippet = new_code_snippet.strip()
        if len(new_code_snippet) < 10:
            return "Error: Generated script content is too short aborting for safety."
        with open(script_path, "a", encoding="utf-8") as f:
            f.write("\n\n" + new_code_snippet + "\n")
        return "Success! I have updated my code safely without text chopping errors."
    except Exception as e:
        return f"Failed to update code. Error details: {str(e)}"

def Security_camera_sweep(sweep_time: int = 3) -> str:
     """
     Triggers a stable browser webcam frame, encodes it, and hands it off to llama3.2-vision for a natural description.
     """
     try:
        st.markdown("### 📷 Diamond Security System: AI Multimodal Image Analyst")
        

        if "camera_scan_results" not in st.session_state:
            st.session_state.camera_scan_results = None
            
        img_file = st.camera_input("Please click below to snap an authentication image for AI scanning:")
        

        if img_file is not None and st.session_state.camera_scan_results is None:
            with st.spinner("💎 Diamond is analyzing image pixel channels locally..."):


                raw_image_bytes = img_file.getvalue()
                


                vision_response = ollama.chat(
                    model='llama3.2-vision',
                    messages=[{
                        'role': 'user',
                        'content': 'Describe what you see in this image in one concise, clear sentence. Focus on any people, objects, or context present.',
                        'images': [raw_image_bytes]
                    }]
                )
                

                image_description = vision_response['message']['content']
                

                st.session_state.camera_scan_results = f"Analysis Complete! Local Vision Insight:\n\n{image_description}"
        

        if st.session_state.camera_scan_results is not None:
            st.success(st.session_state.camera_scan_results)
            final_output = st.session_state.camera_scan_results
            st.session_state.camera_scan_results = None
            return final_output
            
        return "Camera frame verification is currently awaiting input inside the workspace control layout container block."
     except Exception as e:
        return f"Multimodal vision processing failed. Details: {str(e)}"

def voice_maker(text_to_speak: str) -> None:
    """
    Uses the system sound drivers to read text aloud completely offline without blocking execution.
    """
    def audio_worker(text):
        try:

            engine = pyttsx3.init()
            available_voices = engine.getProperty('voices')
            target_voice = available_voices[0] # type: ignore
            engine.setProperty('voice', target_voice.id)
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 1.0)
            

            clean_text = text.replace("💎", "").replace("🧑‍💻", "").replace("📬", "").strip()
            
            engine.say(clean_text)
            engine.runAndWait()
            

            if hasattr(engine, '_inLoop') and engine._inLoop:
                engine.endLoop()
        except Exception:
            pass


    thread = threading.Thread(target=audio_worker, args=(text_to_speak,))
    thread.daemon = True  
    thread.start()

def fire_wall_checker(traget_ip):
    ports_to_test  = [22, 80, 443, 3389, 8080]
    scan_log = []

    for port in ports_to_test:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            result = s.connect_ex((traget_ip, port))

            if result == 0:
                status = "OPEN (Vulnerable - No active firewall blockade)"
            elif result != 0 and result != 10061:
                status = "FILTERED (Protected - Active firewall dropping packets)"
            else:
                status = "CLOSED"

            scan_log.append(f"Port {port}: {status}")
            s.close()
        except Exception as e:
            scan_log.append(f"port {port}: Error scanning ({str(e)})")

availble_tools = {
    'get_cpu_status': get_cpu_status,
    'get_unread_emails': get_unread_emails,
    'send_email_message': send_email_message,
    'control_laptop_task': control_laptop_task,
    'generate_local_app': generate_local_app,
    'code_update': code_update,
    'Security_camera_sweep': Security_camera_sweep
}




st.set_page_config(page_title="AI multi-tool workspace", page_icon="💎", layout="centered")
st.markdown(
    """
    <style>
    .stApp { background-color: #041C0F !important; }
    div[data-testid="stChatInput"] { background-color: #0C2E1B !important; }
    h1, h2, h3, h4, h5, h6, p, span, div { color: #E2F4EA !important; }
    [data-testid="stSidebar"] { background-color: #020F08 !important; border-right: 1px solid #00FF7F; }
    </style>
    """,
    unsafe_allow_html=True
)


with st.sidebar:
    st.markdown("## ⚙️ Diamond Core Desk")
    st.markdown("Actively toggle features on or off to completely flush unneeded files from your shared laptop RAM memory blocks.")
    

    allow_vision_portal = st.checkbox("📷 Mount Live Integrated Vision Portal", value=True)
    allow_voice_engine = st.checkbox("🔊 Enable Offline System Voice", value=True)
    
    st.markdown("---")
    if st.button("🗑️ Clear Hidden Memory Cache File", use_container_width=True):
        if os.path.exists(MEMORY_FILE_PATH):
            os.remove(MEMORY_FILE_PATH)
        st.session_state.messages = []
        st.rerun()


st.markdown("<h3 style='display: flex; align-items: center; gap: 10px; margin-bottom: 0px;'><span style='filter: hue-rotate(110deg) saturate(3.5); font-size: 32px;'>💎</span> Diamond: Unified Intelligence Terminal</h3>", unsafe_allow_html=True)
st.markdown("<div style='display: inline-block; background-color: #0C2E1B; border: 1px solid #00FF7F; padding: 4px 12px; border-radius: 20px; font-size: 13px; color: #00FF7F; font-weight: bold; margin-top: 5px; margin-bottom: 20px;'>🟢 System Status: Optimal</div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = load_convo_memory()





if allow_vision_portal:
    st.markdown("#### 📷 Integrated Vision Portal")
    img_file = st.camera_input("Snap an analysis frame to feed directly to Diamond's vision matrix:")

    if img_file is not None:
        if "last_processed_img" not in st.session_state or st.session_state.last_processed_img != img_file.file_id:
            with st.spinner("💎 Diamond is running optical pixel analysis passes..."):
                raw_image_bytes = img_file.getvalue()
                try:
                    vision_response = ollama.chat(
                        model='qwen2.5vl',
                        messages=[{
                            'role': 'user',
                            'content': 'Describe what you see in this image in one concise, clear sentence. Focus on any people, objects, or context present.',
                            'images': [raw_image_bytes]
                        }]
                    )
                    vision_text = vision_response['message']['content']
                    
                    st.session_state.messages.append({"role": "user", "content": "[Uploaded Camera Snapshot Checkpoint]"})
                    st.session_state.messages.append({"role": "assistant", "content": f"Vision Analysis: {vision_text}"})
                    save_convo_memory(st.session_state.messages)
                    st.session_state.last_processed_img = img_file.file_id
                    
                    st.success(f"👁️ **AI Description Result:** {vision_text}")
                    

                    if allow_voice_engine:
                        voice_maker(f"Analysis Complete! {vision_text}")
                        
                except Exception as vision_err:
                    st.error(f"Vision model connection failed: {str(vision_err)}")
else:
    st.markdown("<div style='color: #a1a1a1; font-size: 13px; font-style: italic; padding: 10px 0;'>🔒 Integrated Vision Portal has been unmounted. Camera hardware channels are offline to save RAM memory profiles.</div>", unsafe_allow_html=True)




st.markdown("---")
st.markdown("#### 🛡️ Infrastructure Firewall Interrogator")

target_ip = st.text_input("Target Network IP Address", value="127.0.0.1")
ports_to_test = [21, 22, 80, 443, 3389, 8080]

if st.button("🚀 Launch Live Firewall Audit", use_container_width=True):
    scan_results = []
    st.markdown("### 📡 Active Network Probing...")
    
    for port in ports_to_test:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            result = s.connect_ex((target_ip, port))
            
            if result == 0:
                status = "OPEN (Vulnerable - No active firewall blockade)"
            elif result != 0 and result != 10061:
                status = "FILTERED (Protected - Active firewall dropping packets)"
            else:
                status = "CLOSED"
                
            scan_results.append(f"Port {port}: {status}")
            st.text(f"📡 Probed Port {port}... Status: {status}")
            s.close()
        except Exception as e:
            scan_results.append(f"Port {port}: Error ({str(e)})")

    raw_network_data = "\n".join(scan_results)
    
    with st.spinner("🧠 Handing telemetry to Diamond Core reasoning matrix..."):
        try:
            firewall_prompt = (
                "You are Diamond, an elite offensive security defense assistant. "
                "Review the following live port scan results. Highlight which doors are left open, "
                "explain exactly how an adversary would target those specific open ports, "
                "and write a highly detailed step-by-step recommendation list explaining how "
                "the administrator can configure their firewall rules to make it better and safer."
            )
            
            response = ollama.chat(
                model='llama3',
                messages=[
                    {'role': 'system', 'content': firewall_prompt},
                    {'role': 'user', 'content': f"Live Telemetry for target {target_ip}:\n\n{raw_network_data}"}
                ]
            )
            
            st.markdown("##### 🎯 DIAMOND HARDENING FEEDBACK REPORT:")
            st.info(response['message']['content'])
            

            st.session_state.messages.append({"role": "user", "content": f"[Ran Firewall Scan on {target_ip}]"})
            st.session_state.messages.append({"role": "assistant", "content": response['message']['content']})
            save_convo_memory(st.session_state.messages)
            
        except Exception as e:
            st.error(f"Diamond System Core Offline: {str(e)}")

if st.session_state.get("scan_report_output"):
    st.markdown("##### 🎯 DIAMOND HARDENING FEEDBACK REPORT:")
    st.info(st.session_state.scan_report_output)

st.markdown("---")
st.markdown("#### 💬 Core Conversation Grid")




if user_input := st.chat_input("what is bugging you."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_convo_memory(st.session_state.messages)
    
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="💎"):
        tool_manifest = [
            {
                'type': 'function',
                'function': {
                    'name': 'get_cpu_status',
                    'description': 'Retrieves the real time cpu percentage and core count of the local machine',
                    'parameters': {'type': 'object', 'properties': {}}
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'control_laptop_task',
                    'description': 'Controls basic operating system operations like opening desktop apps or typing a text sequence.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'action_type': {'type': 'string', 'description': 'Must be exactly either "open" or "type".'},
                            'details': {'type': 'string', 'description': 'The application name to open OR the text sentence you want typed.'}
                        },
                        'required': ['action_type', 'details']
                    }
                }
            }
        ]


        system_instruction = {
            "role": "system",
            "content": (
                "You are Diamond, an elite, highly capable, and sleek AI desktop terminal assistant running completely offline on your user's machine. "
                "You possess powerful custom source-code system automation capabilities built into your core environment, which include: "
                "- Monitoring your machine's live hardware performance and core CPU status "
                "- Automating operating system actions like opening desktop apps or typing strings using mouse/keyboard simulation shortcuts "
                "- Connecting to secure email channels to scan unread messages or dispatch new text emails "
                "- Writing, saving, and updating standalone Python software applications directly inside your project storage directory folders "
                "- Analyzing visual camera snapshots directly through your unified vision console layout "
                "Always stay firmly in character as an intelligent, helpful custom terminal interface. If the user asks what tools you have, "
                "list and describe these skills conversationally in plain English text. Do NOT make any actual tool or function calls unless the user "
                "explicitly commands you to execute a specific task. Also you are an elite defense engineer. Review these live port states, write a detailed vulnerability analysis, and explain how the user can make their firewall better."
            )
        }


        payload_messages = [system_instruction] + st.session_state.messages

        try:
            ai_response = ollama.chat(
                model='qwen2.5:3b', 
                messages=payload_messages, 
                tools=tool_manifest
            )
            
            if ai_response.get('message', {}).get('tool_calls'):
                for call in ai_response['message']['tool_calls']:
                    tool_requested = call['function']['name']
                    tool_arguments = call['function'].get('arguments', {})

                    if tool_requested in availble_tools:
                        with st.spinner(""):
                            st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; color: #a1a1a1; padding: 10px 0;'><span style='filter: hue-rotate(110deg) saturate(3.5); font-size: 24px; display: inline-block;'>💎</span> <span>Diamond is executing background tool: {tool_requested}...</span></div>", unsafe_allow_html=True)
                            tool_output = availble_tools[tool_requested](**tool_arguments)
                        
                        st.session_state.messages.append(ai_response['message'])
                        st.session_state.messages.append({'role': 'tool', 'name': tool_requested, 'content': tool_output})


                        final_payload = [system_instruction] + st.session_state.messages


                        final_pass = ollama.chat(model='qwen2.5:3b', messages=final_payload)
                        agent_reply = final_pass['message']['content']
                        st.markdown(agent_reply)
                        
                        if allow_voice_engine:
                            voice_maker(agent_reply)
                            
                        st.session_state.messages.append({"role": "assistant", "content": agent_reply})
                        save_convo_memory(st.session_state.messages)
            else:
                agent_reply = ai_response['message']['content']
                st.markdown(agent_reply)
                
                if allow_voice_engine:
                    voice_maker(agent_reply)
                    
                st.session_state.messages.append({"role": "assistant", "content": agent_reply})
                save_convo_memory(st.session_state.messages)
                
        except Exception as e:
            st.error(f"Ollama integration error: {str(e)}")