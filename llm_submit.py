#!/usr/bin/env python3
"""
LLM Submission Helper for Deckorator
Optionally submit generated templates directly to AI services
"""

import json
import os
import sys
import base64
from pathlib import Path

try:
    import requests
except ImportError:
    print("⚠️  Optional: Install 'requests' for direct LLM submission: pip install requests")
    requests = None

class LLMSubmissionHelper:
    def __init__(self):
        self.supported_services = {
            'anthropic': 'Claude (Anthropic)',
            'openai': 'ChatGPT (OpenAI)',
            'manual': 'Manual Copy-Paste'
        }
    
    def welcome(self):
        print("\n🤖 LLM SUBMISSION HELPER")
        print("=" * 30)
        print("This tool helps you submit your generated deck plan to AI services.")
        print("You can either:")
        print("• Get formatted text to copy-paste manually")
        print("• Submit directly via API (requires API keys)")
        print()
    
    def load_template(self):
        """Find and load the most recent template"""
        xml_files = list(Path('.').glob('deck_plan_request_*.xml'))
        
        if not xml_files:
            print("❌ No deck plan templates found!")
            print("   Run 'python deck_planner.py' first to generate a template.")
            return None
        
        # Get the most recent template
        latest_template = max(xml_files, key=os.path.getctime)
        print(f"📁 Found template: {latest_template}")
        
        with open(latest_template, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_photos(self):
        """Get list of photo files"""
        photo_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        photos = []
        
        print("\n📸 PHOTO DETECTION")
        print("-" * 20)
        
        for ext in photo_extensions:
            photos.extend(Path('.').glob(f'*{ext}'))
            photos.extend(Path('.').glob(f'*{ext.upper()}'))
        
        if photos:
            print(f"Found {len(photos)} photo files:")
            for photo in photos[:10]:  # Show first 10
                print(f"  • {photo}")
            if len(photos) > 10:
                print(f"  ... and {len(photos) - 10} more")
        else:
            print("No photo files found in current directory.")
            print("💡 TIP: Place your site photos in the same folder as the script.")
        
        return photos
    
    def format_for_manual_submission(self, template_content, photos):
        """Format content for manual copy-paste"""
        submission_text = f"""I need help creating detailed deck construction plans. Here's my project information:

{template_content}

PHOTOS INCLUDED:
"""
        if photos:
            submission_text += f"I'm uploading {len(photos)} photos showing:\n"
            submission_text += "• Site conditions and planned deck area\n"
            submission_text += "• Current house attachment point\n"
            submission_text += "• Ground conditions and obstacles\n"
            submission_text += "• Any reference designs or sketches\n\n"
        else:
            submission_text += "No photos uploaded yet - I'll add them after submitting this template.\n\n"
        
        submission_text += """PLEASE PROVIDE:
• Detailed construction plans and step-by-step instructions
• Complete material lists with quantities
• Cost estimates for my local area
• Safety guidelines appropriate for my skill level
• Permit and code compliance guidance
• Tool requirements and rental recommendations

Thank you for your detailed assistance with this deck project!"""
        
        return submission_text
    
    def save_submission_text(self, formatted_text):
        """Save formatted text to file"""
        filename = "deck_submission_text.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        return filename
    
    def submit_to_anthropic(self, template_content, photos, api_key):
        """Submit to Claude via Anthropic API"""
        if not requests:
            print("❌ 'requests' library not installed. Use manual submission instead.")
            return False
        
        print("🔄 Submitting to Claude...")
        
        # Prepare the message
        message_content = [
            {
                "type": "text",
                "text": f"I need help creating detailed deck construction plans. Here's my project information:\n\n{template_content}"
            }
        ]
        
        # Add photos if available
        for photo in photos[:5]:  # Limit to 5 photos
            try:
                with open(photo, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                    message_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": f"image/{photo.suffix[1:]}",
                            "data": image_data
                        }
                    })
            except Exception as e:
                print(f"⚠️  Couldn't process {photo}: {e}")
        
        # API request
        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': api_key,
                    'anthropic-version': '2023-06-01'
                },
                json={
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 4000,
                    'messages': [
                        {
                            'role': 'user',
                            'content': message_content
                        }
                    ]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Submission failed: {e}")
            return False
    
    def get_api_key(self, service):
        """Get API key from user or environment"""
        env_vars = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY'
        }
        
        # Check environment variable first
        if service in env_vars:
            api_key = os.getenv(env_vars[service])
            if api_key:
                print(f"✅ Found API key in environment variable {env_vars[service]}")
                return api_key
        
        # Ask user for API key
        print(f"\n🔑 API KEY REQUIRED for {self.supported_services[service]}")
        print("You can:")
        print("1. Enter your API key now (secure - not saved)")
        print(f"2. Set environment variable {env_vars[service]} and restart")
        print("3. Use manual submission instead")
        
        choice = input("\nEnter API key or press Enter for manual submission: ").strip()
        
        if choice:
            return choice
        else:
            return None
    
    def choose_submission_method(self):
        """Let user choose how to submit"""
        print("\n📤 SUBMISSION METHOD")
        print("-" * 20)
        print("1. Manual copy-paste (recommended for first time)")
        print("2. Direct API submission to Claude")
        print("3. Direct API submission to ChatGPT") 
        
        while True:
            try:
                choice = int(input("\nChoose method (1-3): "))
                if choice == 1:
                    return 'manual'
                elif choice == 2:
                    return 'anthropic'
                elif choice == 3:
                    return 'openai'
                else:
                    print("❌ Please enter 1, 2, or 3")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def run(self):
        """Main execution flow"""
        self.welcome()
        
        # Load template
        template_content = self.load_template()
        if not template_content:
            return
        
        # Detect photos
        photos = self.get_photos()
        
        # Choose submission method
        method = self.choose_submission_method()
        
        if method == 'manual':
            # Format for manual submission
            formatted_text = self.format_for_manual_submission(template_content, photos)
            filename = self.save_submission_text(formatted_text)
            
            print(f"\n✅ SUCCESS!")
            print(f"📁 Submission text saved to: {filename}")
            print("\n📋 NEXT STEPS:")
            print("1. Open the saved file and copy the entire content")
            print("2. Go to claude.ai, chat.openai.com, or your preferred AI")
            print("3. Paste the content as your first message")
            print("4. Upload your photos (drag and drop)")
            print("5. Send the message and get your detailed deck plans!")
            
        elif method in ['anthropic', 'openai']:
            # API submission
            api_key = self.get_api_key(method)
            
            if not api_key:
                print("\n💡 Falling back to manual submission...")
                formatted_text = self.format_for_manual_submission(template_content, photos)
                filename = self.save_submission_text(formatted_text)
                print(f"📁 Submission text saved to: {filename}")
            else:
                if method == 'anthropic':
                    result = self.submit_to_anthropic(template_content, photos, api_key)
                    if result:
                        print("\n✅ SUCCESS! Claude responded:")
                        print("=" * 50)
                        print(result[:1000] + "..." if len(result) > 1000 else result)
                        print("=" * 50)
                        
                        # Save full response
                        with open('claude_deck_plans.txt', 'w', encoding='utf-8') as f:
                            f.write(result)
                        print("\n📁 Full response saved to: claude_deck_plans.txt")
                    else:
                        print("❌ API submission failed. Try manual submission instead.")
                else:  # OpenAI
                    print("🚧 OpenAI integration coming soon! Using manual submission...")
                    formatted_text = self.format_for_manual_submission(template_content, photos)
                    filename = self.save_submission_text(formatted_text)
                    print(f"📁 Submission text saved to: {filename}")

def main():
    helper = LLMSubmissionHelper()
    try:
        helper.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Submission cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Try manual submission instead.")

if __name__ == "__main__":
    main()