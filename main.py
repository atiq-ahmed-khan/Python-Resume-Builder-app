import streamlit as st 
import pandas as pd
from PIL import Image, ImageDraw
import base64
from fpdf import FPDF
import time
import json
import io
import os
import tempfile
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Professional Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Improved CSS styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: white;
    padding: 2rem;
    border-radius: 1rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.section-card {
    background: white;
    padding: 1.5rem;
    border-radius: 0.75rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

.stButton > button {
    background: #2563eb;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: #1d4ed8;
    transform: translateY(-2px);
}

.profile-image {
    border-radius: 50% !important;
    border: 4px solid #2563eb !important;
    padding: 4px !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    aspect-ratio: 1 !important;
    object-fit: cover !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
}

.profile-image:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3) !important;
}

.form-section {
    background: white;
    padding: 1.5rem;
    border-radius: 0.75rem;
    margin-bottom: 1rem;
}

.custom-file-upload {
    border: 2px dashed #2563eb;
    border-radius: 0.5rem;
    padding: 1rem;
    text-align: center;
    cursor: pointer;
}

.info-box {
    background: #f0f9ff;
    border-left: 4px solid #2563eb;
    padding: 1rem;
    margin: 1rem 0;
}

.success-message {
    background: #dcfce7;
    color: #166534;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.error-message {
    background: #fee2e2;
    color: #991b1b;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.download-button {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: #2563eb;
    color: white !important;
    text-decoration: none;
    border-radius: 0.5rem;
    transition: all 0.3s ease;
    margin: 1rem 0;
    font-weight: 500;
}

.download-button:hover {
    background: #1d4ed8;
    transform: translateY(-2px);
    color: white !important;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# Enhanced template designs
TEMPLATES = {
    "Executive": {
        "colors": {
            "primary": "#1a365d",
            "secondary": "#2c5282",
            "text": "#2d3748",
            "accent": "#90cdf4"
        },
        "font": "Helvetica",
        "spacing": 1.2,
        "borders": True,
        "header_style": "gradient",
        "section_style": "bordered"
    },
    "Ultra Modern": {
        "colors": {
            "primary": "#e53e3e",
            "secondary": "#c53030",
            "text": "#2d3748",
            "accent": "#fed7d7"
        },
        "font": "Helvetica",
        "spacing": 1.4,
        "borders": False,
        "header_style": "bold",
        "section_style": "modern"
    },
    "Professional Plus": {
        "colors": {
            "primary": "#2b6cb0",
            "secondary": "#2c5282",
            "text": "#2d3748",
            "accent": "#bee3f8"
        },
        "font": "Helvetica",
        "spacing": 1.25,
        "borders": True,
        "header_style": "professional",
        "section_style": "boxed"
    }
}

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = {
        'personal': {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'summary': '',
            'profile_image': None,
            'linkedin': '',
            'github': '',
            'website': ''
        },
        'education': [],
        'experience': [],
        'skills': {
            'technical': [],
            'soft': [],
            'languages': []
        },
        'projects': [],
        'certifications': [],
        'custom_sections': {},
        'section_order': [
            'personal',
            'education',
            'experience',
            'skills',
            'projects',
            'certifications'
        ]
    }

if 'template' not in st.session_state:
    st.session_state.template = "Executive"

class ResumePDF(FPDF):
    def __init__(self, template):
        super().__init__()
        self.template = TEMPLATES[template]
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d")} | Created by Riaz Hussain, Senior Student', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font(self.template['font'], 'B', 14)
        rgb = tuple(int(self.template["colors"]["primary"].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.set_text_color(*rgb)
        
        if self.template["header_style"] == "gradient":
            self.set_fill_color(*rgb)
            self.cell(0, 10, title, 0, 1, 'L', True)
        else:
            self.cell(0, 10, title, 0, 1, 'L')
        
        if self.template["borders"]:
            self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        
        self.ln(4)

def save_profile_image(image):
    if image is not None:
        try:
            img = Image.open(image)
            img = img.convert('RGB')
            
            # Make the image square first
            size = min(img.size)
            left = (img.width - size) // 2
            top = (img.height - size) // 2
            right = left + size
            bottom = top + size
            img = img.crop((left, top, right, bottom))
            
            # Create circular mask
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            
            # Apply mask and resize
            output = Image.new('RGB', (size, size), (255, 255, 255))
            output.paste(img, (0, 0))
            output.putalpha(mask)
            
            # Resize to desired dimensions
            final_size = (200, 200)
            output = output.resize(final_size, Image.LANCZOS)
            
            buf = io.BytesIO()
            output.save(buf, format='PNG')
            return buf.getvalue()
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
    return None

def create_pdf(data, template="Executive"):
    pdf = ResumePDF(template)
    template_settings = TEMPLATES[template]
    pdf.add_page()
    
    # Personal Information
    if data['personal']['profile_image']:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(data['personal']['profile_image'])
                # Position the image in the top-right corner
                pdf.image(tmp.name, x=170, y=10, w=30, h=30)
            os.unlink(tmp.name)
        except Exception as e:
            st.error(f"Error adding profile image: {str(e)}")
    
    # Name and Contact
    pdf.set_font(template_settings['font'], 'B', 24)
    rgb = tuple(int(template_settings["colors"]["primary"].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    pdf.set_text_color(*rgb)
    pdf.cell(0, 10, data['personal']['name'] or "Your Name", ln=True)
    
    pdf.set_font(template_settings['font'], '', 11)
    pdf.set_text_color(int(template_settings["colors"]["text"].lstrip('#')[0:2], 16),
                      int(template_settings["colors"]["text"].lstrip('#')[2:4], 16),
                      int(template_settings["colors"]["text"].lstrip('#')[4:6], 16))
    
    contact_info = []
    if data['personal']['email']:
        contact_info.append(f"📧 {data['personal']['email']}")
    if data['personal']['phone']:
        contact_info.append(f"📱 {data['personal']['phone']}")
    if data['personal']['location']:
        contact_info.append(f"📍 {data['personal']['location']}")
    
    pdf.cell(0, 6, ' | '.join(contact_info) if contact_info else "Contact Information", ln=True)
    
    # Social Links
    social_links = []
    if data['personal']['linkedin']:
        social_links.append(f"LinkedIn: {data['personal']['linkedin']}")
    if data['personal']['github']:
        social_links.append(f"GitHub: {data['personal']['github']}")
    if data['personal']['website']:
        social_links.append(f"Website: {data['personal']['website']}")
    
    if social_links:
        pdf.cell(0, 6, ' | '.join(social_links), ln=True)
    
    # Professional Summary
    if data['personal']['summary']:
        pdf.ln(4)
        pdf.set_font(template_settings['font'], 'B', 12)
        pdf.cell(0, 6, 'Professional Summary', ln=True)
        pdf.set_font(template_settings['font'], '', 11)
        pdf.multi_cell(0, 6, data['personal']['summary'])

    # Add sections based on order
    for section in data['section_order']:
        pdf.ln(10)
        
        if section == 'education' and data['education']:
            pdf.chapter_title('Education')
            for edu in data['education']:
                pdf.set_font(template_settings['font'], 'B', 11)
                pdf.cell(0, 6, f"{edu['degree']} - {edu['institution']}", ln=True)
                pdf.set_font(template_settings['font'], '', 10)
                pdf.cell(0, 6, f"{edu['year']} | GPA: {edu['gpa']}", ln=True)
                pdf.ln(2)
        
        elif section == 'experience' and data['experience']:
            pdf.chapter_title('Professional Experience')
            for exp in data['experience']:
                pdf.set_font(template_settings['font'], 'B', 11)
                pdf.cell(0, 6, f"{exp['position']} at {exp['company']}", ln=True)
                pdf.set_font(template_settings['font'], 'I', 10)
                pdf.cell(0, 6, exp['duration'], ln=True)
                pdf.set_font(template_settings['font'], '', 10)
                pdf.multi_cell(0, 6, exp['description'])
                pdf.ln(2)
        
        elif section == 'skills' and (data['skills']['technical'] or data['skills']['soft'] or data['skills']['languages']):
            pdf.chapter_title('Skills')
            
            if data['skills']['technical']:
                pdf.set_font(template_settings['font'], 'B', 11)
                pdf.cell(0, 6, 'Technical Skills', ln=True)
                pdf.set_font(template_settings['font'], '', 10)
                pdf.multi_cell(0, 6, ', '.join(data['skills']['technical']))
                pdf.ln(2)
            
            if data['skills']['soft']:
                pdf.set_font(template_settings['font'], 'B', 11)
                pdf.cell(0, 6, 'Soft Skills', ln=True)
                pdf.set_font(template_settings['font'], '', 10)
                pdf.multi_cell(0, 6, ', '.join(data['skills']['soft']))
                pdf.ln(2)
            
            if data['skills']['languages']:
                pdf.set_font(template_settings['font'], 'B', 11)
                pdf.cell(0, 6, 'Languages', ln=True)
                pdf.set_font(template_settings['font'], '', 10)
                pdf.multi_cell(0, 6, ', '.join(data['skills']['languages']))
        
        elif section == 'projects' and data['projects']:
            pdf.chapter_title('Projects')
            for project in data['projects']:
                pdf.set_font(template_settings['font'], 'B', 11)
                pdf.cell(0, 6, project['name'], ln=True)
                pdf.set_font(template_settings['font'], 'I', 10)
                pdf.cell(0, 6, project['duration'], ln=True)
                pdf.set_font(template_settings['font'], '', 10)
                pdf.multi_cell(0, 6, project['description'])
                pdf.ln(2)
        
        elif section == 'certifications' and data['certifications']:
            pdf.chapter_title('Certifications')
            for cert in data['certifications']:
                pdf.set_font(template_settings['font'], 'B', 11)
                pdf.cell(0, 6, cert['name'], ln=True)
                pdf.set_font(template_settings['font'], '', 10)
                pdf.cell(0, 6, f"Issuer: {cert['issuer']} | Date: {cert['date']}", ln=True)
                pdf.ln(2)
        
        elif section in data['custom_sections'] and data['custom_sections'][section]:
            pdf.chapter_title(section)
            for entry in data['custom_sections'][section]:
                pdf.set_font(template_settings['font'], 'B', 11)
                pdf.cell(0, 6, entry['title'], ln=True)
                if entry.get('date'):
                    pdf.set_font(template_settings['font'], 'I', 10)
                    pdf.cell(0, 6, entry['date'], ln=True)
                pdf.set_font(template_settings['font'], '', 10)
                pdf.multi_cell(0, 6, entry['description'])
                pdf.ln(2)
    
    # Use a temporary file to generate PDF and read as bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, 'rb') as f:
            pdf_bytes = f.read()
    os.unlink(tmp.name)
    return pdf_bytes

def render_personal_info():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("👤 Personal Information")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", st.session_state.resume_data['personal']['name'])
        email = st.text_input("Email", st.session_state.resume_data['personal']['email'])
        phone = st.text_input("Phone", st.session_state.resume_data['personal']['phone'])
        location = st.text_input("Location", st.session_state.resume_data['personal']['location'])
    
    with col2:
        linkedin = st.text_input("LinkedIn URL", st.session_state.resume_data['personal']['linkedin'])
        github = st.text_input("GitHub URL", st.session_state.resume_data['personal']['github'])
        website = st.text_input("Personal Website", st.session_state.resume_data['personal']['website'])
        
        uploaded_file = st.file_uploader("Profile Picture", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            st.session_state.resume_data['personal']['profile_image'] = save_profile_image(uploaded_file)
            if st.session_state.resume_data['personal']['profile_image']:
                st.image(st.session_state.resume_data['personal']['profile_image'], width=150, output_format='PNG')
    
    summary = st.text_area("Professional Summary", st.session_state.resume_data['personal']['summary'])
    
    if st.button("Save Personal Information"):
        st.session_state.resume_data['personal'].update({
            'name': name,
            'email': email,
            'phone': phone,
            'location': location,
            'linkedin': linkedin,
            'github': github,
            'website': website,
            'summary': summary
        })
        st.success("Personal information saved successfully!")

def render_education():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("🎓 Education")
    
    with st.form("education_form"):
        degree = st.text_input("Degree/Certification")
        institution = st.text_input("Institution")
        col1, col2 = st.columns(2)
        with col1:
            year = st.text_input("Year")
        with col2:
            gpa = st.text_input("GPA")
        
        if st.form_submit_button("Add Education"):
            st.session_state.resume_data['education'].append({
                'degree': degree,
                'institution': institution,
                'year': year,
                'gpa': gpa
            })
            st.success("Education added successfully!")
            time.sleep(1)
            st.rerun()
    
    if st.session_state.resume_data['education']:
        st.markdown("### Current Education Entries")
        for i, edu in enumerate(st.session_state.resume_data['education']):
            with st.expander(f"{edu['degree']} at {edu['institution']}"):
                st.write(f"Year: {edu['year']}")
                st.write(f"GPA: {edu['gpa']}")
                if st.button("Remove", key=f"del_edu_{i}"):
                    st.session_state.resume_data['education'].pop(i)
                    st.rerun()

def render_experience():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("💼 Professional Experience")
    
    with st.form("experience_form"):
        position = st.text_input("Position Title")
        company = st.text_input("Company Name")
        duration = st.text_input("Duration (e.g., Jan 2020 - Present)")
        description = st.text_area("Job Description")
        
        if st.form_submit_button("Add Experience"):
            st.session_state.resume_data['experience'].append({
                'position': position,
                'company': company,
                'duration': duration,
                'description': description
            })
            st.success("Experience added successfully!")
            time.sleep(1)
            st.rerun()
    
    if st.session_state.resume_data['experience']:
        st.markdown("### Current Experience Entries")
        for i, exp in enumerate(st.session_state.resume_data['experience']):
            with st.expander(f"{exp['position']} at {exp['company']}"):
                st.write(f"Duration: {exp['duration']}")
                st.write(f"Description: {exp['description']}")
                if st.button("Remove", key=f"del_exp_{i}"):
                    st.session_state.resume_data['experience'].pop(i)
                    st.rerun()

def render_skills():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("🛠️ Skills")
    
    tabs = st.tabs(["Technical Skills", "Soft Skills", "Languages"])
    
    with tabs[0]:
        tech_skills = st.text_area(
            "Technical Skills (one per line)",
            value='\n'.join(st.session_state.resume_data['skills']['technical'])
        )
        if st.button("Save Technical Skills"):
            st.session_state.resume_data['skills']['technical'] = [
                skill.strip() for skill in tech_skills.split('\n') if skill.strip()
            ]
            st.success("Technical skills saved!")
    
    with tabs[1]:
        soft_skills = st.text_area(
            "Soft Skills (one per line)",
            value='\n'.join(st.session_state.resume_data['skills']['soft'])
        )
        if st.button("Save Soft Skills"):
            st.session_state.resume_data['skills']['soft'] = [
                skill.strip() for skill in soft_skills.split('\n') if skill.strip()
            ]
            st.success("Soft skills saved!")
    
    with tabs[2]:
        languages = st.text_area(
            "Languages (one per line)",
            value='\n'.join(st.session_state.resume_data['skills']['languages'])
        )
        if st.button("Save Languages"):
            st.session_state.resume_data['skills']['languages'] = [
                lang.strip() for lang in languages.split('\n') if lang.strip()
            ]
            st.success("Languages saved!")

def render_projects():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("🚀 Projects")
    
    with st.form("project_form"):
        name = st.text_input("Project Name")
        duration = st.text_input("Duration (e.g., Mar 2023 - Jun 2023)")
        description = st.text_area("Project Description")
        
        if st.form_submit_button("Add Project"):
            st.session_state.resume_data['projects'].append({
                'name': name,
                'duration': duration,
                'description': description
            })
            st.success("Project added successfully!")
            time.sleep(1)
            st.rerun()
    
    if st.session_state.resume_data['projects']:
        st.markdown("### Current Projects")
        for i, project in enumerate(st.session_state.resume_data['projects']):
            with st.expander(f"{project['name']}"):
                st.write(f"Duration: {project['duration']}")
                st.write(f"Description: {project['description']}")
                if st.button("Remove", key=f"del_proj_{i}"):
                    st.session_state.resume_data['projects'].pop(i)
                    st.rerun()

def render_certifications():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("📜 Certifications")
    
    with st.form("certification_form"):
        name = st.text_input("Certification Name")
        issuer = st.text_input("Issuing Organization")
        date = st.text_input("Date Obtained")
        
        if st.form_submit_button("Add Certification"):
            st.session_state.resume_data['certifications'].append({
                'name': name,
                'issuer': issuer,
                'date': date
            })
            st.success("Certification added successfully!")
            time.sleep(1)
            st.rerun()
    
    if st.session_state.resume_data['certifications']:
        st.markdown("### Current Certifications")
        for i, cert in enumerate(st.session_state.resume_data['certifications']):
            with st.expander(f"{cert['name']}"):
                st.write(f"Issuer: {cert['issuer']}")
                st.write(f"Date: {cert['date']}")
                if st.button("Remove", key=f"del_cert_{i}"):
                    st.session_state.resume_data['certifications'].pop(i)
                    st.rerun()

def render_section_order():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("🔄 Section Order")
    
    sections = st.session_state.resume_data['section_order']
    for i in range(len(sections)):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(sections[i])
        with col2:
            if i > 0 and st.button("↑", key=f"up_{i}"):
                sections[i], sections[i-1] = sections[i-1], sections[i]
                st.rerun()
        with col3:
            if i < len(sections)-1 and st.button("↓", key=f"down_{i}"):
                sections[i], sections[i+1] = sections[i+1], sections[i]
                st.rerun()

def render_preview_download():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("📄 Preview & Download")
    
    if st.button("Generate Resume PDF"):
        try:
            pdf_output = create_pdf(st.session_state.resume_data, st.session_state.template)
            b64_pdf = base64.b64encode(pdf_output).decode('utf-8')
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="resume.pdf" class="download-button">📥 Download Resume PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("Resume generated successfully! Click the button above to download.")
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
    
    if st.button("Save Resume Data"):
        try:
            resume_data = st.session_state.resume_data.copy()
            if resume_data['personal']['profile_image']:
                resume_data['personal']['profile_image'] = base64.b64encode(
                    resume_data['personal']['profile_image']
                ).decode('utf-8')
            data_str = json.dumps(resume_data, indent=2)
            b64_data = base64.b64encode(data_str.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64_data}" download="resume_data.json" class="download-button">💾 Download Resume Data</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("Resume data saved! Click the button above to download.")
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")

def main():
    st.markdown("""
    <div class="main-header">
        <h1>Professional Resume Builder</h1>
        <p>Create a stunning professional resume in minutes</p>
        <p>Created by Riaz Hussain, Senior Student</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📝 Resume Sections")
        section = st.radio(
            "Choose section to edit:",
            ["Personal Information", "Education", "Experience", "Skills",
             "Projects", "Certifications", "Section Order", "Preview & Download"]
        )
        
        st.header("🎨 Template")
        st.session_state.template = st.selectbox(
            "Choose template:",
            list(TEMPLATES.keys())
        )
    
    if section == "Personal Information":
        render_personal_info()
    elif section == "Education":
        render_education()
    elif section == "Experience":
        render_experience()
    elif section == "Skills":
        render_skills()
    elif section == "Projects":
        render_projects()
    elif section == "Certifications":
        render_certifications()
    elif section == "Section Order":
        render_section_order()
    elif section == "Preview & Download":
        render_preview_download()

if __name__ == "__main__":
    main()