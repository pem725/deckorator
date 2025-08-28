#!/usr/bin/env python3
"""
Deckorator - Construction-Focused Deck Planning System
Generates XML templates that produce actual construction specifications, not just rehashed inputs.
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

class ConstructionDeckPlanner:
    def __init__(self):
        self.user_responses = {}
        self.suppliers_db = {}
        self.existing_template = None
        self.template_version = "3.0"  # Construction-focused version
        self.load_suppliers_database()
        
    def load_suppliers_database(self):
        """Load supplier database or create default"""
        try:
            with open('suppliers_database.json', 'r') as f:
                self.suppliers_db = json.load(f)
        except FileNotFoundError:
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
        print("🏗️  DECKORATOR - Construction Planning System v3.0")
        print("=" * 60)
        print("This system generates CONSTRUCTION SPECIFICATIONS, not summaries.")
        print("You will receive:")
        print("• Grading requirements and drainage analysis")
        print("• Exact footer locations, depths, and spacing")
        print("• Detailed framing plans with code compliance") 
        print("• Competitive bidding material lists with quantities")
        print("• Project timeline with Gantt chart format")
        print("• Actual buildable construction documentation")
        print("\n" + "=" * 60 + "\n")
    
    def collect_precise_measurements(self):
        """Collect exact measurements for calculations"""
        print("\n📏 PRECISE MEASUREMENTS (Required for Calculations)")
        print("-" * 50)
        print("The AI needs exact dimensions to calculate footers, spans, materials.")
        
        while True:
            try:
                length = float(input("Deck length (feet): "))
                width = float(input("Deck width (feet): "))
                break
            except ValueError:
                print("❌ Please enter numbers only (e.g., 12.5)")
        
        self.user_responses['exact_length'] = length
        self.user_responses['exact_width'] = width
        self.user_responses['total_area'] = length * width
        
        # Height from ground for structural calculations
        while True:
            try:
                height = float(input("Height from ground to deck surface (inches): "))
                break
            except ValueError:
                print("❌ Please enter height in inches (e.g., 30)")
        
        self.user_responses['deck_height_inches'] = height
        
        # House attachment details for ledger calculations
        attachment = input("How does deck attach to house? (ledger/freestanding): ").lower()
        self.user_responses['attachment_method'] = attachment
        
        if 'ledger' in attachment:
            # Get ledger attachment details
            self.user_responses['ledger_height'] = input("Height of ledger attachment point from ground (inches): ")
            self.user_responses['house_construction'] = input("House construction (wood frame/brick/concrete): ")
    
    def collect_soil_and_drainage(self):
        """Collect soil and drainage information for grading analysis"""
        print("\n🌍 SOIL & DRAINAGE ANALYSIS")
        print("-" * 30)
        
        # Slope measurements
        print("Measure the ground slope under your planned deck:")
        slope_direction = input("Primary slope direction (north/south/east/west/level): ")
        self.user_responses['slope_direction'] = slope_direction
        
        if slope_direction.lower() != 'level':
            while True:
                try:
                    slope_inches = float(input(f"Slope amount over deck length - how many inches higher is the {slope_direction} side? "))
                    break
                except ValueError:
                    print("❌ Enter slope in inches (e.g., 6 for 6 inch slope)")
            
            self.user_responses['slope_amount_inches'] = slope_inches
            self.user_responses['slope_percentage'] = (slope_inches / (self.user_responses['exact_length'] * 12)) * 100
        
        # Soil type for footer depth calculations
        soil_type = input("Soil type (clay/sand/loam/rocky/unknown): ")
        self.user_responses['soil_type'] = soil_type
        
        # Drainage issues
        drainage_issues = input("Any drainage problems? (water pooling/wet areas/none): ")
        self.user_responses['drainage_issues'] = drainage_issues
        
        # Proximity to foundation for drainage requirements
        foundation_distance = input("Distance from house foundation (feet): ")
        self.user_responses['foundation_distance'] = foundation_distance
    
    def collect_construction_parameters(self):
        """Collect parameters for construction calculations"""
        print("\n🔨 CONSTRUCTION PARAMETERS")
        print("-" * 30)
        
        # Load requirements based on intended use
        intended_use = input("Primary deck use (dining/hot tub/storage/general): ")
        self.user_responses['intended_use'] = intended_use
        
        # Material selection affects spacing calculations
        joist_material = input("Joist material (2x8 PT/2x10 PT/2x12 PT/engineered): ")
        self.user_responses['joist_material'] = joist_material
        
        decking_material = input("Decking material (5/4x6 PT/composite/2x6 PT): ")
        self.user_responses['decking_material'] = decking_material
        
        # Local code requirements
        self.user_responses['zip_code'] = input("Zip code (for local codes): ")
        
        # Timeline constraints for Gantt chart
        start_date = input("Planned start date (YYYY-MM-DD): ")
        self.user_responses['start_date'] = start_date
        
        # Equipment available
        self.user_responses['has_excavator'] = input("Will rent excavator? (yes/no): ").lower() == 'yes'
        self.user_responses['concrete_subcontract'] = input("Subcontract concrete? (yes/no): ").lower() == 'yes'
    
    def collect_photo_resources(self):
        """Collect photo album URLs for site analysis"""
        print("\n📸 SITE PHOTOS FOR ANALYSIS")
        print("-" * 30)
        
        album_url = input("Photo album URL (or press Enter if none): ").strip()
        if album_url:
            if not album_url.startswith('http'):
                album_url = 'https://' + album_url
            self.user_responses['photo_album_url'] = album_url
            self.user_responses['photo_album_description'] = input("What do the photos show? ")
        else:
            self.user_responses['photo_album_url'] = ""
            self.user_responses['photo_album_description'] = "Individual photos will be uploaded"
    
    def generate_construction_xml(self):
        """Generate XML focused on construction specifications"""
        local_suppliers = self.suppliers_db.get(self.user_responses['zip_code'], self.suppliers_db['default'])
        
        # Calculate derived values
        joist_spacing = self.calculate_joist_spacing()
        footer_layout = self.calculate_footer_layout()
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<construction_specification_request>
  <project_overview>
    <description>Generate actual construction specifications and working drawings</description>
    <template_version>{self.template_version}</template_version>
    <generated_date>{datetime.now().strftime('%Y-%m-%d')}</generated_date>
    <focus>Construction documentation, not input summary</focus>
  </project_overview>

  <site_specifications>
    <dimensions>
      <length_feet>{self.user_responses['exact_length']}</length_feet>
      <width_feet>{self.user_responses['exact_width']}</width_feet>
      <total_square_feet>{self.user_responses['total_area']}</total_square_feet>
      <height_above_ground_inches>{self.user_responses['deck_height_inches']}</height_above_ground_inches>
    </dimensions>
    
    <site_conditions>
      <slope_direction>{self.user_responses['slope_direction']}</slope_direction>
      <slope_amount_inches>{self.user_responses.get('slope_amount_inches', 0)}</slope_amount_inches>
      <slope_percentage>{self.user_responses.get('slope_percentage', 0):.2f}%</slope_percentage>
      <soil_type>{self.user_responses['soil_type']}</soil_type>
      <drainage_issues>{self.user_responses['drainage_issues']}</drainage_issues>
      <distance_from_foundation_feet>{self.user_responses['foundation_distance']}</distance_from_foundation_feet>
    </site_conditions>

    <attachment_details>
      <method>{self.user_responses['attachment_method']}</method>
      <ledger_height_inches>{self.user_responses.get('ledger_height', 'N/A')}</ledger_height_inches>
      <house_construction>{self.user_responses.get('house_construction', 'N/A')}</house_construction>
    </attachment_details>
  </site_specifications>

  <structural_requirements>
    <intended_load>{self.user_responses['intended_use']}</intended_load>
    <joist_material>{self.user_responses['joist_material']}</joist_material>
    <decking_material>{self.user_responses['decking_material']}</decking_material>
    <calculated_joist_spacing>{joist_spacing}</calculated_joist_spacing>
    <footer_layout>{footer_layout}</footer_layout>
  </structural_requirements>

  <photo_resources>
    <album_url>{self.user_responses['photo_album_url']}</album_url>
    <album_description>{self.user_responses['photo_album_description']}</album_description>
  </photo_resources>

  <local_compliance>
    <jurisdiction>Building department for {self.user_responses['zip_code']}</jurisdiction>
    <code_reference>https://www.fairfaxcounty.gov/landdevelopment/sites/landdevelopment/files/assets/documents/pdf/publications/deck-details.pdf</code_reference>
    <permit_required>{self.user_responses['deck_height_inches'] > 30}</permit_required>
  </local_compliance>

  <construction_timeline>
    <start_date>{self.user_responses['start_date']}</start_date>
    <equipment_rental_needed>{self.user_responses['has_excavator']}</equipment_rental_needed>
    <subcontracted_work>{"Concrete pours" if self.user_responses['concrete_subcontract'] else "None"}</subcontracted_work>
  </construction_timeline>

  <required_deliverables>
    <!-- CRITICAL: These are SPECIFICATIONS, not input summaries -->
    <grading_analysis>
      <requirement>Analyze photos and site conditions to specify exact grading requirements</requirement>
      <deliverable>Specific grading plan with cut/fill requirements, drainage solutions, and slope corrections needed for proper water runoff</deliverable>
      <focus>Address drainage from east side of house and overall site water management</focus>
    </grading_analysis>
    
    <foundation_plan>
      <requirement>Calculate exact footer specifications based on dimensions, soil, and loads</requirement>
      <deliverable>
        - Exact number of footers required
        - Precise hole locations with measurements from reference points  
        - Hole depths based on frost line and soil conditions
        - Footer spacing calculations per IRC and local codes
        - Concrete specifications and quantities per hole
      </deliverable>
      <calculations_needed>Use actual dimensions: {self.user_responses['exact_length']}' x {self.user_responses['exact_width']}'</calculations_needed>
    </foundation_plan>
    
    <framing_specifications>
      <requirement>Design framing system that complies with local building codes</requirement>
      <deliverable>
        - Detailed framing sketch with measurements
        - Joist spacing calculations for {self.user_responses['joist_material']} and {self.user_responses['decking_material']}
        - Beam sizing and span calculations
        - Connection details and hardware specifications
        - Code compliance verification against Fairfax County requirements
      </deliverable>
      <reference_codes>Use linked PDF: deck-details.pdf for compliance verification</reference_codes>
    </framing_specifications>
    
    <material_specifications>
      <requirement>Generate competitive bidding material list with exact quantities</requirement>
      <deliverable>
        - Itemized list with quantities, sizes, and specifications
        - Format suitable for sending to multiple suppliers
        - Include lumber, hardware, concrete, and finishing materials  
        - Separate sections for: Structural, Decking, Railings, Hardware
        - 10% waste factor included in calculations
      </deliverable>
      <suppliers_for_pricing>{local_suppliers.get('suppliers', ['Local suppliers'])}</suppliers_for_pricing>
    </material_specifications>
    
    <project_timeline>
      <requirement>Create realistic timeline with resource optimization</requirement>
      <deliverable>
        - Phase-by-phase timeline starting from {self.user_responses['start_date']}
        - Gantt chart format showing task dependencies
        - Equipment rental scheduling (excavator timing)
        - Subcontractor coordination (concrete pours)
        - Weather considerations and backup dates
        - Resource utilization optimization
      </deliverable>
      <constraints>Excavator rental available, concrete subcontracted</constraints>
    </project_timeline>
  </required_deliverables>

  <ai_instructions>
    <primary_directive>GENERATE CONSTRUCTION SPECIFICATIONS, NOT INPUT SUMMARIES</primary_directive>
    <analysis_requirements>
      <photos>Analyze provided photos to determine actual site conditions, existing grades, drainage patterns</photos>
      <calculations>Perform engineering calculations based on provided dimensions and conditions</calculations>
      <code_compliance>Reference Fairfax County deck details PDF for specific compliance requirements</code_compliance>
      <practical_construction>Focus on buildable specifications that a contractor could execute</practical_construction>
    </analysis_requirements>
    <output_format>
      <structure>Organize as: 1) Grading Plan, 2) Foundation Specifications, 3) Framing Plans, 4) Material Lists, 5) Construction Timeline</structure>
      <detail_level>Specific measurements, quantities, and step-by-step procedures</detail_level>
      <professional_quality>Construction-ready documentation suitable for permits and building</professional_quality>
    </output_format>
  </ai_instructions>

  <submission_notes>
    <critical>This template is designed to generate ACTUAL CONSTRUCTION SPECIFICATIONS</critical>
    <photos>Upload photos showing: current site conditions, ground slope, house attachment point, drainage patterns</photos>
    <expectations>You should receive: detailed construction plans, not a summary of what you told the AI</expectations>
  </submission_notes>
</construction_specification_request>'''
        
        return xml_content
    
    def calculate_joist_spacing(self):
        """Calculate appropriate joist spacing based on materials and span"""
        # This is a simplified calculation - the AI will do the detailed work
        material = self.user_responses.get('joist_material', '').lower()
        span = self.user_responses['exact_width']  # Assuming joists span the width
        
        if '2x8' in material and span <= 12:
            return "16 inches on center"
        elif '2x10' in material and span <= 16:
            return "16 inches on center"
        elif '2x12' in material:
            return "16 inches on center"
        else:
            return "Requires engineering calculation based on span and load"
    
    def calculate_footer_layout(self):
        """Provide basic footer layout info for AI to expand"""
        length = self.user_responses['exact_length']
        width = self.user_responses['exact_width']
        
        # Basic layout - AI will provide exact specifications
        if length <= 12 and width <= 12:
            return "4-footer minimum layout, corner and mid-span positions"
        elif length <= 16 and width <= 16:
            return "6-footer layout with intermediate supports"
        else:
            return "8+ footer layout requiring engineering calculations"
    
    def save_template(self, xml_content):
        """Save the generated template to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"construction_specs_request_{timestamp}.xml"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return filename
    
    def display_next_steps(self, filename):
        """Show user what to do next"""
        print("\n🎉 CONSTRUCTION SPECIFICATION REQUEST GENERATED!")
        print("=" * 55)
        print(f"📁 Template saved as: {filename}")
        print("\n🏗️ THIS TEMPLATE GENERATES ACTUAL CONSTRUCTION SPECS:")
        print("• Grading requirements and drainage solutions")
        print("• Exact footer locations, depths, and spacing")
        print("• Detailed framing plans with code compliance")
        print("• Competitive bidding material lists")
        print("• Project timeline with Gantt chart")
        
        print("\n📋 NEXT STEPS:")
        print("1. 📸 Take detailed site photos showing:")
        print("   • Current ground conditions and slope")
        print("   • House attachment point")
        print("   • Drainage patterns and problem areas")
        print("   • Any obstacles or utilities")
        
        if self.user_responses.get('photo_album_url'):
            print(f"   ✅ Your shared album: {self.user_responses['photo_album_url']}")
        
        print("\n2. 🤖 Submit to AI with template + photos")
        print("3. 📐 Receive ACTUAL CONSTRUCTION SPECIFICATIONS")
        print("4. 🏗️ Build your deck with professional documentation!")
        print("=" * 55)
    
    def run(self):
        """Main program flow"""
        try:
            self.welcome_message()
            
            print("🎯 This system generates CONSTRUCTION SPECIFICATIONS.")
            print("You will NOT get a summary of your inputs.")
            print("You WILL get actual building plans, material lists, and timelines.\n")
            
            # Collect construction-focused data
            self.collect_precise_measurements()
            self.collect_soil_and_drainage()
            self.collect_construction_parameters()
            self.collect_photo_resources()
            
            # Generate construction-focused template
            print("\n🔧 GENERATING CONSTRUCTION SPECIFICATION REQUEST...")
            xml_content = self.generate_construction_xml()
            filename = self.save_template(xml_content)
            
            # Show next steps
            self.display_next_steps(filename)
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Planning session canceled.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try running the script again.")
            sys.exit(1)

def main():
    """Entry point"""
    planner = ConstructionDeckPlanner()
    planner.run()

if __name__ == "__main__":
    main()