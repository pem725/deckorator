# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains "deckorator" - a comprehensive deck planning system that provides structured templates and supporting resources for deck construction projects. The system is designed to be family-friendly and adaptable to different skill levels and locations.

## Repository Structure

### Core Templates
- `deck_prompt_basic.xml` - Simplified template for beginners and DIYers
- `deck_prompt_advanced.xml` - Comprehensive template with detailed specifications and professional features
- `family_roles_template.xml` - Framework for coordinating family member involvement and safety

### Supporting Resources
- `material_suppliers_22032.json` - Local supplier database with pricing and contact information
- `seasonal_planning_guide.md` - Optimal timing guidance for Northern Virginia climate
- `location_config.json` - Configuration template for adapting to different regions

## Key Components

### Basic XML Template (`deck_prompt_basic.xml`)
Simplified template designed for family use featuring:
- **Project type selection**: New deck, repair, or expansion options
- **Simple specifications**: Basic dimensions and material preferences  
- **Budget and timeline planning**: Practical ranges and seasonal timing
- **Family-friendly deliverables**: Clear guides, local supplier info, safety tips
- **Beginner-focused context**: Patient explanations and simple language

### Advanced XML Template (`deck_prompt_advanced.xml`)
Comprehensive template for detailed planning including:
- **Local pricing integration**: Zip code 22032 supplier research and comparison
- **Detailed deliverables**: Technical drawings, comprehensive estimates, project tracking
- **Time optimization**: Scheduling for cost minimization and labor availability
- **Professional coordination**: Multi-expert input framework
- **Comprehensive estimates**: ROI analysis, variance tracking, forecasting tools

### Family Coordination System (`family_roles_template.xml`)
Framework for organizing family involvement:
- **Role assignment**: Based on skill level, age, and availability
- **Safety guidelines**: Age-appropriate task assignments and equipment requirements
- **Phase coordination**: Timeline and responsibility tracking across project phases
- **Communication tools**: Progress documentation and coordination recommendations

### Location Support (`location_config.json`)
Configuration system for regional adaptation:
- **Building codes**: Jurisdiction-specific permit and code requirements
- **Climate considerations**: Regional weather patterns and optimal construction windows
- **Supplier networks**: Local availability and market conditions
- **Customization templates**: Examples for different US regions

### Supplier Database (`material_suppliers_22032.json`)
Comprehensive local resource database:
- **Big box stores**: Home Depot, Lowe's locations with distances and specialties
- **Local lumber yards**: Contractor pricing and custom services
- **Specialty suppliers**: Deck-specific materials and design consultation
- **Seasonal pricing**: Cost optimization strategies and timing recommendations

### Planning Guide (`seasonal_planning_guide.md`)
Northern Virginia-specific timing guidance:
- **Monthly breakdown**: Optimal activities and considerations by month
- **Weather planning**: Temperature, precipitation, and seasonal factors
- **Cost optimization**: Pricing patterns and savings opportunities
- **Family coordination**: School calendar and holiday considerations

## Architecture Notes

The system uses a tiered approach to accommodate different user needs:

1. **Skill-based templates**: Basic for beginners, advanced for experienced builders
2. **Local customization**: Region-specific supplier, climate, and code information  
3. **Family coordination**: Role-based task assignment with safety prioritization
4. **Comprehensive planning**: Integration of timing, cost, and resource optimization

### Template Selection Guide
- **Use Basic Template**: First-time deck builders, simple rectangular decks, limited time for planning
- **Use Advanced Template**: Complex designs, multiple levels, professional involvement, detailed cost tracking
- **Family Coordination**: Any project involving multiple family members or varying skill levels

### Customization Workflow
1. Update `location_config.json` with local information
2. Research and update supplier database for your area
3. Adapt seasonal guide for your climate zone
4. Select appropriate template based on project complexity and experience level

This modular structure allows the system to scale from simple DIY projects to complex multi-phase construction while maintaining safety and cost-effectiveness.