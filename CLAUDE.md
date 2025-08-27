# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains "deckorator" - a deck addition planning project that uses structured XML prompts to guide comprehensive deck construction planning and execution.

## Repository Structure

The project is currently minimal with a single XML template file:

- `deck_prompt_skeleton.xml` - The core XML template that defines the structure for deck addition project planning

## Key Components

### XML Prompt Template (`deck_prompt_skeleton.xml`)

This is the main architectural component that provides a structured framework for:

- **Project specifications**: Dimensions, materials, and foundation requirements
- **Site conditions**: Terrain, existing structures, utilities, and access considerations  
- **Professional team integration**: Framework for incorporating up to 3 professionals with expertise and links
- **Deliverables management**: Structured requests for material lists, cut lists, cost estimates, step-by-step instructions, safety considerations, plan interpretation, and code compliance notes
- **Constraint handling**: Budget, skill level, available tools, and time considerations
- **Context instructions**: Role definition as deck contractor/advisor with Fairfax County building code integration

### Key Features

- **Plan Analysis Integration**: Designed to work with uploaded hand-drawn plans
- **Local Code Compliance**: Built-in reference to Fairfax County deck requirements
- **Multi-professional Input**: Structured framework for integrating multiple expert perspectives
- **Comprehensive Deliverables**: Complete project planning from materials to safety considerations

## Architecture Notes

The XML template uses a hierarchical structure that mirrors typical construction project planning workflows:
1. Project overview and scope definition
2. Technical specifications and materials
3. Site assessment and conditions
4. Team collaboration framework  
5. Deliverable requirements and constraints
6. Contextual guidance for AI assistant behavior

This structure allows for systematic project planning while maintaining flexibility for different project types and scales.