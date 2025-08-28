#!/usr/bin/env python3
"""
Deckorator - Interactive Deck Planning System
Generates custom XML templates for LLM processing based on user requirements.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

class DeckPlanner:
    def __init__(self):
        self.user_responses = {}
        self.suppliers_db = {}
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
    
    def welcome_message(self):
        """Display welcome and instructions"""
        print("🏗️  DECKORATOR - Interactive Deck Planning System")
        print("=" * 55)
        print("This tool creates a custom deck planning template that you can")
        print("submit to an LLM (like Claude or ChatGPT) along with:")
        print("• Photos of your planned deck area")
        print("• Hand-drawn sketches of desired design") 
        print("• Precise measurements or estimates")
        print("• Material preferences")
        print("\nThe LLM will then generate detailed construction plans,")
        print("material lists, cost estimates, and step-by-step instructions.")
        print("\n" + "=" * 55 + "\n")
    
    def get_user_input(self, prompt, options=None, input_type="text"):
        """Get validated user input"""
        while True:
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
    
    def collect_project_basics(self):
        """Collect basic project information"""
        print("\n📋 PROJECT BASICS")
        print("-" * 20)
        
        self.user_responses['project_type'] = self.get_user_input(
            "What type of deck project is this?",
            ["New deck construction", "Deck repair/renovation", "Deck expansion/addition"]
        )
        
        self.user_responses['complexity'] = self.get_user_input(
            "What level of planning detail do you need?",
            ["Basic (simple rectangular deck, first-time builder)", 
             "Advanced (complex design, multiple levels, professional coordination)"]
        )
        
        self.user_responses['zip_code'] = self.get_user_input(
            "What's your zip code? (for local supplier recommendations)"
        )
        
        # Estimate project size
        self.user_responses['deck_size'] = self.get_user_input(
            "Approximate deck size?",
            ["Small (under 200 sq ft)", "Medium (200-400 sq ft)", "Large (400+ sq ft)"]
        )
        
        self.user_responses['budget_range'] = self.get_user_input(
            "What's your budget range?",
            ["Under $5,000", "$5,000 - $10,000", "$10,000 - $20,000", "Over $20,000"]
        )
    
    def collect_location_details(self):
        """Collect location and site information"""
        print("\n🏠 LOCATION & SITE")
        print("-" * 20)
        
        self.user_responses['attachment_type'] = self.get_user_input(
            "How will the deck attach to your house?",
            ["Attached to house (ledger board)", "Freestanding deck", "Not sure - need advice"]
        )
        
        self.user_responses['ground_conditions'] = self.get_user_input(
            "Describe your ground conditions:",
            ["Level ground", "Slight slope", "Steep slope", "Very uneven terrain"]
        )
        
        self.user_responses['height_from_ground'] = self.get_user_input(
            "How high off the ground will the deck be?",
            ["Ground level (under 30 inches)", "Standard height (30 inches - 6 feet)", 
             "High deck (over 6 feet)", "Not sure - need calculations"]
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
        
        self.user_responses['work_assignments'] = {}
        
        for phase, description in phases:
            print(f"\n{phase}: {description}")
            choice = self.get_user_input(
                f"Your plan for {phase}",
                ["I'll do it myself (DIY)", "Family/friends will help", 
                 "Hire professionals", "Not sure - need advice"]
            )
            self.user_responses['work_assignments'][phase] = choice
    
    def collect_family_resources(self):
        """Collect information about available family help"""
        print("\n👨‍👩‍👧‍👦 FAMILY & HELPER RESOURCES")
        print("-" * 35)
        
        self.user_responses['primary_builder'] = self.get_user_input(
            "Who is the primary person managing this project?"
        )
        
        self.user_responses['construction_experience'] = self.get_user_input(
            "What's your construction experience level?",
            ["Complete beginner", "Some DIY experience", 
             "Experienced DIYer", "Professional background"]
        )
        
        helpers_available = self.get_user_input(
            "Do you have helpers available?",
            ["Just me (solo project)", "Spouse/partner available", 
             "Family members can help", "Friends/neighbors will help", 
             "Multiple helpers available"]
        )
        self.user_responses['helpers_available'] = helpers_available
        
        if "help" in helpers_available.lower():
            self.user_responses['helper_details'] = self.get_user_input(
                "Describe your helpers (ages, experience levels, availability)"
            )
    
    def collect_timeline_preferences(self):
        """Collect timing and schedule preferences"""
        print("\n🗓️ TIMELINE & SCHEDULING")
        print("-" * 25)
        
        self.user_responses['start_timeframe'] = self.get_user_input(
            "When do you want to start construction?",
            ["As soon as possible", "Next month", "This spring", 
             "This summer", "This fall", "Next year"]
        )
        
        self.user_responses['work_schedule'] = self.get_user_input(
            "When can you work on the project?",
            ["Weekends only", "Evenings and weekends", 
             "Flexible schedule", "Full-time dedication"]
        )
        
        self.user_responses['completion_timeline'] = self.get_user_input(
            "How quickly do you want to complete it?",
            ["Take my time (2-3 months)", "Moderate pace (1 month)", 
             "Fast completion (2-3 weeks)", "As quick as possible"]
        )
    
    def collect_material_preferences(self):
        """Collect material and design preferences"""
        print("\n🪵 MATERIALS & DESIGN PREFERENCES")
        print("-" * 35)
        
        self.user_responses['decking_material'] = self.get_user_input(
            "What decking material do you prefer?",
            ["Pressure-treated lumber (economical)", "Cedar (natural, premium)", 
             "Composite decking (low maintenance)", "Not sure - need recommendations"]
        )
        
        self.user_responses['railing_style'] = self.get_user_input(
            "What railing style do you want?",
            ["Simple wood railings", "Decorative balusters", 
             "Cable railings (modern)", "Glass panels (premium)", 
             "Not sure - need ideas"]
        )
        
        self.user_responses['special_features'] = self.get_user_input(
            "Any special features desired?",
            ["Just basic deck", "Built-in seating", "Lighting", 
             "Multiple levels", "Pergola/shade structure", 
             "Outdoor kitchen prep", "Multiple features"]
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
    <description>Custom deck planning request generated by Deckorator system</description>
    <project_type>{self.user_responses.get('project_type', '')}</project_type>
    <complexity_level>basic</complexity_level>
    <generated_date>{datetime.now().strftime('%Y-%m-%d')}</generated_date>
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
    <response_format>Provide organized sections with clear headings, actionable steps, and safety callouts appropriate for the user's experience level</response_format>
  </context_instructions>

  <submission_instructions>
    <photos_to_include>
      <site_photos>Wide-angle shots of the planned deck area from multiple angles</site_photos>
      <detail_photos>Close-ups of house attachment point, ground conditions, obstacles</detail_photos>
      <reference_photos>Any inspiration photos or similar decks you like</reference_photos>
    </photos_to_include>
    
    <sketches_to_include>
      <hand_drawn_plans>Your rough sketch of desired deck layout and dimensions</hand_drawn_plans>
      <measurements>Include any measurements you've taken or estimates of key dimensions</measurements>
    </sketches_to_include>

    <additional_context>
      <specific_questions>List any specific questions or concerns you have about the project</specific_questions>
      <constraints>Mention any HOA requirements, neighbor considerations, or site limitations</constraints>
    </additional_context>
  </submission_instructions>
</deck_planning_request>'''
        
        return xml_content
    
    def generate_advanced_template(self):
        """Generate advanced template XML with more detailed requirements"""
        # Similar to basic but with additional sections for professional coordination,
        # detailed cost tracking, multi-phase planning, etc.
        local_suppliers = self.get_local_suppliers(self.user_responses['zip_code'])
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<deck_planning_request>
  <project_overview>
    <description>Advanced deck planning request with professional coordination capabilities</description>
    <project_type>{self.user_responses.get('project_type', '')}</project_type>
    <complexity_level>advanced</complexity_level>
    <generated_date>{datetime.now().strftime('%Y-%m-%d')}</generated_date>
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
    <response_format>Professional-grade documentation with detailed plans, specifications, and project management guidance</response_format>
  </context_instructions>

  <submission_instructions>
    <photos_to_include>
      <site_photos>Comprehensive site documentation from multiple angles and elevations</site_photos>
      <detail_photos>Close-ups of structural attachment points, utilities, grade conditions</detail_photos>
      <reference_photos>Design inspiration and similar projects for style guidance</reference_photos>
      <existing_structure>Current conditions that will be modified or integrated</existing_structure>
    </photos_to_include>
    
    <sketches_to_include>
      <detailed_plans>Scaled drawings with dimensions and elevation views</detailed_plans>
      <site_measurements>Precise measurements of key dimensions and constraints</site_measurements>
      <design_details>Specific features, connections, and architectural elements desired</design_details>
    </sketches_to_include>

    <additional_context>
      <specific_requirements>Detailed project requirements and performance specifications</specific_requirements>
      <constraints_and_challenges>Site limitations, HOA requirements, neighbor considerations</constraints_and_challenges>
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
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return filename
    
    def display_next_steps(self, filename):
        """Show user what to do next"""
        print("\n🎉 SUCCESS! Your custom deck planning template has been generated!")
        print("=" * 60)
        print(f"📁 Template saved as: {filename}")
        print("\n📋 NEXT STEPS:")
        print("1. 📸 Take photos of your planned deck area (multiple angles)")
        print("2. ✏️  Create hand-drawn sketches of your desired deck design")
        print("3. 📏 Take measurements or provide dimension estimates")
        print("4. 🤖 Submit the XML template + photos + sketches to an LLM:")
        print("   • Claude (claude.ai)")
        print("   • ChatGPT (chat.openai.com)")
        print("   • Other AI assistants")
        print("\n💡 TIP: Copy the entire XML content and paste it as your first")
        print("message to the AI, then upload your photos and sketches.")
        print("\n🏗️ The AI will generate detailed plans, material lists,")
        print("cost estimates, and step-by-step construction guidance!")
        print("=" * 60)
    
    def run(self):
        """Main program flow"""
        try:
            self.welcome_message()
            
            # Collect all user requirements
            self.collect_project_basics()
            self.collect_location_details()
            self.collect_diy_vs_professional()
            self.collect_family_resources()
            self.collect_timeline_preferences()
            self.collect_material_preferences()
            
            # Generate and save template
            print("\n🔧 GENERATING YOUR CUSTOM TEMPLATE...")
            xml_content = self.generate_xml_template()
            filename = self.save_template(xml_content)
            
            # Show next steps
            self.display_next_steps(filename)
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Planning session canceled. You can run this again anytime!")
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