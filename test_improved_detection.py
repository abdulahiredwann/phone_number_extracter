#!/usr/bin/env python3
"""
Test improved phone number detection
"""

import phonenumbers
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat
import re

def extract_phone_numbers_improved(text, region):
    """Improved phone number extraction with regex fallback"""
    hits = []
    try:
        # First try with PhoneNumberMatcher
        for match in PhoneNumberMatcher(text, region):
            num = match.number
            if phonenumbers.is_possible_number(num) and phonenumbers.is_valid_number(num):
                e164 = phonenumbers.format_number(num, PhoneNumberFormat.E164)
                natl = phonenumbers.format_number(num, PhoneNumberFormat.NATIONAL)
                hits.append((e164, natl, match.raw_string))
                print(f"   📞 Found via matcher: {e164} ({natl}) from '{match.raw_string}'")
        
        # Also try regex pattern matching for Israeli numbers
        israeli_patterns = [
            r'\+972\s*[2-9]\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}',  # +972 X-XXX-XXXX
            r'0[2-9]\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}',        # 0X-XXX-XXXX
            r'[2-9]\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}',          # X-XXX-XXXX
        ]
        
        for pattern in israeli_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                raw_number = match.group(0)
                try:
                    # Clean the number
                    clean_number = re.sub(r'[^\d+]', '', raw_number)
                    if not clean_number.startswith('+'):
                        if clean_number.startswith('0'):
                            clean_number = '+972' + clean_number[1:]
                        else:
                            clean_number = '+972' + clean_number
                    
                    parsed = phonenumbers.parse(clean_number, region)
                    if phonenumbers.is_valid_number(parsed):
                        e164 = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
                        natl = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
                        
                        # Check if we already have this number
                        if not any(hit[0] == e164 for hit in hits):
                            hits.append((e164, natl, raw_number))
                            print(f"   📞 Found via regex: {e164} ({natl}) from '{raw_number}'")
                except Exception as e:
                    print(f"   ❌ Regex match error for '{raw_number}': {e}")
                    
    except Exception as e:
        print(f"Phone number extraction error: {e}")
    return hits

def test_improved_detection():
    """Test improved phone number detection"""
    
    # Test with the actual text from your video
    test_texts = [
        "Sample israeli Numbers",
        "Sample Numbers)",
        "Sample israeli Numbers]",
        "Sample israeli Numbers 3,",
        "Sample sracli",
        "Sample sracli Numbers]",
        "Sample israeli Numbers cer) =",
        # Test with actual phone numbers
        "+972 50-123-4567",
        "+972 52-234-5678", 
        "+972 53-345-6789",
        "050-123-4567",
        "052-234-5678",
        "50-123-4567",
        "52-234-5678"
    ]
    
    print("🔍 Testing improved phone number detection...")
    print(f"🌍 Region: IL")
    print()
    
    for text in test_texts:
        print(f"📝 Testing: '{text}'")
        hits = extract_phone_numbers_improved(text, "IL")
        if hits:
            print(f"   ✅ Found {len(hits)} phone numbers")
        else:
            print(f"   ❌ No phone numbers found")
        print()

if __name__ == "__main__":
    test_improved_detection()
