"""
Enhanced Streamlit App for LangChain-based Multi-Agent AI Use Case Generation System
Updated with Streamlit 2025 best practices
"""
import streamlit as st
import json
import os
from datetime import datetime
from ai_proposal_system import SimpleLangChainSystem
from config.settings import settings

# Configure Streamlit page with 2025 best practices
st.set_page_config(
    page_title="AI Use Case Generator - LangChain",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# AI Use Case Generator\nPowered by LangChain Multi-Agent System"
    }
)

# Use st.cache_data for better performance (replaces deprecated @st.cache)
@st.cache_data(ttl=3600, show_spinner=False)
def initialize_system():
    """Initialize the system with caching for better performance"""
    try:
        system = SimpleLangChainSystem()
        return system, system.get_system_status()
    except Exception as e:
        return None, {"status": "error", "error": str(e)}

# Custom CSS with modern design principles
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
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .status-healthy {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }
    .status-warning {
        background: linear-gradient(90deg, #ffc107, #fd7e14);
        color: black;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }
    .status-error {
        background: linear-gradient(90deg, #dc3545, #e74c3c);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Enhanced main application with latest Streamlit features"""
    
    # Modern header with gradient
    st.markdown('<h1 class="main-header">🤖 AI Use Case Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Powered by LangChain Multi-Agent System</p>', unsafe_allow_html=True)

    # Initialize system
    system, status = initialize_system()
    
    # Sidebar with enhanced status display
    with st.sidebar:
        st.header("🔧 System Configuration")
        
        # Enhanced status display with new badge styling
        if status["status"] == "healthy":
            st.markdown('<div class="status-healthy">✅ System Status: Healthy</div>', unsafe_allow_html=True)
        elif status["status"] == "error":
            st.markdown('<div class="status-error">❌ System Status: Error</div>', unsafe_allow_html=True)
            st.error(f"Error: {status.get('error', 'Unknown error')}")
        else:
            st.markdown('<div class="status-warning">⚠️ System Status: Configuration Needed</div>', unsafe_allow_html=True)
            
        # Use new metric styling
        if system:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔧 Tools", f"{len(status.get('tools', []))}")
                st.metric("🤖 Agents", f"{len(status.get('agents', []))}")
            with col2:
                st.metric("🔑 API Keys", "✅" if status.get("api_keys_configured") else "❌")
                st.metric("🧠 Model", status.get('llm', 'Unknown'))
        
        # Add helpful links
        st.markdown("---")
        st.markdown("### 📚 Resources")
        st.markdown("- [OpenRouter API](https://openrouter.ai)")
        st.markdown("- [Serper API](https://serper.dev)")
        st.markdown("- [Kaggle API](https://www.kaggle.com/docs/api)")

    # Main content with flexible layout
    if not system:
        st.error("⚠️ System initialization failed. Please check your configuration.")
        st.markdown("### 🔧 Troubleshooting Steps:")
        st.markdown("1. Check that all API keys are configured in Streamlit secrets")
        st.markdown("2. Verify your OpenRouter API key is valid")
        st.markdown("3. Ensure Serper API key is configured")
        st.markdown("4. Check the logs for detailed error information")
        st.stop()

    # Input section with improved UX
    st.header("📝 Input Parameters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Enhanced input with validation
        company = st.text_input(
            "🏢 Company Name",
            value="Zoho",
            help="Enter the company name for AI use case generation",
            placeholder="e.g., Microsoft, Google, Tesla"
        )
        
        # Industry selector with search capability
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
        st.header("⚙️ Generation Options")
        
        # Advanced options in expander
        with st.expander("🔧 Advanced Settings", expanded=False):
            show_detailed = st.toggle(
                "Show Detailed Output",
                value=True,
                help="Display comprehensive research findings and analysis"
            )
            
            auto_download = st.toggle(
                "Auto-download Report",
                value=True,
                help="Automatically prepare download links for generated reports"
            )
            
            # Use new slider with better UX
            processing_timeout = st.slider(
                "Processing Timeout (minutes)",
                min_value=2,
                max_value=10,
                value=5,
                help="Maximum time to wait for proposal generation"
            )

    # Generation button with modern styling
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "🚀 Generate AI Use Case Proposal",
            type="primary",
            use_container_width=True,
            help="Click to start the multi-agent proposal generation process"
        )

    # Generation process with enhanced feedback
    if generate_button:
        if not company or not industry:
            st.error("⚠️ Please provide both company name and industry sector.")
            st.stop()

        # Modern progress tracking
        progress_container = st.container()
        
        with progress_container:
            # Use new progress bar with custom text
            progress_bar = st.progress(0, text="Initializing AI agents...")
            status_placeholder = st.empty()
            
            try:
                # Enhanced progress tracking
                steps = [
                    ("🔍 Research Agent: Market analysis", 25),
                    ("🎯 Use Case Agent: Generating AI scenarios", 50), 
                    ("📊 Resource Agent: Collecting datasets", 75),
                    ("📋 Proposal Agent: Creating final report", 90)
                ]
                
                for step_text, progress in steps:
                    progress_bar.progress(progress, text=step_text)
                    status_placeholder.info(f"Currently processing: {step_text}")
                
                # Generate proposal
                result = system.generate_proposal(company, industry)
                
                progress_bar.progress(100, text="✅ Generation completed!")
                status_placeholder.success("🎉 Proposal generated successfully!")
                
                # Enhanced results display
                if result["status"] == "success":
                    st.success("🎉 Proposal generated successfully!")
                    
                    # Results with modern tabs
                    st.header("📊 Generated Business Proposal")
                    
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📋 Executive Summary", 
                        "🔍 Research Insights", 
                        "🎯 Use Cases", 
                        "📁 Resources"
                    ])
                    
                    with tab1:
                        st.markdown("### Executive Summary")
                        st.markdown(result["result"])
                    
                    with tab2:
                        if show_detailed:
                            st.markdown("### Research Findings")
                            st.markdown(result.get("research_findings", "No research data available"))
                        else:
                            st.info("💡 Enable 'Show Detailed Output' to view research findings")
                    
                    with tab3:
                        if show_detailed:
                            st.markdown("### AI Use Cases")
                            st.markdown(result.get("use_cases", "No use cases available"))
                        else:
                            st.info("💡 Enable 'Show Detailed Output' to view detailed use cases")
                    
                    with tab4:
                        if show_detailed:
                            st.markdown("### Resources & Assets")
                            st.markdown(result.get("resources", "No resources available"))
                        else:
                            st.info("💡 Enable 'Show Detailed Output' to view resources")

                    # Enhanced download section
                    if auto_download:
                        st.markdown("---")
                        st.header("📥 Download Reports")
                        
                        # Prepare download data
                        download_data = {
                            "company": result["company"],
                            "industry": result["industry"],
                            "timestamp": result["timestamp"],
                            "proposal": result["result"],
                            "research_findings": result.get("research_findings", ""),
                            "use_cases": result.get("use_cases", ""),
                            "resources": result.get("resources", "")
                        }
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # JSON download with improved UX
                            json_data = json.dumps(download_data, indent=2, ensure_ascii=False)
                            st.download_button(
                                label="📄 Download Full Report (JSON)",
                                data=json_data,
                                file_name=f"{company}_{industry}_AI_Proposal_{result['timestamp']}.json",
                                mime="application/json",
                                help="Complete structured data in JSON format"
                            )
                        
                        with col2:
                            # Markdown download
                            st.download_button(
                                label="📝 Download Proposal (Markdown)",
                                data=result["result"],
                                file_name=f"{company}_{industry}_AI_Proposal_{result['timestamp']}.md",
                                mime="text/markdown",
                                help="Formatted proposal for documentation"
                            )

                        # Success metrics with enhanced display
                        st.markdown("---")
                        st.header("📊 Generation Summary")
                        
                        metrics_cols = st.columns(4)
                        with metrics_cols[0]:
                            st.metric("🏢 Company", result["company"])
                        with metrics_cols[1]:
                            st.metric("🏭 Industry", result["industry"])
                        with metrics_cols[2]:
                            st.metric("📅 Generated", result["timestamp"])
                        with metrics_cols[3]:
                            st.metric("✅ Status", "Success")

                else:
                    st.error(f"❌ Generation failed: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"🚨 System error: {str(e)}")
            finally:
                # Clean up progress indicators after a delay
                import time
                time.sleep(2)
                progress_container.empty()

    # Enhanced footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;">
        <p>🤖 Powered by LangChain Multi-Agent System | Built with Streamlit</p>
        <p>🔧 Uses OpenRouter API, Serper API, Kaggle API, and GitHub API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()