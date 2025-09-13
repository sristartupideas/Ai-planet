"""
Simple LangChain-based Multi-Agent AI Use Case Generation System

This system uses LangChain's core components for reliable multi-agent workflows
following the official LangChain documentation patterns.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from config.settings import settings
from tools.web_search_tool import WebSearchTool
from tools.kaggle_tool import KaggleTool
from tools.github_tool import GitHubTool
from utils.error_handling import (
    SystemError, APIError, ValidationError, ConfigurationError,
    handle_api_errors, validate_company_input, validate_industry_input,
    log_system_event, create_error_report, retry_on_failure,
    check_system_health, create_fallback_response
)

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

class SimpleLangChainSystem:
    """
    Simple LangChain-based Multi-Agent AI Use Case Generation System
    
    This system uses LangChain's core components for reliable multi-agent workflows
    with proper state management and context passing.
    """
    
    def __init__(self):
        """Initialize the Simple LangChain Multi-Agent System"""
        try:
            # Validate system health
            check_system_health()
            self._validate_api_connectivity()
            
            # Initialize LLM with enhanced error handling
            self.llm = self._initialize_llm()
            
            # Initialize tools
            self.web_search_tool = WebSearchTool()
            self.kaggle_tool = KaggleTool()
            self.github_tool = GitHubTool()
            
            # Create LangChain tools
            self.tools = [
                Tool(
                    name="web_search",
                    description="Search the web for information about companies, industries, and AI trends",
                    func=self.web_search_tool._run
                ),
                Tool(
                    name="kaggle_search",
                    description="Search Kaggle for relevant datasets",
                    func=self.kaggle_tool._run
                ),
                Tool(
                    name="github_search",
                    description="Search GitHub for relevant repositories",
                    func=self.github_tool._run
                )
            ]
            
            log_system_event("system_initialization", "Simple LangChain Multi-Agent AI System initialized successfully")
            logger.info("Simple LangChain Multi-Agent AI System initialized successfully")
            
        except Exception as e:
            error_report = create_error_report(e, {"context": "system_initialization"})
            logger.error(f"System initialization failed: {error_report}")
            raise SystemError(f"Failed to initialize system: {str(e)}")
    
    def _initialize_llm(self):
        """Initialize LLM with proper API key validation"""
        # Validate API key first
        if not settings.OPENROUTER_API_KEY:
            raise ConfigurationError("OPENROUTER_API_KEY is not configured. Please check your secrets or environment variables.")
        
        logger.info(f"Initializing LLM with model: {settings.LLM_MODEL}")
        logger.info(f"API Key configured: {'Yes' if settings.OPENROUTER_API_KEY else 'No'}")
        
        # Initialize LLM with provider routing for tool use
        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://ai-planet.streamlit.app",
                "X-Title": "AI Use Case Generator"
            }
        )
        
        return llm
    
    def _validate_api_connectivity(self) -> None:
        """Validate API connectivity before starting the workflow"""
        logger.info("Validating API connectivity...")
        
        # Test OpenRouter API
        try:
            if not settings.OPENROUTER_API_KEY:
                raise ConfigurationError("OPENROUTER_API_KEY is not configured")
            
            test_llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://ai-planet.streamlit.app",
                    "X-Title": "AI Use Case Generator"
                }
            )
            test_response = test_llm.invoke("Test connectivity")
            logger.info("✅ OpenRouter API connectivity verified")
        except Exception as e:
            logger.error(f"❌ OpenRouter API connectivity test failed: {str(e)}")
            raise ConfigurationError(f"OpenRouter API test failed: {str(e)}")
        
        # Test tools
        try:
            logger.info("✅ All tools initialized successfully")
        except Exception as e:
            logger.warning(f"Tool initialization failed: {str(e)}")
        
        logger.info("API connectivity validation completed")
    
    def _create_agent(self, system_prompt: str, agent_name: str) -> AgentExecutor:
        """Create a LangChain agent with the given system prompt"""
        
        # Create agent prompt template
        agent_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_tools_agent(self.llm, self.tools, agent_prompt)
        
        # Create agent executor with memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
        
        return agent_executor
    
    def _research_agent(self, company: str, industry: str) -> str:
        """Research Agent - conducts market research"""
        logger.info("🔍 Research Agent: Starting market research...")
        
        # Create research prompt
        research_prompt = f"""
        You are a Senior Market Research Analyst. Conduct comprehensive market research for {company} in the {industry} sector.
        
        COMPANY: {company}
        INDUSTRY: {industry}
        
        RESEARCH REQUIREMENTS:
        1. Use the web_search tool to find recent reports and industry analyses
        2. Focus on authoritative sources: McKinsey, Deloitte, PwC, BCG, company reports
        3. Search for specific queries like:
           - "{industry} AI adoption trends 2025"
           - "{company} annual report AI strategy"
           - "{industry} market research McKinsey Deloitte"
           - "{company} competitive analysis technology sector"
        
        OUTPUT FORMAT:
        Provide a comprehensive research report with:
        - Executive Summary (2-3 paragraphs)
        - Industry analysis and trends
        - Competitive landscape
        - Market opportunities
        - Strategic recommendations
        
        Include specific data points, statistics, and quantitative insights with source citations.
        """
        
        # Create and execute agent
        agent = self._create_agent(research_prompt, "Research Agent")
        
        result = agent.invoke({
            "input": f"Conduct comprehensive market research for {company} in {industry}. Use the web_search tool to find authoritative sources and recent reports."
        })
        
        logger.info("✅ Research Agent: Market research completed")
        return result["output"]
    
    def _use_case_agent(self, company: str, industry: str, research_findings: str) -> str:
        """Use Case Agent - generates 15-20 detailed AI use cases"""
        logger.info("🎯 Use Case Agent: Generating AI use cases...")
        
        # Create use case prompt
        use_case_prompt = f"""
        You are an AI/ML Industry Specialist and Use Case Strategist. Generate EXACTLY 15-20 detailed AI use cases for {company} in the {industry} sector.
        
        COMPANY: {company}
        INDUSTRY: {industry}
        
        RESEARCH FINDINGS:
        {research_findings}
        
        CRITICAL REQUIREMENTS:
        - Generate EXACTLY 15-20 detailed AI use cases
        - Organize by AI technology categories:
          * Generative AI & LLMs (4-5 use cases)
          * Computer Vision (4-5 use cases)
          * Predictive Analytics & ML (4-5 use cases)
          * Natural Language Processing (2-3 use cases)
          * Automation & Optimization (2-3 use cases)
        
        Each use case MUST include:
        - Description
        - ROI estimate
        - Implementation complexity
        - Cross-functional impact
        - Business value
        
        Use the web_search tool to find current AI use cases and industry benchmarks.
        """
        
        # Create and execute agent
        agent = self._create_agent(use_case_prompt, "Use Case Agent")
        
        result = agent.invoke({
            "input": f"Generate 15-20 detailed AI use cases for {company} in {industry} based on the research findings. Use the web_search tool to find current AI use cases and industry benchmarks."
        })
        
        logger.info("✅ Use Case Agent: AI use cases generated")
        return result["output"]
    
    def _resource_agent(self, company: str, industry: str, research_findings: str, use_cases: str) -> str:
        """Resource Agent - collects datasets and repositories"""
        logger.info("📚 Resource Agent: Collecting resources...")
        
        # Create resource prompt
        resource_prompt = f"""
        You are an AI/ML Resource Collection Specialist. Collect relevant datasets and GitHub repositories for {company} in the {industry} sector.
        
        COMPANY: {company}
        INDUSTRY: {industry}
        
        RESEARCH FINDINGS:
        {research_findings}
        
        USE CASES:
        {use_cases}
        
        REQUIREMENTS:
        1. Use kaggle_search tool to find relevant datasets
        2. Use github_search tool to find relevant repositories
        3. Focus on {industry}-specific and {company}-relevant resources
        4. Include at least 3-5 Kaggle datasets with clickable links
        5. Include at least 3-5 GitHub repositories with clickable links
        6. Provide quality assessments for each resource
        
        OUTPUT FORMAT:
        - Executive Summary
        - Datasets with direct links and quality assessments
        - GitHub repositories with direct links and quality assessments
        - Implementation recommendations
        """
        
        # Create and execute agent
        agent = self._create_agent(resource_prompt, "Resource Agent")
        
        result = agent.invoke({
            "input": f"Collect relevant datasets and repositories for {company} in {industry}. Use the kaggle_search and github_search tools to find resources."
        })
        
        logger.info("✅ Resource Agent: Resources collected")
        return result["output"]
    
    def _proposal_agent(self, company: str, industry: str, research_findings: str, use_cases: str, resources: str) -> str:
        """Proposal Agent - creates final business proposal"""
        logger.info("📝 Proposal Agent: Creating final proposal...")
        
        # Create proposal prompt
        proposal_prompt = f"""
        You are a Senior Business Strategy Consultant and Proposal Writer. Create a comprehensive business proposal for {company} in the {industry} sector.
        
        COMPANY: {company}
        INDUSTRY: {industry}
        
        RESEARCH FINDINGS:
        {research_findings}
        
        USE CASES:
        {use_cases}
        
        RESOURCES:
        {resources}
        
        PROPOSAL REQUIREMENTS:
        1. Executive Summary
        2. Business Case
        3. AI Use Cases (MANDATORY: Include the complete use case analysis from above)
        4. Implementation Roadmap
        5. Budget and ROI
        6. Resource Assets & Implementation Support (MANDATORY: Include clickable links)
        7. Risk Management
        8. Next Steps
        
        CRITICAL: Section 3 (AI Use Cases) MUST include the complete 15-20 detailed use cases from above.
        CRITICAL: Include all clickable links to datasets and repositories.
        """
        
        # Create and execute agent
        agent = self._create_agent(proposal_prompt, "Proposal Agent")
        
        result = agent.invoke({
            "input": f"Create a comprehensive business proposal for {company} in {industry} incorporating all research, use cases, and resources."
        })
        
        logger.info("✅ Proposal Agent: Final proposal created")
        return result["output"]
    
    def generate_proposal(self, company: str, industry: str) -> Dict[str, Any]:
        """
        Generate a comprehensive AI use case proposal
        
        Args:
            company: Company name
            industry: Industry sector
            
        Returns:
            Dictionary containing the proposal results
        """
        try:
            validate_company_input(company)
            validate_industry_input(industry)
            
            log_system_event("proposal_generation_started", f"Starting proposal generation for {company} in {industry}")
            logger.info(f"Starting proposal generation for {company} in {industry}")
            
            # Execute workflow sequentially
            logger.info("Executing LangChain multi-agent workflow...")
            
            # Step 1: Research
            research_findings = self._research_agent(company, industry)
            
            # Step 2: Use Cases
            use_cases = self._use_case_agent(company, industry, research_findings)
            
            # Step 3: Resources
            resources = self._resource_agent(company, industry, research_findings, use_cases)
            
            # Step 4: Final Proposal
            final_proposal = self._proposal_agent(company, industry, research_findings, use_cases, resources)
            
            # Validate output
            self._validate_proposal_output(final_proposal, company, industry)
            
            # Save output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(settings.REPORTS_DIR, f"{company}_{industry}_{timestamp}.json")
            
            output_data = {
                "company": company,
                "industry": industry,
                "timestamp": timestamp,
                "result": final_proposal,
                "research_findings": research_findings,
                "use_cases": use_cases,
                "resources": resources,
                "status": "success"
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            log_system_event("proposal_generation_completed", f"Proposal generated successfully for {company}")
            logger.info(f"Proposal generated successfully for {company}")
            
            return {
                "status": "success",
                "company": company,
                "industry": industry,
                "result": final_proposal,
                "research_findings": research_findings,
                "use_cases": use_cases,
                "resources": resources,
                "output_file": output_file,
                "timestamp": timestamp
            }
            
        except ValidationError as e:
            error_report = create_error_report(e, {"company": company, "industry": industry})
            logger.error(f"Validation error: {error_report}")
            return {
                "status": "error",
                "error_type": "validation",
                "message": str(e),
                "company": company,
                "industry": industry
            }
        except APIError as e:
            error_report = create_error_report(e, {"company": company, "industry": industry})
            logger.error(f"API error: {error_report}")
            return {
                "status": "error",
                "error_type": "api",
                "message": str(e),
                "company": company,
                "industry": industry
            }
        except Exception as e:
            error_report = create_error_report(e, {"company": company, "industry": industry})
            logger.error(f"Unexpected error generating proposal for {company}: {error_report}")
            return {
                "status": "error",
                "error_type": "unexpected",
                "message": str(e),
                "company": company,
                "industry": industry
            }
    
    def _validate_proposal_output(self, result: str, company: str, industry: str) -> None:
        """Validate that the proposal output contains all required elements"""
        result_str = str(result).lower()
        
        # Check for required elements
        required_elements = {
            "executive summary": "executive summary" in result_str,
            "ai use cases": "use case" in result_str or "ai" in result_str,
            "budget": "budget" in result_str or "cost" in result_str or "investment" in result_str,
            "roi": "roi" in result_str or "return on investment" in result_str,
            "implementation": "implementation" in result_str or "roadmap" in result_str,
            "risk": "risk" in result_str,
            "company name": company.lower() in result_str,
            "industry": industry.lower() in result_str
        }
        
        # Check for sufficient use cases
        use_case_count = result_str.count("use case") + result_str.count("1.") + result_str.count("2.") + result_str.count("3.")
        has_sufficient_use_cases = use_case_count >= 15
        
        # Check for resource links
        has_kaggle_links = "kaggle.com" in result_str
        has_github_links = "github.com" in result_str
        has_http_links = "http" in result_str
        
        missing_elements = [element for element, present in required_elements.items() if not present]
        
        if missing_elements:
            logger.warning(f"Proposal missing required elements: {missing_elements}")
        
        if has_sufficient_use_cases:
            logger.info(f"✅ Proposal contains sufficient use cases ({use_case_count} found)")
        else:
            logger.warning(f"⚠️ Proposal has insufficient use cases ({use_case_count} found, need at least 15)")
        
        if has_kaggle_links or has_github_links:
            logger.info("✅ Proposal contains clickable resource links")
        else:
            logger.warning("⚠️ Proposal missing clickable resource links")
    
    def get_system_status(self):
        """Get system status"""
        api_key_status = settings.validate_api_keys()
        return {
            "agents": [
                "Research Agent",
                "Use Case Agent", 
                "Resource Agent",
                "Proposal Agent"
            ],
            "tools": [
                "Web Search Tool",
                "Kaggle Tool",
                "GitHub Tool"
            ],
            "api_keys_configured": api_key_status["valid"],
            "llm": settings.LLM_MODEL,
            "status": "healthy" if api_key_status["valid"] else "configuration_needed"
        }

def main():
    """Main function for testing the Simple LangChain system"""
    try:
        system = SimpleLangChainSystem()
        company = "Zoho"
        industry = "Technology"
        
        print(f"🚀 Starting Simple LangChain Multi-Agent AI System for {company} in {industry}")
        print("=" * 60)
        
        result = system.generate_proposal(company, industry)
        
        if result["status"] == "success":
            print("✅ Proposal generated successfully!")
            print(f"📄 Output saved to: {result['output_file']}")
            print(f"📊 Result: {result['result'][:200]}...")
        else:
            print(f"❌ Error: {result['message']}")
            
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        print(f"❌ System failed: {str(e)}")

if __name__ == "__main__":
    main()
