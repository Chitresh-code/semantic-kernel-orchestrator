from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from semantic_kernel.functions import kernel_function


class EmailCalendarTools:
    """Mock email and calendar tools for demonstration. Replace with actual integrations."""

    def __init__(self):
        # Mock calendar events
        self.calendar_events = [
            {
                "id": "evt001",
                "title": "Sales Team Meeting",
                "start_time": "2024-12-18T10:00:00",
                "end_time": "2024-12-18T11:00:00",
                "attendees": ["sales@company.com"],
                "type": "internal"
            },
            {
                "id": "evt002",
                "title": "Client Demo - TechStart Inc",
                "start_time": "2024-12-19T14:00:00",
                "end_time": "2024-12-19T15:00:00",
                "attendees": ["sarah@techstart.io", "sales@company.com"],
                "type": "client_meeting"
            }
        ]

        # Mock email templates
        self.email_templates = {
            "follow_up": {
                "subject": "Following up on our conversation",
                "body": """Dear {contact_name},

I hope this email finds you well. I wanted to follow up on our recent conversation about {topic}.

{custom_message}

I'd be happy to schedule a call to discuss this further at your convenience.

Best regards,
{sender_name}"""
            },
            "demo_invite": {
                "subject": "Invitation: Product Demo for {company_name}",
                "body": """Dear {contact_name},

Thank you for your interest in our solutions. I'd like to invite you to a personalized product demonstration.

During this demo, we'll show you:
- Key features relevant to {industry}
- How our solution addresses your specific challenges
- Integration capabilities with your existing systems

Please let me know your availability, and I'll send a calendar invitation.

Best regards,
{sender_name}"""
            },
            "proposal_delivery": {
                "subject": "Proposal: {proposal_title}",
                "body": """Dear {contact_name},

Thank you for taking the time to discuss your requirements with us. As promised, I've attached our detailed proposal for {proposal_title}.

Key highlights of our proposal:
- {highlight_1}
- {highlight_2}
- {highlight_3}

I'd be happy to schedule a call to walk through the proposal and answer any questions you may have.

Best regards,
{sender_name}"""
            }
        }

    @kernel_function(
        description="""Send an email using predefined professional templates.

        Input Parameters:
        - template_name (str): Template to use ('follow_up', 'demo_invite', 'proposal_delivery')
        - recipient_email (str): Email address of the recipient
        - **kwargs: Template variables like contact_name, company_name, sender_name, topic, etc.

        Output:
        - JSON string containing:
          * status: 'success' if email sent
          * email_id: Unique identifier for the sent email
          * recipient: Email address where it was sent
          * subject: The email subject line
          * sent_at: Timestamp when email was sent
          * message: Confirmation message
        - Error message if template not found or missing variables

        Example: send_email('demo_invite', 'john@acme.com', contact_name='John Smith', company_name='Acme Corp', industry='Manufacturing', sender_name='Sales Team')""",
        name="send_email"
    )
    def send_email(self, template_name: str, recipient_email: str, **kwargs) -> str:
        """Send an email using a predefined template."""
        if template_name not in self.email_templates:
            return json.dumps({"error": f"Template '{template_name}' not found"})

        template = self.email_templates[template_name]

        try:
            # Fill in template variables
            subject = template["subject"].format(**kwargs)
            body = template["body"].format(**kwargs)

            # Mock email sending (in real implementation, would use actual email service)
            email_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            return json.dumps({
                "status": "success",
                "email_id": email_id,
                "recipient": recipient_email,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "message": "Email sent successfully"
            }, indent=2)

        except KeyError as e:
            return json.dumps({"error": f"Missing template variable: {e}"})

    @kernel_function(
        description="""Send a custom email with your own subject and body content.

        Input Parameters:
        - recipient_email (str): Email address of the recipient
        - subject (str): Email subject line
        - body (str): Full email body content
        - sender_name (str): Name of the sender (default: 'Sales Team')

        Output:
        - JSON string containing:
          * status: 'success' if email sent
          * email_id: Unique identifier for the sent email
          * recipient: Email address where it was sent
          * subject: The email subject line
          * sender: Name of the sender
          * sent_at: Timestamp when email was sent
          * message: Confirmation message

        Example: send_custom_email('jane@techstart.io', 'Follow up on our meeting', 'Hi Jane, Thank you for the productive meeting yesterday...', 'John Sales')""",
        name="send_custom_email"
    )
    def send_custom_email(self, recipient_email: str, subject: str, body: str, sender_name: str = "Sales Team") -> str:
        """Send a custom email with specified content."""
        email_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return json.dumps({
            "status": "success",
            "email_id": email_id,
            "recipient": recipient_email,
            "subject": subject,
            "sender": sender_name,
            "sent_at": datetime.now().isoformat(),
            "message": "Custom email sent successfully"
        }, indent=2)

    @kernel_function(
        description="""Schedule a meeting with specified attendees and check for conflicts.

        Input Parameters:
        - title (str): Meeting title/subject
        - start_time (str): Start time in ISO format (e.g., '2024-12-20T14:00:00')
        - duration_minutes (int): Meeting duration in minutes
        - attendees (str): Comma-separated list of attendee email addresses
        - description (str): Optional meeting description/agenda (default: '')

        Output:
        - JSON string containing:
          * status: 'success' if meeting scheduled, 'conflict' if time conflicts exist
          * event_id: Unique identifier for the scheduled meeting
          * message: Confirmation or conflict details
          * event_details: Complete meeting information with attendees and times
        - If conflict detected, includes details of conflicting event
        - Error message for invalid date format

        Example: schedule_meeting('Product Demo', '2024-12-20T14:00:00', 60, 'john@acme.com,sales@company.com', 'Demo of Enterprise Software features')""",
        name="schedule_meeting"
    )
    def schedule_meeting(self, title: str, start_time: str, duration_minutes: int, attendees: str, description: str = "") -> str:
        """Schedule a meeting with the specified details."""
        try:
            # Parse start time
            start_dt = datetime.fromisoformat(start_time)
            end_dt = start_dt + timedelta(minutes=duration_minutes)

            # Check for conflicts (simple check)
            for event in self.calendar_events:
                event_start = datetime.fromisoformat(event["start_time"])
                event_end = datetime.fromisoformat(event["end_time"])

                if (start_dt < event_end and end_dt > event_start):
                    return json.dumps({
                        "status": "conflict",
                        "message": f"Time conflict with existing event: {event['title']}",
                        "conflicting_event": event
                    }, indent=2)

            # Create new event
            event_id = f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            new_event = {
                "id": event_id,
                "title": title,
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "attendees": attendees.split(","),
                "description": description,
                "type": "scheduled_meeting"
            }

            self.calendar_events.append(new_event)

            return json.dumps({
                "status": "success",
                "event_id": event_id,
                "message": "Meeting scheduled successfully",
                "event_details": new_event
            }, indent=2)

        except ValueError as e:
            return json.dumps({"error": f"Invalid date format: {e}"})

    @kernel_function(
        description="""Find available time slots within a date range for scheduling meetings.

        Input Parameters:
        - start_date (str): Start date/time to search from in ISO format (e.g., '2024-12-20T09:00:00')
        - end_date (str): End date/time to search until in ISO format (e.g., '2024-12-21T17:00:00')
        - duration_minutes (int): Required meeting duration in minutes (default: 60)

        Output:
        - JSON string containing:
          * available_slots: Array of available time slots, each with start_time, end_time, duration_minutes
          * total_found: Total number of available slots found
        - Only shows business hours (9 AM - 5 PM, Monday-Friday)
        - Excludes existing calendar conflicts
        - Returns first 10 available slots
        - Error message for invalid date format

        Example: find_available_slots('2024-12-20T09:00:00', '2024-12-21T17:00:00', 90) finds 90-minute slots over 2 days""",
        name="find_available_slots"
    )
    def find_available_slots(self, start_date: str, end_date: str, duration_minutes: int = 60) -> str:
        """Find available time slots within a date range."""
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)

            # Business hours: 9 AM to 5 PM, Monday to Friday
            available_slots = []
            current_dt = start_dt

            while current_dt < end_dt:
                # Skip weekends
                if current_dt.weekday() >= 5:
                    current_dt += timedelta(days=1)
                    current_dt = current_dt.replace(hour=9, minute=0, second=0, microsecond=0)
                    continue

                # Check business hours
                if current_dt.hour < 9:
                    current_dt = current_dt.replace(hour=9, minute=0, second=0, microsecond=0)
                elif current_dt.hour >= 17:
                    current_dt += timedelta(days=1)
                    current_dt = current_dt.replace(hour=9, minute=0, second=0, microsecond=0)
                    continue

                # Check if slot is available
                slot_end = current_dt + timedelta(minutes=duration_minutes)
                if slot_end.hour > 17:
                    current_dt += timedelta(days=1)
                    current_dt = current_dt.replace(hour=9, minute=0, second=0, microsecond=0)
                    continue

                # Check for conflicts
                is_available = True
                for event in self.calendar_events:
                    event_start = datetime.fromisoformat(event["start_time"])
                    event_end = datetime.fromisoformat(event["end_time"])

                    if (current_dt < event_end and slot_end > event_start):
                        is_available = False
                        break

                if is_available:
                    available_slots.append({
                        "start_time": current_dt.isoformat(),
                        "end_time": slot_end.isoformat(),
                        "duration_minutes": duration_minutes
                    })

                # Move to next potential slot (30-minute intervals)
                current_dt += timedelta(minutes=30)

            return json.dumps({
                "available_slots": available_slots[:10],  # Return first 10 slots
                "total_found": len(available_slots)
            }, indent=2)

        except ValueError as e:
            return json.dumps({"error": f"Invalid date format: {e}"})

    @kernel_function(
        description="""Retrieve calendar events within a specified date range.

        Input Parameters:
        - start_date (str): Start date to search from in ISO format (e.g., '2024-12-20T00:00:00')
        - end_date (str): End date to search until in ISO format (e.g., '2024-12-21T23:59:59')

        Output:
        - JSON string containing:
          * events: Array of calendar events with id, title, start_time, end_time, attendees, type
          * count: Total number of events found
          * date_range: The search date range used
        - Shows all events (internal meetings, client meetings, etc.)
        - Error message for invalid date format

        Example: get_calendar_events('2024-12-20T00:00:00', '2024-12-21T23:59:59') returns all events for 2 days""",
        name="get_calendar_events"
    )
    def get_calendar_events(self, start_date: str, end_date: str) -> str:
        """Get calendar events within a specified date range."""
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)

            events_in_range = []
            for event in self.calendar_events:
                event_start = datetime.fromisoformat(event["start_time"])
                if start_dt <= event_start <= end_dt:
                    events_in_range.append(event)

            return json.dumps({
                "events": events_in_range,
                "count": len(events_in_range),
                "date_range": {
                    "start": start_date,
                    "end": end_date
                }
            }, indent=2)

        except ValueError as e:
            return json.dumps({"error": f"Invalid date format: {e}"})

    @kernel_function(
        description="""Cancel or reschedule an existing calendar meeting.

        Input Parameters:
        - event_id (str): Unique identifier of the meeting to manage (e.g., 'evt001')
        - action (str): Action to perform ('cancel' or 'reschedule')
        - new_start_time (str): New start time in ISO format - required for reschedule action (e.g., '2024-12-21T10:00:00')

        Output:
        - JSON string containing:
          * status: 'success' if action completed
          * message: Confirmation message describing what was done
          * cancelled_event OR updated_event: Details of the affected meeting
        - For reschedule: maintains original duration and updates both start and end times
        - Error message if event not found, invalid action, or missing new_start_time for reschedule

        Example: manage_meeting('evt001', 'reschedule', '2024-12-21T10:00:00') moves meeting to new time""",
        name="manage_meeting"
    )
    def manage_meeting(self, event_id: str, action: str, new_start_time: str = None) -> str:
        """Cancel or reschedule a meeting."""
        # Find the event
        event = None
        for i, evt in enumerate(self.calendar_events):
            if evt["id"] == event_id:
                event = evt
                event_index = i
                break

        if not event:
            return json.dumps({"error": f"Event {event_id} not found"})

        if action == "cancel":
            self.calendar_events.pop(event_index)
            return json.dumps({
                "status": "success",
                "message": f"Meeting '{event['title']}' has been cancelled",
                "cancelled_event": event
            }, indent=2)

        elif action == "reschedule" and new_start_time:
            try:
                new_start_dt = datetime.fromisoformat(new_start_time)
                original_duration = datetime.fromisoformat(event["end_time"]) - datetime.fromisoformat(event["start_time"])
                new_end_dt = new_start_dt + original_duration

                # Update the event
                event["start_time"] = new_start_dt.isoformat()
                event["end_time"] = new_end_dt.isoformat()

                return json.dumps({
                    "status": "success",
                    "message": f"Meeting '{event['title']}' has been rescheduled",
                    "updated_event": event
                }, indent=2)

            except ValueError as e:
                return json.dumps({"error": f"Invalid date format: {e}"})

        else:
            return json.dumps({"error": "Invalid action or missing new_start_time for reschedule"})