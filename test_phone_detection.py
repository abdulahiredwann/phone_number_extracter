#!/usr/bin/env python3
"""
Test script to debug phone number detection
"""

import phonenumbers
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat

def test_phone_detection():
    """Test phone number detection with Israeli numbers"""
    
    # Test text with Israeli phone numbers
    test_text = """
    +972 50-123-4567
    +972 52-234-5678
    +972 53-345-6789
    +972 54-456-7890
    +972 55-567-8901
    +972 58-678-9012
    +972 59-789-0123
    +972 2-123-4567
    +972 3-234-5678
    +972 4-345-6789
    +972 8-456-7890
    +972 9-567-8901
    +972 77-678-9012
    +972 72-789-0123
    +972 74-890-1234
    """
    
    print("🔍 Testing phone number detection...")
    print(f"📝 Test text: {test_text.strip()}")
    print(f"🌍 Region: IL")
    print()
    
    # Test with PhoneNumberMatcher
    print("📞 Using PhoneNumberMatcher:")
    hits = []
    try:
        for match in PhoneNumberMatcher(test_text, "IL"):
            num = match.number
            if phonenumbers.is_possible_number(num) and phonenumbers.is_valid_number(num):
                e164 = phonenumbers.format_number(num, PhoneNumberFormat.E164)
                natl = phonenumbers.format_number(num, PhoneNumberFormat.NATIONAL)
                hits.append((e164, natl, match.raw_string))
                print(f"  ✅ Found: {e164} ({natl}) - Raw: '{match.raw_string}'")
            else:
                print(f"  ❌ Invalid: {match.raw_string}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print(f"\n📊 Total found: {len(hits)}")
    
    # Test individual numbers
    print("\n🔍 Testing individual numbers:")
    individual_numbers = [
        "+972 50-123-4567",
        "+972 52-234-5678", 
        "+972 53-345-6789",
        "972 50-123-4567",
        "050-123-4567",
        "50-123-4567"
    ]
    
    for number in individual_numbers:
        try:
            parsed = phonenumbers.parse(number, "IL")
            if phonenumbers.is_valid_number(parsed):
                e164 = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
                natl = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
                print(f"  ✅ {number} -> {e164} ({natl})")
            else:
                print(f"  ❌ {number} -> Invalid")
        except Exception as e:
            print(f"  ❌ {number} -> Error: {e}")

if __name__ == "__main__":
    test_phone_detection()
