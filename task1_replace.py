#!/usr/bin/env python3
"""Task 1: Replace TypeWords/typewords.cc with Nuo.im/nuo.im in source files."""

import os

BASE = '/www/wwwroot/nuo.im'

# ========== 1. env.ts ==========
env_path = os.path.join(BASE, 'packages/core/src/config/env.ts')
with open(env_path, 'r') as f:
    content = f.read()

replacements = [
    ("Host = 'typewords.cc'", "Host = 'nuo.im'"),
    ("API: 'https://api.typewords.cc/'", "API: 'https://api.nuo.im/'"),
    ("LIBS_URL: 'https://libs.typewords.cc/'", "LIBS_URL: 'https://libs.nuo.im/'"),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"[env.ts] Replaced: {old} -> {new}")
    else:
        print(f"[env.ts] NOT FOUND: {old}")

# Verify GITHUB preserved
if "GITHUB = 'https://github.com/zyronon/TypeWords'" in content:
    print("[env.ts] GITHUB link preserved ✓")

with open(env_path, 'w') as f:
    f.write(content)

# ========== 2. nuxt.config.ts ==========
nuxt_path = os.path.join(BASE, 'apps/nuxt/nuxt.config.ts')
with open(nuxt_path, 'r') as f:
    content = f.read()

nuxt_replacements = [
    # typewords.cc URLs
    ("https://typewords.cc/", "https://nuo.im/"),
    # JSON-LD name fields
    ("name: 'TypeWords'", "name: 'Nuo.im'"),
]

for old, new in nuxt_replacements:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"[nuxt.config.ts] Replaced {count} occurrences: {old} -> {new}")
    else:
        print(f"[nuxt.config.ts] NOT FOUND: {old}")

# Verify GitHub link preserved
if 'github.com/zyronon' in content:
    print("[nuxt.config.ts] GitHub links preserved ✓")

with open(nuxt_path, 'w') as f:
    f.write(content)

print("\nAll replacements completed.")
