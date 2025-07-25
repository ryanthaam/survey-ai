#!/usr/bin/env python3
"""
Quick test script to demonstrate the AI Chat Assistant functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ai_assistant import AIAnalysisAssistant
import json

def test_ai_assistant():
    """Test the AI assistant with sample data"""
    
    # Sample analysis results (like what you'd get from real analysis)
    sample_results = {
        'total_responses': 10,
        'clusters': {
            0: [
                "Great customer service team was very helpful",
                "Customer support responded quickly to my inquiry",
                "Staff was knowledgeable and professional"
            ],
            1: [
                "Wait time on phone was too long",
                "Had to wait 15 minutes before speaking to someone"
            ],
            2: [
                "Website interface is confusing and hard to navigate",
                "Checkout process has too many steps",
                "Website needs to be simplified"
            ],
            3: [
                "Product quality is excellent and materials feel premium",
                "Construction is solid and well-made"
            ],
            4: [
                "Pricing seems high compared to competitors",
                "Found similar products elsewhere for 20-30% less"
            ]
        },
        'summaries': {
            0: "Customer service receives positive feedback for helpfulness and responsiveness",
            1: "Wait times are a significant pain point for customer service",
            2: "Website usability issues affecting customer experience", 
            3: "Product quality praised for materials and construction",
            4: "Pricing concerns with competitive disadvantage"
        },
        'sentiments': {
            0: {'sentiment': 'positive', 'confidence': 0.89},
            1: {'sentiment': 'negative', 'confidence': 0.78},
            2: {'sentiment': 'negative', 'confidence': 0.85},
            3: {'sentiment': 'positive', 'confidence': 0.92},
            4: {'sentiment': 'negative', 'confidence': 0.74}
        }
    }
    
    # Initialize AI Assistant
    assistant = AIAnalysisAssistant()
    
    # Test sample questions
    test_questions = [
        "What are the main problems customers are facing?",
        "Which areas are customers most satisfied with?",
        "What should we prioritize for improvement?",
        "How do customers feel about our pricing?"
    ]
    
    print("🤖 AI Chat Assistant Demo")
    print("=" * 50)
    
    # Set the analysis context
    assistant.analysis_context = sample_results
    
    for question in test_questions:
        print(f"\n👤 User: {question}")
        
        try:
            # Generate AI response
            response = assistant._generate_ai_response(question)
            print(f"🤖 AI: {response}")
        except Exception as e:
            print(f"🤖 AI: I need an OpenAI API key to provide intelligent responses. Error: {str(e)}")
            print("🤖 AI: [Demo Mode] Based on the analysis, I can see customers are having issues with wait times and website navigation, but love the product quality and customer service helpfulness.")
        
        print("-" * 30)
    
    print("\n✨ This is how the AI assistant works in the main application!")
    print("📝 It analyzes your actual survey data and provides intelligent business insights.")

if __name__ == "__main__":
    test_ai_assistant()