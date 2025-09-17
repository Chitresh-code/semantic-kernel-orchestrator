from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from semantic_kernel.functions import kernel_function


class DocumentGeneratorTools:
    """Mock document generation tools for demonstration. Replace with actual document services."""

    def __init__(self):
        # Document templates
        self.templates = {
            "sales_proposal": {
                "sections": [
                    "Executive Summary",
                    "Customer Requirements",
                    "Proposed Solution",
                    "Implementation Timeline",
                    "Investment Summary",
                    "Next Steps"
                ],
                "format": "professional"
            },
            "quote": {
                "sections": [
                    "Quote Summary",
                    "Product Details",
                    "Pricing Breakdown",
                    "Terms and Conditions"
                ],
                "format": "standard"
            },
            "contract": {
                "sections": [
                    "Agreement Overview",
                    "Scope of Services",
                    "Deliverables",
                    "Payment Terms",
                    "Legal Terms",
                    "Signatures"
                ],
                "format": "legal"
            },
            "implementation_plan": {
                "sections": [
                    "Project Overview",
                    "Implementation Phases",
                    "Timeline and Milestones",
                    "Resource Requirements",
                    "Risk Mitigation",
                    "Success Criteria"
                ],
                "format": "technical"
            }
        }

        # Sample content generators
        self.content_generators = {
            "executive_summary": self._generate_executive_summary,
            "customer_requirements": self._generate_customer_requirements,
            "proposed_solution": self._generate_proposed_solution,
            "implementation_timeline": self._generate_implementation_timeline,
            "investment_summary": self._generate_investment_summary,
            "next_steps": self._generate_next_steps
        }

    @kernel_function(
        description="""Generate a comprehensive sales proposal document with multiple sections.

        Input Parameters:
        - customer_info (str): JSON object with customer details including:
          * name: Company name
          * contact_person: Primary contact name
          * industry: Industry sector
          * company_size: Size category
          * Any other relevant customer information
        - products (str): JSON object with product/quote information including:
          * items: Array of products with pricing and features
          * final_total: Total cost
          * Other pricing details
        - requirements (str): Optional JSON object with specific customer requirements array (default: None)

        Output:
        - JSON string containing complete proposal document:
          * document_id: Unique proposal identifier
          * document_type: 'Sales Proposal'
          * created_date: Document creation date
          * customer: Customer information
          * sections: Object with generated content for each section:
            - executive_summary: Overview and value proposition
            - customer_requirements: Documented needs and challenges
            - proposed_solution: Detailed solution description
            - implementation_timeline: Project phases and timeline
            - investment_summary: Cost breakdown and ROI
            - next_steps: Action items and process

        Example: generate_proposal('{"name":"Acme Corp","industry":"Manufacturing"}', '{"items":[...],"final_total":75000}', '{"requirements":["automation","scalability"]}') creates full business proposal""",
        name="generate_proposal"
    )
    def generate_proposal(self, customer_info: str, products: str, requirements: str = None) -> str:
        """Generate a comprehensive sales proposal."""
        try:
            customer_data = json.loads(customer_info)
            product_data = json.loads(products)
            requirement_data = json.loads(requirements) if requirements else {}

            proposal = {
                "document_id": f"PROP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "document_type": "Sales Proposal",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "customer": customer_data,
                "sections": {}
            }

            # Generate each section
            proposal["sections"]["executive_summary"] = self._generate_executive_summary(customer_data, product_data)
            proposal["sections"]["customer_requirements"] = self._generate_customer_requirements(requirement_data)
            proposal["sections"]["proposed_solution"] = self._generate_proposed_solution(product_data)
            proposal["sections"]["implementation_timeline"] = self._generate_implementation_timeline(product_data)
            proposal["sections"]["investment_summary"] = self._generate_investment_summary(product_data)
            proposal["sections"]["next_steps"] = self._generate_next_steps()

            return json.dumps(proposal, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid input format: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Error generating proposal: {e}"})

    @kernel_function(
        description="""Generate a formal, professional quote document from pricing data.

        Input Parameters:
        - quote_data (str): JSON object containing quote information including:
          * quote_id: Unique quote identifier
          * items: Array of line items with products, pricing, features
          * final_total: Total quote amount
          * valid_until: Quote expiration date
          * Other pricing breakdown details
        - customer_info (str): JSON object with customer details including:
          * name: Company name
          * contact_person: Primary contact
          * email: Contact email address
          * Any other relevant customer information

        Output:
        - JSON string containing formatted quote document:
          * document_id: Document identifier based on quote ID
          * document_type: 'Price Quote'
          * created_date and valid_until: Document dates
          * customer: Customer information
          * quote_details: Complete quote data
          * formatted_content: Professional formatting with:
            - header: Document title with customer name
            - quote_summary: Key quote details and total
            - product_details: Formatted product line items
            - terms_and_conditions: Standard quote terms

        Example: generate_quote_document('{"quote_id":"Q20241220","items":[...],"final_total":50000}', '{"name":"TechStart Inc","contact_person":"Jane Doe"}') creates professional quote document""",
        name="generate_quote_document"
    )
    def generate_quote_document(self, quote_data: str, customer_info: str) -> str:
        """Generate a formatted quote document."""
        try:
            quote = json.loads(quote_data)
            customer = json.loads(customer_info)

            document = {
                "document_id": f"QUOTE_{quote.get('quote_id', 'UNKNOWN')}",
                "document_type": "Price Quote",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "valid_until": quote.get("valid_until"),
                "customer": customer,
                "quote_details": quote,
                "formatted_content": {
                    "header": f"Price Quote for {customer.get('name', 'Customer')}",
                    "quote_summary": f"Quote ID: {quote.get('quote_id')}\nValid Until: {quote.get('valid_until')}\nTotal Amount: ${quote.get('final_total', 0):,.2f}",
                    "product_details": self._format_quote_items(quote.get("items", [])),
                    "terms_and_conditions": self._generate_terms_and_conditions()
                }
            }

            return json.dumps(document, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid input format: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Error generating quote document: {e}"})

    @kernel_function(
        description="""Generate a detailed project implementation plan with phases, timelines, and resource requirements.

        Input Parameters:
        - project_info (str): JSON object with project details including:
          * project_name: Name of the implementation project
          * customer: Customer information
          * products: Products/services being implemented
          * scope: Project scope and objectives
          * Any other relevant project details
        - timeline_weeks (int): Total project duration in weeks (default: 12)

        Output:
        - JSON string containing comprehensive implementation plan:
          * document_id: Unique plan identifier
          * document_type: 'Implementation Plan'
          * created_date: Document creation date
          * project: Project information
          * timeline_weeks: Total project duration
          * phases: Array of implementation phases with:
            - phase: Phase name
            - duration_weeks: Phase duration
            - activities: Key activities in this phase
            - deliverables: Expected outputs
          * resources: Required client and vendor resources
          * risks: Risk assessment with mitigation strategies
          * success_criteria: Measurable success indicators

        Example: generate_implementation_plan('{"project_name":"ERP Implementation","customer":"Acme Corp","scope":"Full system deployment"}', 16) creates 16-week implementation roadmap""",
        name="generate_implementation_plan"
    )
    def generate_implementation_plan(self, project_info: str, timeline_weeks: int = 12) -> str:
        """Generate a detailed implementation plan."""
        try:
            project_data = json.loads(project_info)

            plan = {
                "document_id": f"IMPL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "document_type": "Implementation Plan",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "project": project_data,
                "timeline_weeks": timeline_weeks,
                "phases": self._generate_implementation_phases(project_data, timeline_weeks),
                "resources": self._generate_resource_requirements(project_data),
                "risks": self._generate_risk_assessment(),
                "success_criteria": self._generate_success_criteria()
            }

            return json.dumps(plan, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid input format: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Error generating implementation plan: {e}"})

    @kernel_function(
        description="""Generate a professional service agreement contract template.

        Input Parameters:
        - agreement_details (str): JSON object with contract specifics including:
          * services: Array of services being provided
          * duration: Contract duration
          * payment_terms: Payment schedule and terms
          * deliverables: Expected outcomes and deliverables
          * total_value: Contract total value
          * Any other agreement-specific details
        - customer_info (str): JSON object with customer details including:
          * name: Company name
          * contact_person: Authorized signatory
          * address: Company address
          * email: Contact email
          * Any other relevant customer information

        Output:
        - JSON string containing complete contract template:
          * document_id: Unique contract identifier
          * document_type: 'Service Agreement'
          * created_date: Contract creation date
          * parties: Both client and provider information
          * agreement_details: Contract specifics
          * sections: Legal contract sections:
            - scope_of_services: Detailed service descriptions
            - deliverables: Expected outputs and timelines
            - payment_terms: Payment schedule and conditions
            - legal_terms: Standard legal clauses
            - signature_blocks: Signature areas for both parties

        Example: generate_contract('{"services":["Implementation","Training"],"duration":"6 months","total_value":100000}', '{"name":"Acme Corp","contact_person":"John Smith","address":"123 Main St"}') creates professional service contract""",
        name="generate_contract"
    )
    def generate_contract(self, agreement_details: str, customer_info: str) -> str:
        """Generate a contract template."""
        try:
            agreement = json.loads(agreement_details)
            customer = json.loads(customer_info)

            contract = {
                "document_id": f"CONTRACT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "document_type": "Service Agreement",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "parties": {
                    "client": customer,
                    "provider": {
                        "name": "Your Company Name",
                        "address": "Company Address",
                        "contact": "legal@company.com"
                    }
                },
                "agreement_details": agreement,
                "sections": {
                    "scope_of_services": self._generate_scope_of_services(agreement),
                    "deliverables": self._generate_deliverables(agreement),
                    "payment_terms": self._generate_payment_terms(agreement),
                    "legal_terms": self._generate_legal_terms(),
                    "signature_blocks": self._generate_signature_blocks()
                }
            }

            return json.dumps(contract, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid input format: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Error generating contract: {e}"})

    @kernel_function(
        description="""Generate a custom document using predefined templates with flexible content.

        Input Parameters:
        - template_name (str): Template to use from available options:
          * 'sales_proposal': Professional sales proposal with 6 sections
          * 'quote': Price quote with product details and terms
          * 'contract': Service agreement with legal terms
          * 'implementation_plan': Project plan with phases and timelines
        - content_data (str): JSON object with data specific to the chosen template
        - options (str): Optional JSON object with document formatting options (default: None)

        Output:
        - JSON string containing custom document:
          * document_id: Unique document identifier
          * document_type: Formatted template name
          * created_date: Document creation date
          * template: Template name used
          * format: Template format style ('professional', 'standard', 'legal', 'technical')
          * options: Any formatting options applied
          * content: Input data used for generation
          * sections: Generated content for each template section
        - Content generated based on template structure and provided data
        - Error message if template not found

        Example: generate_custom_document('sales_proposal', '{"customer":"Acme Corp","products":["Software"]}', '{"format":"executive"}') creates custom proposal using executive formatting""",
        name="generate_custom_document"
    )
    def generate_custom_document(self, template_name: str, content_data: str, options: str = None) -> str:
        """Generate a custom document using specified template."""
        try:
            data = json.loads(content_data)
            doc_options = json.loads(options) if options else {}

            if template_name not in self.templates:
                return json.dumps({"error": f"Template '{template_name}' not found"})

            template = self.templates[template_name]

            document = {
                "document_id": f"DOC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "document_type": template_name.replace("_", " ").title(),
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "template": template_name,
                "format": template["format"],
                "options": doc_options,
                "content": data,
                "sections": {}
            }

            # Generate content for each section
            for section in template["sections"]:
                section_key = section.lower().replace(" ", "_")
                if section_key in self.content_generators:
                    document["sections"][section_key] = self.content_generators[section_key](data)
                else:
                    document["sections"][section_key] = f"Content for {section} section would be generated here based on provided data."

            return json.dumps(document, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid input format: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Error generating custom document: {e}"})

    # Helper methods for content generation
    def _generate_executive_summary(self, customer_data: dict, product_data: dict) -> str:
        """Generate executive summary content."""
        company_name = customer_data.get("name", "Customer")
        industry = customer_data.get("industry", "business")

        summary = f"""
This proposal outlines a comprehensive solution designed specifically for {company_name}'s {industry} operations.

Our recommended solution addresses your key business challenges while providing:
- Streamlined operations and improved efficiency
- Scalable technology platform for future growth
- Measurable ROI within 12-18 months
- Industry-leading support and implementation services

The total investment for this solution is ${sum(item.get('line_total', 0) for item in product_data.get('items', [])):,.2f}, with implementation beginning within 4-6 weeks of contract execution.
"""
        return summary.strip()

    def _generate_customer_requirements(self, requirement_data: dict) -> str:
        """Generate customer requirements section."""
        if not requirement_data:
            return "Customer requirements will be detailed based on discovery sessions and needs assessment."

        requirements = ["Based on our analysis, your key requirements include:"]
        for req in requirement_data.get("requirements", []):
            requirements.append(f"• {req}")

        return "\n".join(requirements)

    def _generate_proposed_solution(self, product_data: dict) -> str:
        """Generate proposed solution section."""
        if not product_data.get("items"):
            return "Proposed solution details will be customized based on selected products and services."

        solution = ["Our proposed solution includes:"]
        for item in product_data.get("items", []):
            solution.append(f"• {item.get('product_name')}: {item.get('billing_note')}")
            if item.get("features"):
                for feature in item["features"]:
                    solution.append(f"  - {feature}")

        return "\n".join(solution)

    def _generate_implementation_timeline(self, product_data: dict) -> str:
        """Generate implementation timeline."""
        timeline = [
            "Implementation Timeline:",
            "• Week 1-2: Project initiation and environment setup",
            "• Week 3-6: Core system implementation and configuration",
            "• Week 7-10: Integration and customization",
            "• Week 11-12: Testing, training, and go-live support"
        ]
        return "\n".join(timeline)

    def _generate_investment_summary(self, product_data: dict) -> str:
        """Generate investment summary."""
        total = product_data.get("final_total", 0)
        summary = f"""
Investment Summary:
• Total Solution Cost: ${total:,.2f}
• Payment Terms: Net 30 days
• Implementation included in pricing
• 12-month warranty and support included
"""
        return summary.strip()

    def _generate_next_steps(self) -> str:
        """Generate next steps section."""
        return """
Next Steps:
1. Review and approve this proposal
2. Execute service agreement
3. Schedule project kickoff meeting
4. Begin implementation process

We're excited to partner with you on this initiative and look forward to your feedback.
"""

    def _format_quote_items(self, items: list) -> str:
        """Format quote items for document."""
        if not items:
            return "No items specified"

        formatted = ["Product/Service Details:"]
        for item in items:
            formatted.append(f"• {item.get('product_name')}")
            formatted.append(f"  Tier: {item.get('tier')}")
            formatted.append(f"  Quantity: {item.get('quantity')}")
            formatted.append(f"  Unit Price: ${item.get('unit_price'):,.2f}")
            formatted.append(f"  Total: ${item.get('line_total'):,.2f}")
            formatted.append("")

        return "\n".join(formatted)

    def _generate_terms_and_conditions(self) -> str:
        """Generate standard terms and conditions."""
        return """
Terms and Conditions:
• Quote valid for 30 days from issue date
• Payment terms: Net 30 days
• Prices exclude applicable taxes
• Implementation timeline subject to scope confirmation
• Standard warranty and support terms apply
"""

    def _generate_implementation_phases(self, project_data: dict, timeline_weeks: int) -> list:
        """Generate implementation phases."""
        phases = [
            {
                "phase": "Project Initiation",
                "duration_weeks": 2,
                "activities": ["Kickoff meeting", "Environment setup", "Team assignments"],
                "deliverables": ["Project charter", "Environment ready"]
            },
            {
                "phase": "Core Implementation",
                "duration_weeks": timeline_weeks // 2,
                "activities": ["System configuration", "Core feature setup", "Basic integration"],
                "deliverables": ["Configured system", "Basic functionality"]
            },
            {
                "phase": "Customization & Integration",
                "duration_weeks": timeline_weeks // 3,
                "activities": ["Custom features", "Third-party integrations", "Data migration"],
                "deliverables": ["Customized system", "Integrated environment"]
            },
            {
                "phase": "Testing & Go-Live",
                "duration_weeks": timeline_weeks - (timeline_weeks // 2) - (timeline_weeks // 3) - 2,
                "activities": ["System testing", "User training", "Go-live support"],
                "deliverables": ["Tested system", "Trained users", "Live environment"]
            }
        ]
        return phases

    def _generate_resource_requirements(self, project_data: dict) -> dict:
        """Generate resource requirements."""
        return {
            "client_resources": [
                "Project manager (25% allocation)",
                "Subject matter experts (as needed)",
                "IT support (10% allocation)"
            ],
            "vendor_resources": [
                "Implementation lead (100% allocation)",
                "Technical consultants (50% allocation)",
                "Training specialist (25% allocation)"
            ]
        }

    def _generate_risk_assessment(self) -> list:
        """Generate risk assessment."""
        return [
            {
                "risk": "Scope creep",
                "impact": "Medium",
                "mitigation": "Regular scope reviews and change control process"
            },
            {
                "risk": "Resource availability",
                "impact": "High",
                "mitigation": "Confirmed resource allocation before project start"
            },
            {
                "risk": "Integration challenges",
                "impact": "Medium",
                "mitigation": "Early integration testing and validation"
            }
        ]

    def _generate_success_criteria(self) -> list:
        """Generate success criteria."""
        return [
            "System deployed on time and within budget",
            "All functional requirements met",
            "User acceptance criteria satisfied",
            "Performance benchmarks achieved",
            "Knowledge transfer completed"
        ]

    def _generate_scope_of_services(self, agreement: dict) -> str:
        """Generate scope of services."""
        return "Detailed scope of services based on the agreed proposal and specifications."

    def _generate_deliverables(self, agreement: dict) -> str:
        """Generate deliverables section."""
        return "Specific deliverables will be outlined based on the project scope and timeline."

    def _generate_payment_terms(self, agreement: dict) -> str:
        """Generate payment terms."""
        return """
Payment Terms:
• Payment schedule: Net 30 days from invoice date
• Late payment fees: 1.5% per month on overdue amounts
• Invoicing: Monthly for services, upon delivery for products
"""

    def _generate_legal_terms(self) -> str:
        """Generate standard legal terms."""
        return """
Standard Legal Terms:
• Confidentiality and non-disclosure provisions
• Intellectual property rights
• Limitation of liability
• Termination clauses
• Governing law and dispute resolution
"""

    def _generate_signature_blocks(self) -> dict:
        """Generate signature blocks."""
        return {
            "client_signature": {
                "name": "[Client Name]",
                "title": "[Title]",
                "date": "_______________"
            },
            "provider_signature": {
                "name": "[Provider Name]",
                "title": "[Title]",
                "date": "_______________"
            }
        }