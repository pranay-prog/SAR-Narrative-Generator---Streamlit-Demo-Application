"""
SAR Narrative Generator - Streamlit Demo Application
Main interface for generating SAR narratives with full audit trail and explainability
"""

import streamlit as st
import json
import os
from datetime import datetime
from sar_generator import SARGenerator, calculate_time_savings
import time

# Page configuration
st.set_page_config(
    page_title="SAR Narrative Generator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E75B6;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E75B6;
    }
    .confidence-high {
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 4px solid #28a745;
    }
    .confidence-medium {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 4px solid #ffc107;
    }
    .confidence-low {
        background-color: #f8d7da;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 4px solid #dc3545;
    }
    .audit-trail-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #2E75B6;
        margin-top: 1rem;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2E75B6;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .clickable-sentence {
        cursor: pointer;
        padding: 0.2rem;
        border-radius: 0.2rem;
        transition: background-color 0.2s;
    }
    .clickable-sentence:hover {
        background-color: #e8f4f8;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_sar' not in st.session_state:
    st.session_state.generated_sar = None
if 'selected_sentence' not in st.session_state:
    st.session_state.selected_sentence = None
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'edited_content' not in st.session_state:
    st.session_state.edited_content = {}
if 'generation_time' not in st.session_state:
    st.session_state.generation_time = None

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x80/2E75B6/FFFFFF?text=SAR+Generator", use_container_width=True)
    
    st.markdown("### ⚙️ Configuration")
    
    # API Key input (optional - works without it using templates)
    api_key = st.text_input(
        "Anthropic API Key (Optional)",
        type="password",
        help="Enter your API key for Claude integration. Demo works without it using templates."
    )
    
    st.markdown("---")
    
    st.markdown("### 📁 Case Selection")
    
    # Define available cases
    case_options = {
        "Case 1: Rapid Fund Movement": {
            "file": "sample_case_data.json",
            "description": "₹50L from 47 accounts in 7 days → immediate foreign wire"
        },
        "Case 2: Trade-Based Money Laundering": {
            "file": "case_trade_based_ml.json",
            "description": "Over-invoicing electronics imports - ₹2.8 crores suspicious"
        },
        "Case 3: Structuring / Smurfing": {
            "file": "case_structuring.json",
            "description": "23 cash deposits below ₹50K threshold across 5 branches"
        }
    }
    
    # Load sample case
    selected_case = st.selectbox(
        "Select Case",
        list(case_options.keys()),
        help="Select a case to generate SAR narrative"
    )
    
    # Show case description
    st.caption(case_options[selected_case]["description"])
    
    # Load case data
    @st.cache_data
    def load_case_data(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error(f"Case file not found: {filename}")
            st.stop()
    
    try:
        case_data = load_case_data(case_options[selected_case]["file"])
        
        st.markdown(f"""
        **Case ID:** {case_data['case_id']}  
        **Alert Date:** {case_data['alert_date']}  
        **Customer:** {case_data['customer']['name']}  
        **Alert Type:** {case_data['alert_details']['alert_type']}  
        **Priority:** {case_data['alert_details']['alert_priority']}
        """)
        
    except Exception as e:
        st.error(f"Error loading case data: {str(e)}")
        st.stop()
    
    st.markdown("---")
    
    # Generate button
    if st.button("🚀 Generate SAR Narrative", type="primary", use_container_width=True):
        with st.spinner("Generating SAR narrative with audit trail..."):
            start_time = time.time()
            
            # Initialize generator
            generator = SARGenerator(anthropic_api_key=api_key if api_key else None)
            
            # Generate SAR
            result = generator.generate_sar_narrative(case_data)
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Store in session state
            st.session_state.generated_sar = result
            st.session_state.generation_time = generation_time
            st.session_state.edit_mode = False
            st.session_state.edited_content = {}
            
            st.success(f"✅ SAR Generated in {generation_time:.1f} seconds!")
    
    # Action buttons
    if st.session_state.generated_sar:
        st.markdown("---")
        st.markdown("### 📝 Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Edit", use_container_width=True):
                st.session_state.edit_mode = not st.session_state.edit_mode
        
        with col2:
            if st.button("📄 Export PDF", use_container_width=True):
                st.info("PDF export functionality would download the SAR as a formatted PDF document.")
        
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.generated_sar = None
            st.session_state.selected_sentence = None
            st.session_state.edit_mode = False
            st.rerun()

# Main content area
st.markdown('<p class="main-header">SAR Narrative Generator with Audit Trail</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transforming Compliance Through Explainable AI</p>', unsafe_allow_html=True)

if st.session_state.generated_sar is None:
    # Welcome screen
    st.markdown("## 👋 Welcome to the SAR Narrative Generator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>⏱️ 80% Time Savings</h3>
            <p>Reduce SAR drafting from 5-6 hours to under 1 hour</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🔍 Full Transparency</h3>
            <p>Complete audit trail with data lineage for every statement</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>✅ Regulatory Ready</h3>
            <p>FinCEN-compliant narratives with automated validation</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 How It Works")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        #### 1️⃣ Select a Case
        Choose from your alert queue or upload case data
        
        #### 2️⃣ Generate Narrative
        AI analyzes transactions and generates a complete SAR narrative
        
        #### 3️⃣ Review with Audit Trail
        Click any sentence to see the source data and reasoning
        
        #### 4️⃣ Edit & Approve
        Make necessary edits and approve for filing
        """)
    
    with col2:
        st.markdown("#### 📊 Available Sample Cases")
        
        cases_preview = {
            "Case 1: Rapid Fund Movement": "47 transactions, ₹50L, 7 days",
            "Case 2: Trade-Based ML": "₹42.5L over-invoicing scheme",
            "Case 3: Smurfing": "32 deposits, 28 depositors",
            "Case 4: Shell Companies": "₹1.25Cr circular flow"
        }
        
        for case_name, case_summary in cases_preview.items():
            st.markdown(f"**{case_name}**")
            st.caption(case_summary)
            st.markdown("")
    
    st.markdown("---")
    st.info("👈 Click **Generate SAR Narrative** in the sidebar to get started!")

else:
    # Generated SAR display
    result = st.session_state.generated_sar
    
    # Metrics at top
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Generation Time", f"{st.session_state.generation_time:.1f}s")
    
    with col2:
        time_savings = calculate_time_savings()
        st.metric("Time Saved", time_savings['time_saved'])
    
    with col3:
        avg_confidence = sum(1 for s in result['sections'] if s.get('confidence') == 'high') / len(result['sections'])
        st.metric("Avg Confidence", f"{avg_confidence*100:.0f}%")
    
    with col4:
        compliant = sum(1 for v in result['compliance_checklist'].values() if v)
        total = len(result['compliance_checklist'])
        st.metric("Compliance", f"{compliant}/{total}")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 SAR Narrative", 
        "🔍 Audit Trail", 
        "💡 AI Reasoning", 
        "✅ Compliance Check"
    ])
    
    with tab1:
        st.markdown("### Generated SAR Narrative")
        
        if st.session_state.edit_mode:
            st.info("✏️ **Edit Mode Active** - Modify the narrative sections below")
        
        for i, section in enumerate(result['sections']):
            section_title = section['title']
            section_content = section['content']
            section_confidence = section.get('confidence', 'medium')
            
            # Show section with confidence indicator
            confidence_class = f"confidence-{section_confidence}"
            
            st.markdown(f'<div class="{confidence_class}">', unsafe_allow_html=True)
            st.markdown(f"#### {section_title}")
            
            # Confidence badge
            confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
            st.caption(f"{confidence_emoji.get(section_confidence, '🟡')} Confidence: {section_confidence.upper()}")
            
            if st.session_state.edit_mode:
                # Edit mode
                edited_key = f"edit_{i}"
                if edited_key not in st.session_state.edited_content:
                    st.session_state.edited_content[edited_key] = section_content
                
                new_content = st.text_area(
                    "Edit content:",
                    value=st.session_state.edited_content[edited_key],
                    height=200,
                    key=f"editor_{i}"
                )
                st.session_state.edited_content[edited_key] = new_content
                
                if new_content != section_content:
                    st.warning("⚠️ This section has been modified")
            else:
                # View mode - make sentences clickable
                sentences = section_content.split('. ')
                for j, sentence in enumerate(sentences):
                    if sentence.strip():
                        sentence_text = sentence + ('.' if not sentence.endswith('.') else '')
                        
                        # Make sentence clickable
                        if st.button(
                            sentence_text,
                            key=f"sent_{i}_{j}",
                            help="Click to see data sources for this statement"
                        ):
                            st.session_state.selected_sentence = sentence_text
                        
                        st.markdown("")  # Spacing
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("")  # Spacing between sections
        
        # Show selected sentence audit trail
        if st.session_state.selected_sentence and not st.session_state.edit_mode:
            st.markdown("---")
            st.markdown("### 🔍 Audit Trail for Selected Statement")
            
            # Find the sentence in audit trail
            matching_audit = [
                item for item in result['audit_trail'] 
                if item['sentence'] in st.session_state.selected_sentence 
                or st.session_state.selected_sentence in item['sentence']
            ]
            
            if matching_audit:
                audit_item = matching_audit[0]
                
                st.markdown(f'<div class="audit-trail-box">', unsafe_allow_html=True)
                st.markdown(f"**Statement:** {audit_item['sentence']}")
                st.markdown(f"**Section:** {audit_item['section']}")
                st.markdown(f"**Confidence:** {audit_item['confidence'].upper()}")
                
                st.markdown("**Data Sources:**")
                for source in audit_item['data_sources']:
                    st.markdown(f"- {source}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Complete Audit Trail")
        st.markdown("All statements with their data lineage and confidence levels")
        
        # Filter by confidence
        confidence_filter = st.multiselect(
            "Filter by Confidence Level",
            ["high", "medium", "low"],
            default=["high", "medium", "low"]
        )
        
        filtered_trail = [
            item for item in result['audit_trail']
            if item['confidence'] in confidence_filter
        ]
        
        st.markdown(f"**Showing {len(filtered_trail)} of {len(result['audit_trail'])} statements**")
        
        for i, item in enumerate(filtered_trail):
            with st.expander(f"{i+1}. {item['sentence'][:80]}..."):
                st.markdown(f"**Section:** {item['section']}")
                
                confidence_color = {
                    "high": "#28a745",
                    "medium": "#ffc107", 
                    "low": "#dc3545"
                }.get(item['confidence'], "#6c757d")
                
                st.markdown(
                    f"**Confidence:** <span style='color: {confidence_color}; font-weight: bold;'>{item['confidence'].upper()}</span>",
                    unsafe_allow_html=True
                )
                
                st.markdown("**Data Sources:**")
                for source in item['data_sources']:
                    st.markdown(f"- `{source}`")
    
    with tab3:
        st.markdown("### AI Reasoning Process")
        st.markdown("Step-by-step reasoning trace showing how the AI generated this narrative")
        
        if result.get('reasoning'):
            for i, step in enumerate(result['reasoning'], 1):
                st.markdown(f"**{i}.** {step}")
        else:
            st.info("Reasoning trace not available for template-generated narratives. Enable Claude API for full reasoning capture.")
    
    with tab4:
        st.markdown("### FinCEN SAR Compliance Checklist")
        
        checklist = result['compliance_checklist']
        
        col1, col2 = st.columns([3, 1])
        
        for requirement, status in checklist.items():
            with col1:
                st.markdown(f"**{requirement}**")
            with col2:
                if status:
                    st.markdown("✅ **Pass**")
                else:
                    st.markdown("❌ **Fail**")
        
        st.markdown("---")
        
        passed = sum(1 for v in checklist.values() if v)
        total = len(checklist)
        percentage = (passed / total) * 100
        
        st.progress(passed / total)
        st.markdown(f"**Overall Compliance Score:** {passed}/{total} ({percentage:.0f}%)")
        
        if percentage == 100:
            st.success("✅ All compliance requirements met! This SAR is ready for regulatory filing.")
        elif percentage >= 80:
            st.warning("⚠️ Most requirements met. Review flagged items before filing.")
        else:
            st.error("❌ Significant compliance gaps. This SAR requires additional work before filing.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>SAR Narrative Generator with Audit Trail</strong> | Built for Financial Crime Compliance</p>
    <p>🔒 All data processed securely | 📊 Full audit trail maintained | ✅ Regulatory-ready output</p>
</div>
""", unsafe_allow_html=True)
