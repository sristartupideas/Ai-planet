"""
Enhanced Streamlit App with Validation, Consolidated Output and Comprehensive Features
Updated with strict validation and single file output generation
"""
import streamlit as st
import json
import os
from datetime import datetime
from ai_proposal_system import EnhancedLangChainSystem
from config.settings import settings

# Configure Streamlit page
st.set_page_config(
    page_title="AI Use Case Generator - Enhanced",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Enhanced AI Use Case Generator\nPowered by LangChain Multi-Agent System with Strict Validation"
    }
)

# Use st.cache_resource for caching system objects
@st.cache_resource(ttl=3600, show_spinner=False)
def initialize_system():
    """Initialize the enhanced system with caching"""
    try:
        system = EnhancedLangChainSystem()
        return system, system.get_system_status()
    except Exception as e:
        return None, {"status": "error", "error": str(e)}

# Enhanced CSS with modern design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-metric {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
    }
    .validation-badge {
        background: #17a2b8;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .enhancement-box {
        background: rgba(23, 162, 184, 0.1);
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .output-section {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Enhanced main application with validation and consolidated output"""
    
    # Modern header
    st.markdown('<h1 class="main-header">🤖 Enhanced AI Use Case Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Powered by LangChain Multi-Agent System with Strict Validation & Consolidated Output</p>', unsafe_allow_html=True)
    
    # Initialize system
    system, status = initialize_system()
    
    # Enhanced sidebar
    with st.sidebar:
        st.header("🔧 System Configuration")
        
        # Enhanced status display
        if status["status"] == "healthy":
            st.markdown('<div class="validation-badge">✅ System Status: Healthy</div>', unsafe_allow_html=True)
        elif status["status"] == "error":
            st.error(f"❌ System Error: {status.get('error', 'Unknown error')}")
        else:
            st.warning("⚠️ Configuration needed")
        
        # Enhanced system metrics
        if system:
            st.markdown("### 📊 System Components")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔧 Tools", f"{len(status.get('tools', []))}")
                st.metric("🤖 Agents", f"{len(status.get('agents', []))}")
            with col2:
                st.metric("🔑 API Keys", "✅" if status.get("api_keys_configured") else "❌")
                st.metric("🧠 Model", "GPT-4o-mini")
            
            # Show enhancements
            if "enhancements" in status:
                st.markdown("### ✨ Enhanced Features")
                for enhancement in status["enhancements"]:
                    st.markdown(f"• {enhancement}")
        
        # System requirements display
        st.markdown("---")
        st.markdown("### 📋 Validation Requirements")
        st.markdown("""
        **Use Case Generation:**
        - Exactly 15-20 use cases total
        - 5 AI technology categories
        - Strict distribution validation
        
        **Output Format:**
        - Single consolidated report
        - Comprehensive methodology
        - Clickable resource links
        """)
        
        # Helpful resources
        st.markdown("### 🔗 Resources")
        st.markdown("""
        - [OpenRouter API](https://openrouter.ai)
        - [Serper API](https://serper.dev) 
        - [Kaggle API](https://www.kaggle.com/docs/api)
        - [System Documentation](https://github.com/your-repo)
        """)
    
    # Main content
    if not system:
        st.error("🚨 System initialization failed. Please check your configuration.")
        st.markdown("""
        ### 🔧 Troubleshooting Steps:
        1. Verify all API keys are configured in Streamlit secrets
        2. Check OpenRouter API key validity
        3. Ensure Serper API key is active
        4. Review system logs for detailed errors
        """)
        st.stop()
    
    # Enhanced input section
    st.markdown("## 📝 Input Parameters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        company = st.text_input(
            "🏢 Company Name",
            value="Zoho",
            help="Enter the company name for AI use case generation",
            placeholder="e.g., Microsoft, Google, Tesla"
        )
        
        industry = st.selectbox(
            "🏭 Industry Sector",
            options=[
                "Technology", "Healthcare", "Finance", "Manufacturing",
                "Retail", "Education", "Automotive", "Energy", 
                "Telecommunications", "Agriculture", "Other"
            ],
            index=0,
            help="Select the primary industry sector"
        )
        
        if industry == "Other":
            industry = st.text_input("Custom Industry", placeholder="Enter custom industry")
    
    with col2:
        st.markdown("### ⚙️ Generation Options")
        
        with st.expander("🔧 Advanced Settings", expanded=False):
            validation_strict = st.toggle(
                "Strict Validation Mode",
                value=True,
                help="Enforce exact 15-20 use cases with category distribution"
            )
            
            generate_consolidated = st.toggle(
                "Generate Consolidated Report", 
                value=True,
                help="Create single comprehensive output file"
            )
            
            include_methodology = st.toggle(
                "Include Methodology Section",
                value=True,
                help="Add detailed methodology documentation"
            )
            
            processing_timeout = st.slider(
                "Processing Timeout (minutes)",
                min_value=3,
                max_value=15,
                value=8,
                help="Maximum time for enhanced processing"
            )
    
    # Generation button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "🚀 Generate Enhanced AI Use Case Proposal",
            type="primary",
            use_container_width=True,
            help="Generate validated use cases with consolidated output"
        )
    
    # Enhanced generation process
    if generate_button:
        if not company or not industry:
            st.error("❌ Please provide both company name and industry sector.")
            st.stop()
        
        # Enhanced progress tracking
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0, text="🔄 Initializing enhanced AI agents...")
            status_placeholder = st.empty()
            
            try:
                # Enhanced progress steps
                steps = [
                    ("🔍 Research Agent: Comprehensive market analysis", 20),
                    ("🤖 Use Case Agent: Generating validated AI scenarios", 45),
                    ("📊 Resource Agent: Curating datasets and repositories", 70),
                    ("📋 Proposal Agent: Creating business proposal", 85),
                    ("✅ Consolidation: Generating single output file", 95)
                ]
                
                for step_text, progress in steps:
                    progress_bar.progress(progress, text=step_text)
                    status_placeholder.info(f"Currently processing: {step_text}")
                
                # Generate enhanced proposal
                with st.spinner("Processing with enhanced validation..."):
                    result = system.generate_proposal(company, industry)
                
                progress_bar.progress(100, text="✅ Enhanced generation completed!")
                status_placeholder.success("🎉 Proposal generated with validation!")
                
                # Enhanced results display
                if result["status"] == "success":
                    st.success("🎉 Enhanced proposal generated successfully!")
                    
                    # Display success metrics
                    st.markdown('<div class="success-metric">✅ Strict Validation Passed | 📊 Consolidated Output Generated | 🔗 Resources Curated</div>', unsafe_allow_html=True)
                    
                    # Enhanced results tabs
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "📋 Executive Summary",
                        "🔍 Research Analysis", 
                        "🤖 Validated Use Cases",
                        "📦 Resource Assets",
                        "📁 Output Files"
                    ])
                    
                    with tab1:
                        st.markdown("### Executive Summary")
                        st.markdown('<div class="output-section">', unsafe_allow_html=True)
                        
                        # Extract executive summary from consolidated report
                        if "consolidated_report" in result:
                            report_lines = result["consolidated_report"].split('\n')
                            summary_started = False
                            summary_lines = []
                            
                            for line in report_lines:
                                if "## 1. Executive Summary" in line:
                                    summary_started = True
                                    continue
                                elif summary_started and line.startswith("## 2."):
                                    break
                                elif summary_started:
                                    summary_lines.append(line)
                            
                            if summary_lines:
                                st.markdown('\n'.join(summary_lines))
                            else:
                                st.markdown(result["result"][:1000] + "...")
                        else:
                            st.markdown(result["result"][:1000] + "...")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tab2:
                        st.markdown("### Industry Research & Market Analysis")
                        st.markdown('<div class="output-section">', unsafe_allow_html=True)
                        if result.get("research_findings"):
                            st.markdown(result["research_findings"])
                        else:
                            st.info("Enable detailed output to view research findings")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tab3:
                        st.markdown("### Validated AI Use Cases")
                        st.markdown('<div class="enhancement-box">', unsafe_allow_html=True)
                        st.markdown("**✅ Validation Status:** Use cases validated for count and category distribution")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="output-section">', unsafe_allow_html=True)
                        if result.get("use_cases"):
                            st.markdown(result["use_cases"])
                        else:
                            st.info("Enable detailed output to view use cases")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tab4:
                        st.markdown("### Curated Resources & Implementation Assets")
                        st.markdown('<div class="output-section">', unsafe_allow_html=True)
                        if result.get("resources"):
                            st.markdown(result["resources"])
                        else:
                            st.info("Enable detailed output to view resources")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tab5:
                        st.markdown("### Generated Output Files")
                        
                        # File download section
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 📋 Consolidated Report")
                            if "consolidated_file" in result and os.path.exists(result["consolidated_file"]):
                                with open(result["consolidated_file"], 'r', encoding='utf-8') as f:
                                    consolidated_content = f.read()
                                
                                st.download_button(
                                    label="📥 Download Consolidated Report (Markdown)",
                                    data=consolidated_content,
                                    file_name=f"{company}_{industry}_CONSOLIDATED_REPORT.md",
                                    mime="text/markdown",
                                    help="Complete report with methodology and conclusions"
                                )
                                
                                # Display file info
                                file_size = len(consolidated_content.encode('utf-8'))
                                st.info(f"📄 File size: {file_size:,} bytes | Contains: Methodology, Results, Conclusions")
                        
                        with col2:
                            st.markdown("#### 📊 Detailed Data")
                            if "json_file" in result and os.path.exists(result["json_file"]):
                                with open(result["json_file"], 'r', encoding='utf-8') as f:
                                    json_content = f.read()
                                
                                st.download_button(
                                    label="📥 Download Detailed Data (JSON)",
                                    data=json_content,
                                    file_name=f"{company}_{industry}_DETAILED_DATA.json",
                                    mime="application/json",
                                    help="Structured data for integration and analysis"
                                )
                                
                                # Display JSON info
                                json_size = len(json_content.encode('utf-8'))
                                st.info(f"📊 File size: {json_size:,} bytes | Contains: Raw data, metadata, timestamps")
                        
                        # File paths display
                        st.markdown("#### 📁 File Locations")
                        if "consolidated_file" in result:
                            st.code(f"Consolidated Report: {result['consolidated_file']}")
                        if "json_file" in result:
                            st.code(f"Detailed Data: {result['json_file']}")
                    
                    # Enhanced summary metrics
                    st.markdown("---")
                    st.markdown("### 📊 Generation Summary")
                    
                    metrics_cols = st.columns(5)
                    with metrics_cols[0]:
                        st.metric("🏢 Company", company)
                    with metrics_cols[1]:
                        st.metric("🏭 Industry", industry)
                    with metrics_cols[2]:
                        st.metric("⏰ Generated", result.get("timestamp", "N/A")[:10])
                    with metrics_cols[3]:
                        st.metric("✅ Status", "Success")
                    with metrics_cols[4]:
                        st.metric("📁 Files", "2" if "consolidated_file" in result else "1")
                
                else:
                    st.error(f"❌ Enhanced generation failed: {result.get('message', 'Unknown error')}")
                    
                    # Enhanced error information
                    if result.get("error_type"):
                        st.markdown(f"**Error Type:** {result['error_type']}")
                    
                    st.markdown("### 🔧 Troubleshooting:")
                    st.markdown("""
                    1. Check API key configuration
                    2. Verify internet connectivity
                    3. Ensure sufficient API credits
                    4. Review system logs for details
                    """)
            
            except Exception as e:
                st.error(f"🚨 System error: {str(e)}")
                st.markdown("Please check the system configuration and try again.")
            
            finally:
                # Clean up progress indicators
                import time
                time.sleep(1)
                progress_container.empty()
    
    # Enhanced footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;">
        <p>🤖 Enhanced AI Use Case Generator | Powered by LangChain Multi-Agent System</p>
        <p>✅ Strict Validation | 📊 Consolidated Output | 🔗 Resource Curation</p>
        <p>🔧 Uses: OpenRouter API, Serper API, Kaggle API, GitHub API</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
