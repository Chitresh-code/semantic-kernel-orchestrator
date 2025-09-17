from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from semantic_kernel.functions import kernel_function


class ProductCatalogTools:
    """Mock product catalog tools for demonstration. Replace with actual product database."""

    def __init__(self):
        # Mock product catalog
        self.products = {
            "PROD001": {
                "id": "PROD001",
                "name": "Enterprise Software License",
                "category": "Software",
                "description": "Comprehensive enterprise software solution with advanced analytics and reporting",
                "price_tiers": {
                    "starter": {"price": 15000, "max_users": 50, "features": ["Basic Analytics", "Standard Support"]},
                    "professional": {"price": 35000, "max_users": 200, "features": ["Advanced Analytics", "Priority Support", "Custom Reports"]},
                    "enterprise": {"price": 75000, "max_users": 1000, "features": ["Full Analytics Suite", "24/7 Support", "Custom Integration", "Dedicated Account Manager"]}
                },
                "implementation_cost": 25000,
                "annual_maintenance": 0.2,  # 20% of license cost
                "deployment_time": "6-12 weeks",
                "technical_requirements": {
                    "min_ram": "16GB",
                    "min_storage": "500GB",
                    "os_support": ["Windows Server", "Linux", "Cloud"],
                    "database": ["SQL Server", "PostgreSQL", "Oracle"]
                },
                "industries": ["Manufacturing", "Finance", "Healthcare", "Retail"],
                "roi_timeline": "12-18 months"
            },
            "PROD002": {
                "id": "PROD002",
                "name": "Professional Services",
                "category": "Services",
                "description": "Expert consulting and implementation services",
                "price_tiers": {
                    "consulting": {"price": 200, "unit": "hour", "features": ["Expert Consultation", "Best Practice Guidance"]},
                    "implementation": {"price": 25000, "unit": "project", "features": ["Full Implementation", "Training", "Documentation"]},
                    "managed_services": {"price": 5000, "unit": "month", "features": ["Ongoing Management", "Monitoring", "Updates"]}
                },
                "delivery_time": "2-8 weeks",
                "team_size": "2-5 experts",
                "industries": ["All"],
                "prerequisites": ["Enterprise Software License or equivalent"]
            },
            "PROD003": {
                "id": "PROD003",
                "name": "Cloud Analytics Platform",
                "category": "SaaS",
                "description": "Cloud-based analytics platform with real-time data processing",
                "price_tiers": {
                    "basic": {"price": 500, "unit": "month", "data_limit": "10GB", "users": 5},
                    "standard": {"price": 1500, "unit": "month", "data_limit": "100GB", "users": 25},
                    "premium": {"price": 5000, "unit": "month", "data_limit": "1TB", "users": 100},
                    "enterprise": {"price": 15000, "unit": "month", "data_limit": "unlimited", "users": "unlimited"}
                },
                "features": ["Real-time Processing", "Custom Dashboards", "API Access", "Data Export"],
                "setup_time": "1-2 weeks",
                "integration_options": ["REST API", "Webhooks", "Database Connectors"],
                "compliance": ["SOC 2", "GDPR", "HIPAA"],
                "industries": ["Technology", "Finance", "Marketing", "E-commerce"]
            },
            "PROD004": {
                "id": "PROD004",
                "name": "Training Package",
                "category": "Services",
                "description": "Comprehensive training for software users and administrators",
                "price_tiers": {
                    "user_training": {"price": 150, "unit": "person", "duration": "1 day"},
                    "admin_training": {"price": 500, "unit": "person", "duration": "3 days"},
                    "train_the_trainer": {"price": 2000, "unit": "session", "duration": "5 days"}
                },
                "delivery_options": ["On-site", "Virtual", "Self-paced Online"],
                "certification": "Available for admin and trainer levels",
                "materials_included": ["Workbooks", "Practice Environments", "Certification Exam"],
                "group_discounts": {"5-10": 0.1, "11-20": 0.15, "21+": 0.2}
            }
        }

        # Mock pricing rules and discounts
        self.pricing_rules = {
            "volume_discounts": {
                "100000-250000": 0.05,  # 5% discount
                "250000-500000": 0.10,  # 10% discount
                "500000+": 0.15         # 15% discount
            },
            "loyalty_discounts": {
                "existing_customer": 0.05,
                "multi_year": 0.08
            },
            "industry_discounts": {
                "nonprofit": 0.15,
                "education": 0.20,
                "government": 0.10
            }
        }

    @kernel_function(
        description="""Retrieve detailed information about a specific product from the catalog.

        Input Parameters:
        - product_id (str): Unique product identifier (e.g., 'PROD001', 'PROD002')

        Output:
        - JSON string containing complete product details:
          * Basic info: id, name, category, description
          * Price tiers: Multiple pricing options with features and user limits
          * Technical requirements: OS support, hardware specs, database compatibility
          * Implementation details: deployment time, team size, prerequisites
          * Industry compatibility and ROI information
        - Error message if product not found

        Example: get_product_info('PROD001') returns full Enterprise Software License details with all pricing tiers and technical specs""",
        name="get_product_info"
    )
    def get_product_info(self, product_id: str) -> str:
        """Get detailed information about a specific product."""
        if product_id not in self.products:
            return json.dumps({"error": f"Product {product_id} not found"})

        product = self.products[product_id]
        return json.dumps(product, indent=2)

    @kernel_function(
        description="""Search for products in the catalog using various criteria and filters.

        Input Parameters:
        - query (str): Search term to look for in product names and descriptions (e.g., 'software', 'analytics', 'training')
        - category (str): Optional filter by product category ('Software', 'Services', 'SaaS') (default: None)
        - industry (str): Optional filter by target industry ('Manufacturing', 'Finance', 'Technology', 'All') (default: None)

        Output:
        - JSON string containing:
          * results: Array of matching products with id, name, category, description (truncated to 100 chars)
          * count: Total number of products found
        - Returns empty results if no matches found
        - Searches both product names and descriptions for query terms

        Example: search_products('analytics', 'SaaS', 'Technology') finds SaaS analytics products for technology companies""",
        name="search_products"
    )
    def search_products(self, query: str, category: str = None, industry: str = None) -> str:
        """Search for products based on various criteria."""
        results = []

        for product in self.products.values():
            match = False

            # Check query in name or description
            if query.lower() in product["name"].lower() or query.lower() in product["description"].lower():
                match = True

            # Check category filter
            if category and product["category"].lower() != category.lower():
                match = False

            # Check industry filter
            if industry and "industries" in product:
                if industry not in product["industries"] and "All" not in product["industries"]:
                    match = False

            if match:
                results.append({
                    "id": product["id"],
                    "name": product["name"],
                    "category": product["category"],
                    "description": product["description"][:100] + "..." if len(product["description"]) > 100 else product["description"]
                })

        return json.dumps({"results": results, "count": len(results)}, indent=2)

    @kernel_function(
        description="""Generate a detailed price quote for specific products with automatic discount calculation.

        Input Parameters:
        - product_configs (str): JSON string with array of product configurations, each containing:
          * product_id: Product identifier (e.g., 'PROD001')
          * tier: Pricing tier ('basic', 'professional', 'enterprise', etc.)
          * quantity: Number of units/licenses (default: 1)
        - customer_type (str): Customer classification ('new' or 'existing') for loyalty discounts (default: 'new')
        - industry (str): Customer industry for industry-specific discounts ('nonprofit', 'education', 'government') (default: None)

        Output:
        - JSON string containing complete quote:
          * quote_id: Unique quote identifier
          * created_date and valid_until dates
          * items: Detailed line items with pricing and features
          * subtotal: Total before discounts
          * discounts: Array of applied discounts with rates and amounts
          * final_total: Total after all discounts
          * payment_terms and implementation_notes
        - Automatically applies volume, loyalty, and industry discounts
        - Error message for invalid product configurations

        Example: generate_quote('[{"product_id":"PROD001","tier":"professional","quantity":1}]', 'existing', 'education') creates quote with educational and loyalty discounts""",
        name="generate_quote"
    )
    def generate_quote(self, product_configs: str, customer_type: str = "new", industry: str = None) -> str:
        """Generate a detailed price quote based on product configurations."""
        try:
            # Parse product configurations
            configs = json.loads(product_configs)

            quote_items = []
            subtotal = 0

            for config in configs:
                product_id = config["product_id"]
                tier = config.get("tier", "basic")
                quantity = config.get("quantity", 1)

                if product_id not in self.products:
                    return json.dumps({"error": f"Product {product_id} not found"})

                product = self.products[product_id]

                if tier not in product["price_tiers"]:
                    return json.dumps({"error": f"Tier {tier} not available for product {product_id}"})

                tier_info = product["price_tiers"][tier]
                unit_price = tier_info["price"]

                # Calculate line total
                if tier_info.get("unit") == "month":
                    # For monthly services, assume 12 months
                    line_total = unit_price * 12 * quantity
                    billing_note = "Annual subscription (12 months)"
                else:
                    line_total = unit_price * quantity
                    billing_note = f"One-time fee" if tier_info.get("unit") != "hour" else "Hourly rate"

                quote_items.append({
                    "product_id": product_id,
                    "product_name": product["name"],
                    "tier": tier,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": line_total,
                    "billing_note": billing_note,
                    "features": tier_info.get("features", [])
                })

                subtotal += line_total

            # Apply discounts
            total_discount = 0
            discount_details = []

            # Volume discount
            for threshold, discount_rate in self.pricing_rules["volume_discounts"].items():
                if threshold.endswith("+"):
                    min_amount = int(threshold[:-1])
                    if subtotal >= min_amount:
                        discount_amount = subtotal * discount_rate
                        total_discount += discount_amount
                        discount_details.append({
                            "type": "Volume Discount",
                            "rate": f"{discount_rate*100}%",
                            "amount": discount_amount
                        })
                        break
                else:
                    min_amount, max_amount = map(int, threshold.split("-"))
                    if min_amount <= subtotal <= max_amount:
                        discount_amount = subtotal * discount_rate
                        total_discount += discount_amount
                        discount_details.append({
                            "type": "Volume Discount",
                            "rate": f"{discount_rate*100}%",
                            "amount": discount_amount
                        })
                        break

            # Customer loyalty discount
            if customer_type == "existing":
                loyalty_discount = subtotal * self.pricing_rules["loyalty_discounts"]["existing_customer"]
                total_discount += loyalty_discount
                discount_details.append({
                    "type": "Existing Customer Discount",
                    "rate": "5%",
                    "amount": loyalty_discount
                })

            # Industry discount
            if industry and industry.lower() in self.pricing_rules["industry_discounts"]:
                industry_discount_rate = self.pricing_rules["industry_discounts"][industry.lower()]
                industry_discount = subtotal * industry_discount_rate
                total_discount += industry_discount
                discount_details.append({
                    "type": f"{industry.title()} Industry Discount",
                    "rate": f"{industry_discount_rate*100}%",
                    "amount": industry_discount
                })

            final_total = subtotal - total_discount

            quote = {
                "quote_id": f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "valid_until": (datetime.now().replace(day=datetime.now().day + 30)).strftime("%Y-%m-%d"),
                "items": quote_items,
                "subtotal": subtotal,
                "discounts": discount_details,
                "total_discount": total_discount,
                "final_total": final_total,
                "payment_terms": "Net 30",
                "implementation_notes": "Implementation timeline varies by product selection"
            }

            return json.dumps(quote, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid product configuration format: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Error generating quote: {e}"})

    @kernel_function(
        description="""Get intelligent product recommendations based on customer profile and requirements.

        Input Parameters:
        - industry (str): Customer's industry sector (e.g., 'Manufacturing', 'Finance', 'Technology', 'Healthcare')
        - company_size (str): Company size category ('small', 'medium', 'large')
        - budget_range (str): Budget range in format 'min-max' or 'min+' (e.g., '10000-50000', '100000+')
        - use_case (str): Optional specific use case or requirement (e.g., 'analytics', 'automation') (default: None)

        Output:
        - JSON string containing:
          * recommendations: Array of up to 5 recommended products, each with:
            - product: Basic product information (id, name, category, description)
            - recommended_tier: Best pricing tier with price and features
            - score: Recommendation score based on fit
            - reasons: Array of why this product is recommended
            - implementation_notes: Timeline and deployment information
          * customer_profile: Summary of the input criteria used
        - Products ranked by relevance score considering industry fit, budget, and use case
        - Only includes products within budget range and suitable for company size

        Example: recommend_products('Manufacturing', 'large', '50000-150000', 'automation') returns enterprise solutions for manufacturing automation""",
        name="recommend_products"
    )
    def recommend_products(self, industry: str, company_size: str, budget_range: str, use_case: str = None) -> str:
        """Recommend products based on customer profile and requirements."""
        recommendations = []

        # Parse budget range
        budget_min, budget_max = 0, float('inf')
        if budget_range:
            if "-" in budget_range:
                parts = budget_range.split("-")
                budget_min = int(parts[0])
                budget_max = int(parts[1]) if parts[1] != "+" else float('inf')
            elif budget_range.endswith("+"):
                budget_min = int(budget_range[:-1])

        for product in self.products.values():
            # Check industry compatibility
            if "industries" in product and industry not in product["industries"] and "All" not in product["industries"]:
                continue

            # Find appropriate tier based on company size and budget
            suitable_tiers = []
            for tier_name, tier_info in product["price_tiers"].items():
                price = tier_info["price"]

                # For monthly services, calculate annual cost
                if tier_info.get("unit") == "month":
                    annual_price = price * 12
                else:
                    annual_price = price

                if budget_min <= annual_price <= budget_max:
                    # Check if tier is suitable for company size
                    if company_size and "max_users" in tier_info:
                        company_size_map = {
                            "small": 50,
                            "medium": 200,
                            "large": 1000
                        }
                        if company_size.lower() in company_size_map:
                            if tier_info["max_users"] >= company_size_map[company_size.lower()]:
                                suitable_tiers.append({
                                    "tier": tier_name,
                                    "price": annual_price,
                                    "features": tier_info.get("features", [])
                                })
                    else:
                        suitable_tiers.append({
                            "tier": tier_name,
                            "price": annual_price,
                            "features": tier_info.get("features", [])
                        })

            if suitable_tiers:
                # Calculate recommendation score
                score = 0
                reasons = []

                # Industry match
                if "industries" in product and industry in product["industries"]:
                    score += 30
                    reasons.append(f"Designed for {industry} industry")

                # Use case match
                if use_case:
                    if use_case.lower() in product["description"].lower():
                        score += 20
                        reasons.append(f"Matches {use_case} use case")

                # Budget fit
                best_tier = min(suitable_tiers, key=lambda x: x["price"])
                if best_tier["price"] <= budget_max * 0.8:  # Within 80% of budget
                    score += 25
                    reasons.append("Cost-effective solution")

                recommendations.append({
                    "product": {
                        "id": product["id"],
                        "name": product["name"],
                        "category": product["category"],
                        "description": product["description"]
                    },
                    "recommended_tier": best_tier,
                    "score": score,
                    "reasons": reasons,
                    "implementation_notes": product.get("deployment_time", "Standard timeline")
                })

        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        return json.dumps({
            "recommendations": recommendations[:5],  # Top 5 recommendations
            "customer_profile": {
                "industry": industry,
                "company_size": company_size,
                "budget_range": budget_range,
                "use_case": use_case
            }
        }, indent=2)

    @kernel_function(
        description="""Check compatibility between multiple products and with customer's technical environment.

        Input Parameters:
        - product_ids (str): JSON array of product IDs to check compatibility for (e.g., '["PROD001", "PROD002"]')
        - customer_environment (str): Optional JSON object describing customer's technical setup with fields like:
          * os: Operating system ('Windows Server', 'Linux', 'Cloud')
          * database: Database system ('SQL Server', 'PostgreSQL', 'Oracle')
          * existing_systems: Current software in use

        Output:
        - JSON string containing comprehensive compatibility report:
          * compatible: Overall compatibility status (true/false)
          * products_checked: Array of each product with individual compatibility status and notes
          * integration_options: Available integration methods (APIs, webhooks, connectors)
          * potential_issues: Array of compatibility concerns or conflicts
          * recommendations: Suggested actions for resolving issues
        - Validates technical requirements against customer environment
        - Identifies integration opportunities between selected products

        Example: check_compatibility('["PROD001", "PROD003"]', '{"os": "Linux", "database": "PostgreSQL"}') checks if Enterprise Software and Cloud Analytics work together on customer's Linux/PostgreSQL setup""",
        name="check_compatibility"
    )
    def check_compatibility(self, product_ids: str, customer_environment: str = None) -> str:
        """Check compatibility between products and with customer environment."""
        try:
            product_list = json.loads(product_ids) if isinstance(product_ids, str) else product_ids
            customer_env = json.loads(customer_environment) if customer_environment else {}

            compatibility_report = {
                "compatible": True,
                "products_checked": [],
                "integration_options": [],
                "potential_issues": [],
                "recommendations": []
            }

            for product_id in product_list:
                if product_id not in self.products:
                    compatibility_report["potential_issues"].append(f"Product {product_id} not found")
                    continue

                product = self.products[product_id]
                product_report = {
                    "id": product_id,
                    "name": product["name"],
                    "compatible": True,
                    "notes": []
                }

                # Check technical requirements
                if "technical_requirements" in product and customer_env:
                    tech_req = product["technical_requirements"]

                    # Check OS compatibility
                    if "os" in customer_env and "os_support" in tech_req:
                        if customer_env["os"] not in tech_req["os_support"]:
                            product_report["compatible"] = False
                            product_report["notes"].append(f"OS {customer_env['os']} not supported")

                    # Check database compatibility
                    if "database" in customer_env and "database" in tech_req:
                        if customer_env["database"] not in tech_req["database"]:
                            product_report["notes"].append(f"Database {customer_env['database']} may require additional configuration")

                # Check integration options
                if "integration_options" in product:
                    compatibility_report["integration_options"].extend(product["integration_options"])

                compatibility_report["products_checked"].append(product_report)

                if not product_report["compatible"]:
                    compatibility_report["compatible"] = False

            # Generate recommendations
            if not compatibility_report["compatible"]:
                compatibility_report["recommendations"].append("Consider alternative product configurations or environment upgrades")

            return json.dumps(compatibility_report, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid input format: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Error checking compatibility: {e}"})