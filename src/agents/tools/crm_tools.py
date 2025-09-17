from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from semantic_kernel.functions import kernel_function


class CRMTools:
    """Mock CRM tools for demonstration. Replace with actual CRM API integration."""

    def __init__(self):
        # Mock customer database
        self.customers = {
            "CUST001": {
                "id": "CUST001",
                "name": "Acme Corporation",
                "contact_person": "John Smith",
                "email": "john.smith@acme.com",
                "phone": "+1-555-0123",
                "industry": "Manufacturing",
                "company_size": "500-1000",
                "annual_revenue": 50000000,
                "status": "active",
                "last_contact": "2024-12-15",
                "acquisition_date": "2023-06-01",
                "lifetime_value": 250000,
                "purchase_history": [
                    {"date": "2024-12-01", "product": "Enterprise Software License", "amount": 45000},
                    {"date": "2024-09-15", "product": "Professional Services", "amount": 25000},
                    {"date": "2024-06-01", "product": "Implementation Package", "amount": 75000}
                ],
                "interactions": [
                    {"date": "2024-12-15", "type": "email", "subject": "Q1 2025 Planning", "outcome": "positive"},
                    {"date": "2024-12-10", "type": "call", "subject": "Product Demo", "outcome": "interested"},
                    {"date": "2024-11-20", "type": "meeting", "subject": "Contract Review", "outcome": "negotiating"}
                ],
                "preferences": {
                    "communication_method": "email",
                    "best_contact_time": "10:00-12:00",
                    "decision_maker": "John Smith",
                    "budget_cycle": "quarterly"
                }
            },
            "CUST002": {
                "id": "CUST002",
                "name": "TechStart Inc",
                "contact_person": "Sarah Johnson",
                "email": "sarah@techstart.io",
                "phone": "+1-555-0456",
                "industry": "Technology",
                "company_size": "50-100",
                "annual_revenue": 5000000,
                "status": "prospect",
                "last_contact": "2024-12-12",
                "acquisition_date": None,
                "lifetime_value": 0,
                "purchase_history": [],
                "interactions": [
                    {"date": "2024-12-12", "type": "email", "subject": "Initial Inquiry", "outcome": "interested"},
                    {"date": "2024-12-08", "type": "webinar", "subject": "Product Overview", "outcome": "attended"}
                ],
                "preferences": {
                    "communication_method": "video_call",
                    "best_contact_time": "14:00-16:00",
                    "decision_maker": "Sarah Johnson",
                    "budget_cycle": "annual"
                }
            }
        }

    @kernel_function(
        description="""Retrieve comprehensive customer information from CRM system.

        Input Parameters:
        - customer_id (str): The unique customer identifier (e.g., 'CUST001')

        Output:
        - JSON string containing complete customer profile including:
          * Basic info (name, contact details, industry, company size)
          * Financial data (annual revenue, lifetime value, status)
          * Purchase history with dates, products, and amounts
          * Interaction history with types, dates, and outcomes
          * Customer preferences for communication and decision-making
        - Error message if customer not found

        Example: get_customer_data('CUST001') returns full customer profile with purchase and interaction history""",
        name="get_customer_data"
    )
    def get_customer_data(self, customer_id: str) -> str:
        """Retrieve customer information by ID."""
        if customer_id not in self.customers:
            return json.dumps({"error": f"Customer {customer_id} not found"})

        customer = self.customers[customer_id]
        return json.dumps(customer, indent=2)

    @kernel_function(
        description="""Search for customers by various criteria in the CRM database.

        Input Parameters:
        - query (str): Search term to look for (e.g., 'Acme', 'Manufacturing', 'active')
        - criteria (str): Search field - 'name', 'industry', or 'status' (default: 'name')

        Output:
        - JSON string containing:
          * results: Array of matching customers with id, name, contact_person, status, industry
          * count: Total number of matches found
        - Returns empty results array if no matches

        Example: search_customers('Tech', 'industry') returns all customers in technology industry""",
        name="search_customers"
    )
    def search_customers(self, query: str, criteria: str = "name") -> str:
        """Search for customers by name, industry, or other criteria."""
        results = []

        for customer in self.customers.values():
            if criteria == "name" and query.lower() in customer["name"].lower():
                results.append({
                    "id": customer["id"],
                    "name": customer["name"],
                    "contact_person": customer["contact_person"],
                    "status": customer["status"],
                    "industry": customer["industry"]
                })
            elif criteria == "industry" and query.lower() in customer["industry"].lower():
                results.append({
                    "id": customer["id"],
                    "name": customer["name"],
                    "contact_person": customer["contact_person"],
                    "status": customer["status"],
                    "industry": customer["industry"]
                })
            elif criteria == "status" and query.lower() == customer["status"].lower():
                results.append({
                    "id": customer["id"],
                    "name": customer["name"],
                    "contact_person": customer["contact_person"],
                    "status": customer["status"],
                    "industry": customer["industry"]
                })

        return json.dumps({"results": results, "count": len(results)}, indent=2)

    @kernel_function(
        description="""Get detailed interaction history for a specific customer.

        Input Parameters:
        - customer_id (str): The unique customer identifier (e.g., 'CUST001')
        - limit (int): Maximum number of recent interactions to return (default: 10)

        Output:
        - JSON string containing:
          * customer_id: The customer identifier
          * customer_name: Customer company name
          * interactions: Array of recent interactions with date, type, subject, outcome
        - Error message if customer not found

        Example: get_interaction_history('CUST001', 5) returns last 5 interactions with dates and outcomes""",
        name="get_interaction_history"
    )
    def get_interaction_history(self, customer_id: str, limit: int = 10) -> str:
        """Get recent interaction history for a customer."""
        if customer_id not in self.customers:
            return json.dumps({"error": f"Customer {customer_id} not found"})

        customer = self.customers[customer_id]
        interactions = customer["interactions"][-limit:]

        return json.dumps({
            "customer_id": customer_id,
            "customer_name": customer["name"],
            "interactions": interactions
        }, indent=2)

    @kernel_function(
        description="""Update specific customer information fields in the CRM system.

        Input Parameters:
        - customer_id (str): The unique customer identifier (e.g., 'CUST001')
        - field (str): The field name to update (e.g., 'status', 'phone', 'email', 'annual_revenue')
        - value (str): The new value for the field

        Output:
        - JSON string containing:
          * status: 'success' if update completed
          * message: Confirmation message
          * customer_id: The updated customer ID
          * updated_field: The field that was modified
          * new_value: The new value that was set
        - Error message if customer not found

        Example: update_customer('CUST001', 'status', 'inactive') updates customer status""",
        name="update_customer"
    )
    def update_customer(self, customer_id: str, field: str, value: str) -> str:
        """Update a specific field for a customer."""
        if customer_id not in self.customers:
            return json.dumps({"error": f"Customer {customer_id} not found"})

        # Simple field update (in real implementation, would validate fields)
        self.customers[customer_id][field] = value

        return json.dumps({
            "status": "success",
            "message": f"Updated {field} for customer {customer_id}",
            "customer_id": customer_id,
            "updated_field": field,
            "new_value": value
        }, indent=2)

    @kernel_function(
        description="""Record a new interaction with a customer in the CRM system.

        Input Parameters:
        - customer_id (str): The unique customer identifier (e.g., 'CUST001')
        - interaction_type (str): Type of interaction ('email', 'call', 'meeting', 'demo', 'webinar')
        - subject (str): Brief description of the interaction topic
        - outcome (str): Result of interaction ('positive', 'neutral', 'interested', 'negotiating', 'pending') (default: 'pending')

        Output:
        - JSON string containing:
          * status: 'success' if interaction logged
          * message: Confirmation message
          * interaction: Details of the logged interaction with date, type, subject, outcome
        - Updates customer's last_contact date automatically
        - Error message if customer not found

        Example: log_interaction('CUST001', 'call', 'Product demo discussion', 'interested') logs a successful demo call""",
        name="log_interaction"
    )
    def log_interaction(self, customer_id: str, interaction_type: str, subject: str, outcome: str = "pending") -> str:
        """Log a new interaction with a customer."""
        if customer_id not in self.customers:
            return json.dumps({"error": f"Customer {customer_id} not found"})

        new_interaction = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": interaction_type,
            "subject": subject,
            "outcome": outcome
        }

        self.customers[customer_id]["interactions"].append(new_interaction)
        self.customers[customer_id]["last_contact"] = new_interaction["date"]

        return json.dumps({
            "status": "success",
            "message": "Interaction logged successfully",
            "interaction": new_interaction
        }, indent=2)

    @kernel_function(
        description="""Analyze customer data and provide intelligent next best action recommendations.

        Input Parameters:
        - customer_id (str): The unique customer identifier (e.g., 'CUST001')

        Output:
        - JSON string containing:
          * customer_id: The customer identifier
          * customer_name: Customer company name
          * suggestions: Array of recommended actions, each with:
            - action: Specific action to take
            - priority: 'high', 'medium', or 'low'
            - reason: Explanation for why this action is recommended
        - Recommendations based on customer status, last contact date, purchase history, and recent interactions
        - Error message if customer not found

        Example: suggest_next_action('CUST001') returns prioritized action recommendations like 'Schedule check-in call' or 'Present upsell opportunity'""",
        name="suggest_next_action"
    )
    def suggest_next_action(self, customer_id: str) -> str:
        """Suggest next best action based on customer data and history."""
        if customer_id not in self.customers:
            return json.dumps({"error": f"Customer {customer_id} not found"})

        customer = self.customers[customer_id]
        suggestions = []

        # Analyze customer status and history to suggest actions
        if customer["status"] == "prospect":
            suggestions.append({
                "action": "Schedule discovery call",
                "priority": "high",
                "reason": "New prospect needs qualification and needs assessment"
            })
            suggestions.append({
                "action": "Send product demo invite",
                "priority": "medium",
                "reason": "Visual demonstration can accelerate decision process"
            })

        elif customer["status"] == "active":
            # Check last contact date
            last_contact = datetime.strptime(customer["last_contact"], "%Y-%m-%d")
            days_since_contact = (datetime.now() - last_contact).days

            if days_since_contact > 30:
                suggestions.append({
                    "action": "Schedule check-in call",
                    "priority": "high",
                    "reason": f"No contact for {days_since_contact} days - risk of churn"
                })

            # Check for upsell opportunities
            if customer["purchase_history"]:
                last_purchase = customer["purchase_history"][-1]
                last_purchase_date = datetime.strptime(last_purchase["date"], "%Y-%m-%d")
                months_since_purchase = (datetime.now() - last_purchase_date).days // 30

                if months_since_purchase >= 3:
                    suggestions.append({
                        "action": "Present upsell opportunity",
                        "priority": "medium",
                        "reason": "Customer may be ready for additional products/services"
                    })

        # General suggestions based on interactions
        recent_interactions = customer["interactions"][-3:]
        if any(interaction["outcome"] == "interested" for interaction in recent_interactions):
            suggestions.append({
                "action": "Send detailed proposal",
                "priority": "high",
                "reason": "Customer has shown recent interest"
            })

        return json.dumps({
            "customer_id": customer_id,
            "customer_name": customer["name"],
            "suggestions": suggestions
        }, indent=2)