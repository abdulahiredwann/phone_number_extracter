#!/usr/bin/env python3
"""
Test the improved phone number detection
"""

import phonenumbers
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat
import re

def extract_phone_numbers_improved(text, region):
    """Improved phone number extraction with better regex patterns"""
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
        
        # Enhanced regex pattern matching for Israeli numbers
        israeli_patterns = [
            r'\+972\s*[2-9]\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{3,4}',  # +972 X-XXX-XXXX or +972 XX-XXX-XXXX
            r'0[2-9]\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{3,4}',        # 0X-XXX-XXXX or 0XX-XXX-XXXX
            r'[2-9]\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{3,4}',          # X-XXX-XXXX or XX-XXX-XXXX
            r'[2-9]\d{2,3}[-.\s]?\d{3,4}',                       # XXX-XXXX (like 421-4567)
        ]
        
        for pattern in israeli_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                raw_number = match.group(0)
                try:
                    # Clean the number - remove all non-digit characters except +
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

def test_phone_detection():
    """Test phone number detection with the problematic text"""
    
    # Test with the actual text from your logs
    test_texts = [
        "Sample israeli Numbers]",
        ". 421-4567]",
        "sto Sample israeli Numbers]",
        "+972 50-123-4567",
        "+972 52-234-5678",
        "421-4567",
        "50-123-4567",
        "52-234-5678"
    ]
    
    print("🔍 Testing improved phone number detection...")
    print(f"🌍 Region: IL")
    print()
    
    for text in test_texts:
        print(f"📝 Testing text: '{text}'")
        hits = extract_phone_numbers_improved(text, "IL")
        if hits:
            print(f"   ✅ Found {len(hits)} phone numbers")
            for e164, natl, raw in hits:
                print(f"      📞 {e164} ({natl}) from '{raw}'")
        else:
            print(f"   ❌ No phone numbers found")
        print()

if __name__ == "__main__":
    test_phone_detection()
