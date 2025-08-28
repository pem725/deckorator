#!/usr/bin/env python3
"""
Deckorator - Interactive Deck Planning System (Enhanced)
Generates custom XML templates for LLM processing with session persistence and photo album integration.
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from pathlib import Path

class DeckPlanner:
    def __init__(self):
        self.user_responses = {}
        self.suppliers_db = {}
        self.existing_template = None
        self.template_version = "2.0"  # Track template versions
        self.load_suppliers_database()
        
    def load_suppliers_database(self):
        """Load supplier database or create default"""
        try:
            with open('suppliers_database.json', 'r') as f:
                self.suppliers_db = json.load(f)
        except FileNotFoundError:
            # Create basic database if file doesn't exist
            self.suppliers_db = {
                "22032": {
                    "area": "Burke/Fairfax, Virginia",
                    "suppliers": ["Home Depot Burke", "Lowe's Burke", "Superior Building Supply"]
                },
                "default": {
                    "area": "Your local area",
                    "suppliers": ["Home Depot", "Lowe's", "Local lumber yards"]
                }
            }
    
    def detect_existing_templates(self):
        """Find existing template files"""
        xml_files = list(Path('.').glob('deck_plan_request_*.xml'))
        if xml_files:
            # Get the most recent template
            latest_template = max(xml_files, key=os.path.getctime)
            return latest_template
        return None
    
    def parse_existing_template(self, template_file):
        """Parse existing XML template and extract user responses"""
        try:
            tree = ET.parse(template_file)
            root = tree.getroot()
            
            # Extract user responses from XML
            responses = {}
            
            # Project basics
            project_basics = root.find('.//project_basics')
            if project_basics is not None:
                responses['deck_size'] = self.safe_get_text(project_basics, 'deck_size')
                responses['budget_range'] = self.safe_get_text(project_basics, 'budget_range')
                timeline = self.safe_get_text(project_basics, 'timeline')
                if timeline and ' - ' in timeline:
                    parts = timeline.split(' - ')
                    responses['start_timeframe'] = parts[0].strip()
                    responses['completion_timeline'] = parts[1].strip()
            
            # Site information
            site_info = root.find('.//site_information')
            if site_info is not None:
                location = site_info.find('location')
                if location is not None:
                    responses['zip_code'] = self.safe_get_text(location, 'zip_code')
                responses['attachment_type'] = self.safe_get_text(site_info, 'attachment_type')
                responses['ground_conditions'] = self.safe_get_text(site_info, 'ground_conditions')
                responses['height_from_ground'] = self.safe_get_text(site_info, 'height_from_ground')
            
            # Materials and design
            materials = root.find('.//materials_and_design')
            if materials is not None:
                responses['decking_material'] = self.safe_get_text(materials, 'decking_material')
                responses['railing_style'] = self.safe_get_text(materials, 'railing_style')
                responses['special_features'] = self.safe_get_text(materials, 'special_features')
            
            # Work approach
            work_approach = root.find('.//work_approach')
            if work_approach is not None:
                responses['primary_builder'] = self.safe_get_text(work_approach, 'primary_builder')
                responses['construction_experience'] = self.safe_get_text(work_approach, 'construction_experience')
                responses['helpers_available'] = self.safe_get_text(work_approach, 'helpers_available')
                responses['helper_details'] = self.safe_get_text(work_approach, 'helper_details')
                responses['work_schedule'] = self.safe_get_text(work_approach, 'work_schedule')
            
            # Work assignments
            work_assignments = root.find('.//work_assignments')
            if work_assignments is not None:
                responses['work_assignments'] = {}
                for child in work_assignments:
                    phase_name = child.tag.replace('_', ' ').replace('and', '&').title()
                    responses['work_assignments'][phase_name] = child.text or ''
            
            # Photo albums (new feature)
            photo_resources = root.find('.//photo_resources')
            if photo_resources is not None:
                responses['photo_album_url'] = self.safe_get_text(photo_resources, 'shared_album_url')
                responses['photo_album_description'] = self.safe_get_text(photo_resources, 'album_description')
            
            # Project type and complexity
            project_overview = root.find('.//project_overview')
            if project_overview is not None:
                responses['project_type'] = self.safe_get_text(project_overview, 'project_type')
                complexity = self.safe_get_text(project_overview, 'complexity_level')
                responses['complexity'] = 'Advanced' if complexity == 'advanced' else 'Basic'
            
            return responses
            
        except Exception as e:
            print(f"⚠️  Warning: Could not parse existing template: {e}")
            return {}
    
    def safe_get_text(self, parent, tag_name):
        """Safely get text content from XML element"""
        element = parent.find(tag_name)
        return element.text if element is not None and element.text else ''
    
    def welcome_message(self):
        """Display welcome and instructions"""
        print("🏗️  DECKORATOR - Interactive Deck Planning System v2.0")
        print("=" * 60)
        print("This tool creates a custom deck planning template that you can")
        print("submit to an LLM (like Claude or ChatGPT) along with:")
        print("• Photos of your planned deck area (or shared photo albums)")
        print("• Hand-drawn sketches of desired design") 
        print("• Precise measurements or estimates")
        print("• Material preferences")
        print("\nThe LLM will then generate detailed construction plans,")
        print("material lists, cost estimates, and step-by-step instructions.")
        print("\n" + "=" * 60 + "\n")
    
    def handle_existing_template(self, template_file):
        """Handle existing template - update or start fresh"""
        print(f"📁 EXISTING TEMPLATE FOUND: {template_file}")
        print("-" * 40)
        print("This template was created:", datetime.fromtimestamp(os.path.getctime(template_file)).strftime('%Y-%m-%d %H:%M:%S'))
        
        choice = self.get_user_input(
            "What would you like to do?",
            [
                "Update existing template (keep previous answers, add new features)",
                "Start completely fresh (ignore existing template)",
                "Review existing template details first"
            ]
        )
        
        if "Update existing" in choice:
            print("📋 Loading existing template data...")
            self.user_responses = self.parse_existing_template(template_file)
            self.existing_template = template_file
            print(f"✅ Loaded {len(self.user_responses)} previous responses")
            print("   You'll be prompted to review and update your information.")
            return True
            
        elif "Review existing" in choice:
            print(f"\n📖 EXISTING TEMPLATE SUMMARY")
            print("-" * 30)
            existing_data = self.parse_existing_template(template_file)
            
            key_info = [
                ('Project Type', existing_data.get('project_type', 'Not specified')),
                ('Complexity', existing_data.get('complexity', 'Not specified')),
                ('Deck Size', existing_data.get('deck_size', 'Not specified')),
                ('Budget', existing_data.get('budget_range', 'Not specified')),
                ('Zip Code', existing_data.get('zip_code', 'Not specified')),
                ('Primary Builder', existing_data.get('primary_builder', 'Not specified')),
                ('Experience Level', existing_data.get('construction_experience', 'Not specified'))
            ]
            
            for label, value in key_info:
                print(f"  {label}: {value}")
            
            print("\n" + "-" * 30)
            continue_choice = self.get_user_input(
                "Now what would you like to do?",
                ["Update this template", "Start fresh instead"]
            )
            
            if "Update" in continue_choice:
                self.user_responses = existing_data
                self.existing_template = template_file
                return True
            else:
                return False
        
        else:  # Start fresh
            return False
    
    def get_user_input(self, prompt, options=None, input_type="text", current_value=None):
        """Get validated user input with option to keep existing values"""
        while True:
            if current_value and current_value.strip():
                if options:
                    print(f"\n{prompt}")
                    print(f"  Current: {current_value}")
                    for i, option in enumerate(options, 1):
                        print(f"  {i}. {option}")
                    print(f"  K. Keep current value ({current_value})")
                    
                    choice = input("\nEnter choice (number or K to keep current): ").strip().upper()
                    if choice == 'K':
                        return current_value
                    try:
                        choice_num = int(choice) - 1
                        if 0 <= choice_num < len(options):
                            return options[choice_num]
                        else:
                            print("❌ Invalid choice. Please try again.")
                    except ValueError:
                        print("❌ Please enter a valid number or K.")
                else:
                    print(f"\n{prompt}")
                    print(f"Current value: {current_value}")
                    response = input("Enter new value (or press Enter to keep current): ").strip()
                    if response:
                        return response
                    else:
                        return current_value
            else:
                # No current value, regular input
                if options:
                    print(f"\n{prompt}")
                    for i, option in enumerate(options, 1):
                        print(f"  {i}. {option}")
                    try:
                        choice = int(input("\nEnter choice (number): ")) - 1
                        if 0 <= choice < len(options):
                            return options[choice]
                        else:
                            print("❌ Invalid choice. Please try again.")
                    except ValueError:
                        print("❌ Please enter a valid number.")
                else:
                    response = input(f"\n{prompt}: ").strip()
                    if response:
                        return response
                    else:
                        print("❌ Please provide a response.")
    
    def collect_photo_resources(self):
        """Collect photo album URLs and local photo information"""
        print("\n📸 PHOTO RESOURCES")
        print("-" * 20)
        print("You can provide photos in two ways:")
        print("1. Share a Google Photos album or other online album")
        print("2. Upload individual photos when submitting to the AI")
        
        # Photo album URL
        current_album = self.user_responses.get('photo_album_url', '')
        album_url = self.get_user_input(
            "Do you have a shared photo album URL? (Google Photos, iCloud, etc.)\nEnter URL or leave blank if none",
            current_value=current_album
        )
        
        if album_url and album_url.strip():
            # Validate URL format
            if not (album_url.startswith('http://') or album_url.startswith('https://')):
                album_url = 'https://' + album_url
            
            self.user_responses['photo_album_url'] = album_url
            
            # Get description of what's in the album
            current_desc = self.user_responses.get('photo_album_description', '')
            self.user_responses['photo_album_description'] = self.get_user_input(
                "Briefly describe what photos are in this album",
                current_value=current_desc or "Site photos, existing deck area, inspiration images, hand-drawn sketches"
            )
        else:
            self.user_responses['photo_album_url'] = ""
            self.user_responses['photo_album_description'] = "Individual photos will be uploaded during AI submission"
        
        # Local photo guidance
        print("\n💡 PHOTO TIPS:")
        if album_url:
            print("✅ Great! Your shared album will be referenced in the template.")
            print("   The AI can access public albums or you can share screenshots.")
        else:
            print("📷 Remember to take photos of:")
            print("   • Planned deck area from multiple angles")
            print("   • House attachment point")
            print("   • Ground conditions and slope")
            print("   • Any obstacles or utilities")
            print("   • Hand-drawn sketches of desired design")
    
    def collect_project_basics(self):
        """Collect basic project information"""
        print("\n📋 PROJECT BASICS")
        print("-" * 20)
        
        current_project_type = self.user_responses.get('project_type', '')
        self.user_responses['project_type'] = self.get_user_input(
            "What type of deck project is this?",
            ["New deck construction", "Deck repair/renovation", "Deck expansion/addition"],
            current_value=current_project_type
        )
        
        current_complexity = self.user_responses.get('complexity', '')
        self.user_responses['complexity'] = self.get_user_input(
            "What level of planning detail do you need?",
            ["Basic (simple rectangular deck, first-time builder)", 
             "Advanced (complex design, multiple levels, professional coordination)"],
            current_value=current_complexity
        )
        
        current_zip = self.user_responses.get('zip_code', '')
        self.user_responses['zip_code'] = self.get_user_input(
            "What's your zip code? (for local supplier recommendations)",
            current_value=current_zip
        )
        
        # Estimate project size
        current_size = self.user_responses.get('deck_size', '')
        self.user_responses['deck_size'] = self.get_user_input(
            "Approximate deck size?",
            ["Small (under 200 sq ft)", "Medium (200-400 sq ft)", "Large (400+ sq ft)"],
            current_value=current_size
        )
        
        current_budget = self.user_responses.get('budget_range', '')
        self.user_responses['budget_range'] = self.get_user_input(
            "What's your budget range?",
            ["Under $5,000", "$5,000 - $10,000", "$10,000 - $20,000", "Over $20,000"],
            current_value=current_budget
        )
    
    def collect_location_details(self):
        """Collect location and site information"""
        print("\n🏠 LOCATION & SITE")
        print("-" * 20)
        
        current_attachment = self.user_responses.get('attachment_type', '')
        self.user_responses['attachment_type'] = self.get_user_input(
            "How will the deck attach to your house?",
            ["Attached to house (ledger board)", "Freestanding deck", "Not sure - need advice"],
            current_value=current_attachment
        )
        
        current_ground = self.user_responses.get('ground_conditions', '')
        self.user_responses['ground_conditions'] = self.get_user_input(
            "Describe your ground conditions:",
            ["Level ground", "Slight slope", "Steep slope", "Very uneven terrain"],
            current_value=current_ground
        )
        
        current_height = self.user_responses.get('height_from_ground', '')
        self.user_responses['height_from_ground'] = self.get_user_input(
            "How high off the ground will the deck be?",
            ["Ground level (under 30 inches)", "Standard height (30 inches - 6 feet)", 
             "High deck (over 6 feet)", "Not sure - need calculations"],
            current_value=current_height
        )
    
    def collect_diy_vs_professional(self):
        """Determine what user will DIY vs hire out"""
        print("\n🔨 DIY vs PROFESSIONAL WORK")
        print("-" * 30)
        
        print("For each phase, tell us your plan:")
        
        phases = [
            ("Planning & Permits", "Research, design, permit applications"),
            ("Foundation Work", "Digging holes, pouring concrete, setting posts"),
            ("Framing", "Joist installation, beam work, structural assembly"),
            ("Decking Installation", "Installing deck boards, cutting, fastening"),
            ("Railing & Stairs", "Safety railings, stair construction"),
            ("Electrical Work", "Outlets, lighting, electrical connections"),
            ("Finishing", "Staining, sealing, final details")
        ]
        
        if 'work_assignments' not in self.user_responses:
            self.user_responses['work_assignments'] = {}
        
        for phase, description in phases:
            print(f"\n{phase}: {description}")
            current_assignment = self.user_responses['work_assignments'].get(phase, '')
            choice = self.get_user_input(
                f"Your plan for {phase}",
                ["I'll do it myself (DIY)", "Family/friends will help", 
                 "Hire professionals", "Not sure - need advice"],
                current_value=current_assignment
            )
            self.user_responses['work_assignments'][phase] = choice
    
    def collect_family_resources(self):
        """Collect information about available family help"""
        print("\n👨‍👩‍👧‍👦 FAMILY & HELPER RESOURCES")
        print("-" * 35)
        
        current_primary = self.user_responses.get('primary_builder', '')
        self.user_responses['primary_builder'] = self.get_user_input(
            "Who is the primary person managing this project?",
            current_value=current_primary
        )
        
        current_experience = self.user_responses.get('construction_experience', '')
        self.user_responses['construction_experience'] = self.get_user_input(
            "What's your construction experience level?",
            ["Complete beginner", "Some DIY experience", 
             "Experienced DIYer", "Professional background"],
            current_value=current_experience
        )
        
        current_helpers = self.user_responses.get('helpers_available', '')
        helpers_available = self.get_user_input(
            "Do you have helpers available?",
            ["Just me (solo project)", "Spouse/partner available", 
             "Family members can help", "Friends/neighbors will help", 
             "Multiple helpers available"],
            current_value=current_helpers
        )
        self.user_responses['helpers_available'] = helpers_available
        
        if "help" in helpers_available.lower():
            current_details = self.user_responses.get('helper_details', '')
            self.user_responses['helper_details'] = self.get_user_input(
                "Describe your helpers (ages, experience levels, availability)",
                current_value=current_details
            )
    
    def collect_timeline_preferences(self):
        """Collect timing and schedule preferences"""
        print("\n🗓️ TIMELINE & SCHEDULING")
        print("-" * 25)
        
        current_start = self.user_responses.get('start_timeframe', '')
        self.user_responses['start_timeframe'] = self.get_user_input(
            "When do you want to start construction?",
            ["As soon as possible", "Next month", "This spring", 
             "This summer", "This fall", "Next year"],
            current_value=current_start
        )
        
        current_schedule = self.user_responses.get('work_schedule', '')
        self.user_responses['work_schedule'] = self.get_user_input(
            "When can you work on the project?",
            ["Weekends only", "Evenings and weekends", 
             "Flexible schedule", "Full-time dedication"],
            current_value=current_schedule
        )
        
        current_completion = self.user_responses.get('completion_timeline', '')
        self.user_responses['completion_timeline'] = self.get_user_input(
            "How quickly do you want to complete it?",
            ["Take my time (2-3 months)", "Moderate pace (1 month)", 
             "Fast completion (2-3 weeks)", "As quick as possible"],
            current_value=current_completion
        )
    
    def collect_material_preferences(self):
        """Collect material and design preferences"""
        print("\n🪵 MATERIALS & DESIGN PREFERENCES")
        print("-" * 35)
        
        current_decking = self.user_responses.get('decking_material', '')
        self.user_responses['decking_material'] = self.get_user_input(
            "What decking material do you prefer?",
            ["Pressure-treated lumber (economical)", "Cedar (natural, premium)", 
             "Composite decking (low maintenance)", "Not sure - need recommendations"],
            current_value=current_decking
        )
        
        current_railing = self.user_responses.get('railing_style', '')
        self.user_responses['railing_style'] = self.get_user_input(
            "What railing style do you want?",
            ["Simple wood railings", "Decorative balusters", 
             "Cable railings (modern)", "Glass panels (premium)", 
             "Not sure - need ideas"],
            current_value=current_railing
        )
        
        current_features = self.user_responses.get('special_features', '')
        self.user_responses['special_features'] = self.get_user_input(
            "Any special features desired?",
            ["Just basic deck", "Built-in seating", "Lighting", 
             "Multiple levels", "Pergola/shade structure", 
             "Outdoor kitchen prep", "Multiple features"],
            current_value=current_features
        )
    
    def get_local_suppliers(self, zip_code):
        """Get suppliers for user's zip code"""
        if zip_code in self.suppliers_db:
            return self.suppliers_db[zip_code]
        else:
            return self.suppliers_db["default"]
    
    def generate_xml_template(self):
        """Generate the final XML template for LLM submission"""
        is_advanced = "Advanced" in self.user_responses.get('complexity', '')
        local_suppliers = self.get_local_suppliers(self.user_responses['zip_code'])
        
        # Choose template based on complexity
        if is_advanced:
            xml_content = self.generate_advanced_template()
        else:
            xml_content = self.generate_basic_template()
        
        return xml_content
    
    def generate_basic_template(self):
        """Generate basic template XML"""
        local_suppliers = self.get_local_suppliers(self.user_responses['zip_code'])
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<deck_planning_request>
  <project_overview>
    <description>Custom deck planning request generated by Deckorator system v{self.template_version}</description>
    <project_type>{self.user_responses.get('project_type', '')}</project_type>
    <complexity_level>basic</complexity_level>
    <generated_date>{datetime.now().strftime('%Y-%m-%d')}</generated_date>
    <template_version>{self.template_version}</template_version>
  </project_overview>

  <user_requirements>
    <project_basics>
      <deck_size>{self.user_responses.get('deck_size', '')}</deck_size>
      <budget_range>{self.user_responses.get('budget_range', '')}</budget_range>
      <timeline>{self.user_responses.get('start_timeframe', '')} - {self.user_responses.get('completion_timeline', '')}</timeline>
    </project_basics>
    
    <site_information>
      <location>
        <zip_code>{self.user_responses.get('zip_code', '')}</zip_code>
        <area>{local_suppliers.get('area', 'Local area')}</area>
      </location>
      <attachment_type>{self.user_responses.get('attachment_type', '')}</attachment_type>
      <ground_conditions>{self.user_responses.get('ground_conditions', '')}</ground_conditions>
      <height_from_ground>{self.user_responses.get('height_from_ground', '')}</height_from_ground>
    </site_information>

    <materials_and_design>
      <decking_material>{self.user_responses.get('decking_material', '')}</decking_material>
      <railing_style>{self.user_responses.get('railing_style', '')}</railing_style>
      <special_features>{self.user_responses.get('special_features', '')}</special_features>
    </materials_and_design>

    <work_approach>
      <primary_builder>{self.user_responses.get('primary_builder', '')}</primary_builder>
      <construction_experience>{self.user_responses.get('construction_experience', '')}</construction_experience>
      <helpers_available>{self.user_responses.get('helpers_available', '')}</helpers_available>
      <helper_details>{self.user_responses.get('helper_details', '')}</helper_details>
      <work_schedule>{self.user_responses.get('work_schedule', '')}</work_schedule>
    </work_approach>

    <work_assignments>'''
        
        for phase, assignment in self.user_responses.get('work_assignments', {}).items():
            xml_content += f'\n      <{phase.lower().replace(" & ", "_").replace(" ", "_")}>{assignment}</{phase.lower().replace(" & ", "_").replace(" ", "_")}>'
        
        xml_content += f'''
    </work_assignments>
  </user_requirements>

  <photo_resources>
    <shared_album_url>{self.user_responses.get('photo_album_url', '')}</shared_album_url>
    <album_description>{self.user_responses.get('photo_album_description', '')}</album_description>
    <photo_instructions>
      <if_shared_album>If shared album URL is provided above, please access and analyze all photos in the album for site conditions, existing structures, and design inspiration.</if_shared_album>
      <if_individual_photos>Individual photos will be uploaded with this request showing site conditions, measurements, and hand-drawn sketches.</if_individual_photos>
    </photo_instructions>
  </photo_resources>

  <local_resources>
    <suppliers>'''
        
        for supplier in local_suppliers.get('suppliers', []):
            xml_content += f'\n      <supplier>{supplier}</supplier>'
        
        xml_content += f'''
    </suppliers>
    <building_codes>
      <jurisdiction>Check local building department for {self.user_responses.get('zip_code', 'your area')}</jurisdiction>
      <permit_likely_required>{self.user_responses.get('height_from_ground', '') != 'Ground level (under 30 inches)'}</permit_likely_required>
    </building_codes>
  </local_resources>

  <deliverables_requested>
    <material_list>true</material_list>
    <cost_estimate>true</cost_estimate>
    <step_by_step_instructions>true</step_by_step_instructions>
    <safety_guidelines>true</safety_guidelines>
    <tool_requirements>true</tool_requirements>
    <timeline_estimate>true</timeline_estimate>
    <local_supplier_recommendations>true</local_supplier_recommendations>
    <permit_guidance>true</permit_guidance>
  </deliverables_requested>

  <context_instructions>
    <role>Act as an experienced, family-friendly deck contractor who explains things clearly for the user's experience level: {self.user_responses.get('construction_experience', '')}</role>
    <safety_priority>Always prioritize safety recommendations appropriate for DIY builders with {self.user_responses.get('construction_experience', '')} experience</safety_priority>
    <budget_conscious>Provide cost-effective solutions within the {self.user_responses.get('budget_range', '')} budget range</budget_conscious>
    <local_focus>Reference suppliers and building codes for {local_suppliers.get('area', 'the local area')}</local_focus>
    <family_coordination>Consider that helpers include: {self.user_responses.get('helpers_available', 'solo builder')}</family_coordination>
    <photo_integration>Analyze provided photos or shared album to give specific recommendations for this exact site and conditions</photo_integration>
    <response_format>Provide organized sections with clear headings, actionable steps, and safety callouts appropriate for the user's experience level</response_format>
  </context_instructions>

  <submission_instructions>
    <photos_to_include>
      <shared_album>If you provided a shared album URL above, mention it in your message to the AI</shared_album>
      <individual_photos>Upload individual photos showing: site conditions, house attachment point, ground slope, obstacles, hand-drawn sketches</individual_photos>
      <reference_photos>Any inspiration photos or similar decks you like</reference_photos>
    </photos_to_include>
    
    <additional_context>
      <specific_questions>List any specific questions or concerns you have about the project</specific_questions>
      <constraints>Mention any HOA requirements, neighbor considerations, or site limitations</constraints>
      <timeline_flexibility>Indicate if your timeline is flexible or if you have hard deadlines</timeline_flexibility>
    </additional_context>
  </submission_instructions>
</deck_planning_request>'''
        
        return xml_content
    
    def generate_advanced_template(self):
        """Generate advanced template XML with more detailed requirements"""
        local_suppliers = self.get_local_suppliers(self.user_responses['zip_code'])
        
        # Similar structure but with advanced sections
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<deck_planning_request>
  <project_overview>
    <description>Advanced deck planning request with professional coordination capabilities v{self.template_version}</description>
    <project_type>{self.user_responses.get('project_type', '')}</project_type>
    <complexity_level>advanced</complexity_level>
    <generated_date>{datetime.now().strftime('%Y-%m-%d')}</generated_date>
    <template_version>{self.template_version}</template_version>
  </project_overview>

  <user_requirements>
    <project_basics>
      <deck_size>{self.user_responses.get('deck_size', '')}</deck_size>
      <budget_range>{self.user_responses.get('budget_range', '')}</budget_range>
      <timeline>{self.user_responses.get('start_timeframe', '')} - {self.user_responses.get('completion_timeline', '')}</timeline>
    </project_basics>
    
    <site_information>
      <location>
        <zip_code>{self.user_responses.get('zip_code', '')}</zip_code>
        <area>{local_suppliers.get('area', 'Local area')}</area>
      </location>
      <attachment_type>{self.user_responses.get('attachment_type', '')}</attachment_type>
      <ground_conditions>{self.user_responses.get('ground_conditions', '')}</ground_conditions>
      <height_from_ground>{self.user_responses.get('height_from_ground', '')}</height_from_ground>
    </site_information>

    <materials_and_design>
      <decking_material>{self.user_responses.get('decking_material', '')}</decking_material>
      <railing_style>{self.user_responses.get('railing_style', '')}</railing_style>
      <special_features>{self.user_responses.get('special_features', '')}</special_features>
    </materials_and_design>

    <work_approach>
      <primary_builder>{self.user_responses.get('primary_builder', '')}</primary_builder>
      <construction_experience>{self.user_responses.get('construction_experience', '')}</construction_experience>
      <helpers_available>{self.user_responses.get('helpers_available', '')}</helpers_available>
      <helper_details>{self.user_responses.get('helper_details', '')}</helper_details>
      <work_schedule>{self.user_responses.get('work_schedule', '')}</work_schedule>
    </work_approach>

    <work_assignments>'''
        
        for phase, assignment in self.user_responses.get('work_assignments', {}).items():
            xml_content += f'\n      <{phase.lower().replace(" & ", "_").replace(" ", "_")}>{assignment}</{phase.lower().replace(" & ", "_").replace(" ", "_")}>'
        
        xml_content += f'''
    </work_assignments>
  </user_requirements>

  <photo_resources>
    <shared_album_url>{self.user_responses.get('photo_album_url', '')}</shared_album_url>
    <album_description>{self.user_responses.get('photo_album_description', '')}</album_description>
    <photo_instructions>
      <if_shared_album>If shared album URL is provided above, please access and analyze all photos in the album for detailed site analysis, existing structures, and design elements.</if_shared_album>
      <if_individual_photos>Individual photos will be uploaded with this request showing precise site conditions, measurements, sketches, and reference designs.</if_individual_photos>
    </photo_instructions>
  </photo_resources>

  <local_resources>
    <suppliers>'''
        
        for supplier in local_suppliers.get('suppliers', []):
            xml_content += f'\n      <supplier>{supplier}</supplier>'
        
        xml_content += f'''
    </suppliers>
    <building_codes>
      <jurisdiction>Check local building department for {self.user_responses.get('zip_code', 'your area')}</jurisdiction>
      <permit_likely_required>{self.user_responses.get('height_from_ground', '') != 'Ground level (under 30 inches)'}</permit_likely_required>
    </building_codes>
  </local_resources>

  <deliverables_requested>
    <!-- Basic Planning -->
    <material_list>true</material_list>
    <cost_estimate>true</cost_estimate>
    <step_by_step_instructions>true</step_by_step_instructions>
    <safety_guidelines>true</safety_guidelines>
    <tool_requirements>true</tool_requirements>
    <timeline_estimate>true</timeline_estimate>
    <local_supplier_recommendations>true</local_supplier_recommendations>
    <permit_guidance>true</permit_guidance>
    
    <!-- Advanced Features -->
    <detailed_technical_drawings>true</detailed_technical_drawings>
    <foundation_engineering>true</foundation_engineering>
    <framing_plans>true</framing_plans>
    <comprehensive_cost_breakdown>true</comprehensive_cost_breakdown>
    <professional_coordination_guidance>true</professional_coordination_guidance>
    <project_timeline_with_milestones>true</project_timeline_with_milestones>
    <quality_control_checkpoints>true</quality_control_checkpoints>
    <contingency_planning>true</contingency_planning>
    <roi_analysis>true</roi_analysis>
  </deliverables_requested>

  <context_instructions>
    <role>Act as an experienced deck contractor with engineering knowledge, capable of coordinating with professionals and managing complex projects</role>
    <experience_level>Adapt guidance for {self.user_responses.get('construction_experience', '')} experience level</experience_level>
    <professional_coordination>Provide guidance for working with contractors, engineers, and inspectors as needed</professional_coordination>
    <safety_priority>Comprehensive safety protocols for complex construction with multiple workers</safety_priority>
    <budget_optimization>Detailed cost management within {self.user_responses.get('budget_range', '')} range with variance tracking</budget_optimization>
    <local_focus>Expert knowledge of {local_suppliers.get('area', 'local area')} suppliers, codes, and best practices</local_focus>
    <family_coordination>Advanced coordination strategies for: {self.user_responses.get('helpers_available', 'project team')}</family_coordination>
    <photo_integration>Provide detailed site-specific recommendations based on thorough analysis of provided photos or shared album</photo_integration>
    <response_format>Professional-grade documentation with detailed plans, specifications, and project management guidance</response_format>
  </context_instructions>

  <submission_instructions>
    <photos_to_include>
      <shared_album>If you provided a shared album URL above, reference it in your message to the AI for comprehensive site analysis</shared_album>
      <individual_photos>Upload comprehensive site documentation, structural details, design sketches, and reference materials</individual_photos>
      <technical_requirements>Include any existing plans, surveys, or technical constraints</technical_requirements>
    </photos_to_include>
    
    <additional_context>
      <specific_requirements>Detailed project requirements and performance specifications</specific_requirements>
      <constraints_and_challenges>Site limitations, HOA requirements, neighbor considerations, utility constraints</constraints_and_challenges>
      <professional_involvement>Which aspects require professional consultation or oversight</professional_involvement>
      <long_term_considerations>Future modifications, maintenance planning, resale considerations</long_term_considerations>
    </additional_context>
  </submission_instructions>
</deck_planning_request>'''
        
        return xml_content
    
    def save_template(self, xml_content):
        """Save the generated template to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"deck_plan_request_{timestamp}.xml"
        
        # Archive old template if we're updating
        if self.existing_template:
            archive_name = f"archive_{os.path.basename(self.existing_template)}"
            os.rename(self.existing_template, archive_name)
            print(f"📁 Previous template archived as: {archive_name}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return filename
    
    def display_next_steps(self, filename):
        """Show user what to do next"""
        print("\n🎉 SUCCESS! Your custom deck planning template has been generated!")
        print("=" * 65)
        print(f"📁 Template saved as: {filename}")
        
        if self.existing_template:
            print("✨ Template updated with new features and your previous responses!")
        
        print("\n📋 NEXT STEPS:")
        print("1. 📸 Prepare your visual materials:")
        
        if self.user_responses.get('photo_album_url'):
            print(f"   ✅ Shared album: {self.user_responses['photo_album_url']}")
            print("   • Make sure the album is publicly viewable or shareable")
            print("   • Or take screenshots of key photos to upload directly")
        else:
            print("   • Take photos of your planned deck area (multiple angles)")
            print("   • Create hand-drawn sketches of your desired deck design")
        
        print("2. ✏️  Take measurements or provide dimension estimates")
        print("3. 🤖 Submit the XML template + photos to an LLM:")
        print("   • Claude (claude.ai) - Best for construction guidance")
        print("   • ChatGPT (chat.openai.com) - Great for creative ideas")
        print("   • Other AI assistants")
        print("\n💡 SUBMISSION TIP: Copy the entire XML content and paste it as your")
        print("first message to the AI, then upload photos or mention your shared album.")
        print("\n🏗️ The AI will generate detailed plans, material lists,")
        print("cost estimates, and step-by-step construction guidance!")
        print("=" * 65)
    
    def run(self):
        """Main program flow"""
        try:
            self.welcome_message()
            
            # Check for existing templates
            existing_template = self.detect_existing_templates()
            
            if existing_template:
                should_update = self.handle_existing_template(existing_template)
                if not should_update:
                    print("🆕 Starting fresh template...")
            else:
                print("🆕 Creating new deck planning template...")
            
            # Collect all user requirements (with existing data awareness)
            self.collect_project_basics()
            self.collect_location_details()
            self.collect_diy_vs_professional()
            self.collect_family_resources()
            self.collect_timeline_preferences()
            self.collect_material_preferences()
            self.collect_photo_resources()  # New feature
            
            # Generate and save template
            print("\n🔧 GENERATING YOUR CUSTOM TEMPLATE...")
            xml_content = self.generate_xml_template()
            filename = self.save_template(xml_content)
            
            # Show next steps
            self.display_next_steps(filename)
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Planning session canceled. Your previous template is preserved.")
            print("   Run this script again anytime to continue!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try running the script again.")
            sys.exit(1)

def main():
    """Entry point"""
    planner = DeckPlanner()
    planner.run()

if __name__ == "__main__":
    main()