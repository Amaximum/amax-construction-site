#!/usr/bin/env python3
"""
Add Home Renovation to footer on all pages
"""

import os
import re

def add_home_renovation_to_footer():
    count = 0
    skipped = 0
    
    # Find all index.html files
    for root, dirs, files in os.walk('.'):
        # Skip hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file == 'index.html':
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if already has home-renovation in footer
                if '/home-renovation/' in content:
                    skipped += 1
                    continue
                
                # Pattern: add after excavation, before christmas-lights
                old_pattern = '<li><a href="/excavation-services/">Excavation</a></li>\n          <li><a href="/christmas-lights-installation-toronto-gta/">Christmas Lights</a></li>'
                new_text = '<li><a href="/excavation-services/">Excavation</a></li>\n          <li><a href="/home-renovation/">Home Renovation</a></li>\n          <li><a href="/christmas-lights-installation-toronto-gta/">Christmas Lights</a></li>'
                
                if old_pattern in content:
                    content = content.replace(old_pattern, new_text)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1
                else:
                    print(f"Pattern not found: {filepath}")
    
    print(f"\nUpdated: {count}")
    print(f"Skipped (already has): {skipped}")

if __name__ == "__main__":
    add_home_renovation_to_footer()
