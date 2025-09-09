#!/usr/bin/env python3
"""
Test with real valid Israeli phone numbers
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
            r'[2-9]\d{3,4}[-.\s]?\d{3,4}',                       # XXXX-XXXX or XXX-XXXX
            r'[2-9]\d{1,4}[-.\s]?\d{3,4}',                       # More flexible: X-XXXX to XXXX-XXXX
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

def test_real_israeli_numbers():
    """Test with real valid Israeli phone numbers"""
    
    # Test with REAL valid Israeli numbers
    test_texts = [
        "Call me at +972 53-123-4567",  # Valid mobile
        "My number is 053-123-4567",    # Valid mobile with 0
        "Contact: 53-123-4567",         # Valid mobile without country code
        "Office: +972 2-123-4567",      # Valid landline
        "Home: 02-123-4567",            # Valid landline with 0
        "Phone: 2-123-4567",            # Valid landline without country code
        "Mobile: +972 77-123-4567",     # Valid mobile
        "Cell: 077-123-4567",           # Valid mobile with 0
    ]
    
    print("🔍 Testing with REAL valid Israeli phone numbers...")
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
    test_real_israeli_numbers()
