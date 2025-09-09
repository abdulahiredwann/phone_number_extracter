#!/usr/bin/env python3
"""
Debug phone number detection with detailed analysis
"""

import phonenumbers
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat
import re

def debug_phone_detection():
    """Debug phone number detection with detailed analysis"""
    
    # Test with the actual text from your logs
    test_texts = [
        ". 421-4567]",
        "421-4567",
        "50-123-4567", 
        "52-234-5678",
        "+972 50-123-4567",
        "+972 52-234-5678"
    ]
    
    print("🔍 Debugging phone number detection...")
    print(f"🌍 Region: IL")
    print()
    
    for text in test_texts:
        print(f"📝 Testing text: '{text}'")
        
        # Test each regex pattern individually
        patterns = [
            (r'\+972\s*[2-9]\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{3,4}', "Full +972 format"),
            (r'0[2-9]\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{3,4}', "0X-XXX-XXXX format"),
            (r'[2-9]\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{3,4}', "X-XXX-XXXX format"),
            (r'[2-9]\d{2,3}[-.\s]?\d{3,4}', "XXX-XXXX format"),
            (r'[2-9]\d{3,4}[-.\s]?\d{3,4}', "XXXX-XXXX format"),
            (r'[2-9]\d{1,4}[-.\s]?\d{3,4}', "Flexible format"),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                raw_number = match.group(0)
                print(f"   🎯 Pattern '{description}' matched: '{raw_number}'")
                
                # Clean the number
                clean_number = re.sub(r'[^\d+]', '', raw_number)
                print(f"   🧹 Cleaned: '{clean_number}'")
                
                if not clean_number.startswith('+'):
                    if clean_number.startswith('0'):
                        clean_number = '+972' + clean_number[1:]
                    else:
                        clean_number = '+972' + clean_number
                
                print(f"   🔢 Final: '{clean_number}'")
                
                try:
                    parsed = phonenumbers.parse(clean_number, "IL")
                    is_possible = phonenumbers.is_possible_number(parsed)
                    is_valid = phonenumbers.is_valid_number(parsed)
                    
                    print(f"   ✅ Possible: {is_possible}, Valid: {is_valid}")
                    
                    if is_valid:
                        e164 = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
                        natl = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
                        print(f"   📞 {e164} ({natl})")
                    else:
                        print(f"   ❌ Invalid number")
                        
                except Exception as e:
                    print(f"   ❌ Parse error: {e}")
                
                print()
        
        print("---")

if __name__ == "__main__":
    debug_phone_detection()
