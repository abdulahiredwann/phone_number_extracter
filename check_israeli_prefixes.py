#!/usr/bin/env python3
"""
Check valid Israeli phone number prefixes
"""

import phonenumbers

def check_israeli_prefixes():
    """Check what prefixes are valid for Israeli numbers"""
    
    test_numbers = [
        "+972501234567",  # 50 prefix
        "+972521234567",  # 52 prefix  
        "+972531234567",  # 53 prefix
        "+972541234567",  # 54 prefix
        "+972551234567",  # 55 prefix
        "+972581234567",  # 58 prefix
        "+972591234567",  # 59 prefix
        "+972771234567",  # 77 prefix
        "+972721234567",  # 72 prefix
        "+972741234567",  # 74 prefix
        "+97221234567",   # 2 prefix (landline)
        "+97231234567",   # 3 prefix (landline)
        "+97241234567",   # 4 prefix (landline)
        "+97281234567",   # 8 prefix (landline)
        "+97291234567",   # 9 prefix (landline)
    ]
    
    print("🔍 Checking Israeli phone number prefixes...")
    print()
    
    for number in test_numbers:
        try:
            parsed = phonenumbers.parse(number, "IL")
            is_possible = phonenumbers.is_possible_number(parsed)
            is_valid = phonenumbers.is_valid_number(parsed)
            
            prefix = number[4:6] if len(number) > 6 else number[4:]
            status = "✅ Valid" if is_valid else "❌ Invalid"
            possible_status = "Possible" if is_possible else "Not Possible"
            
            print(f"📞 {number} (prefix: {prefix}) - {status} ({possible_status})")
            
        except Exception as e:
            print(f"❌ {number} - Error: {e}")

if __name__ == "__main__":
    check_israeli_prefixes()
