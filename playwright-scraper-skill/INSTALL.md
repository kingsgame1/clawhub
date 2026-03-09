# Installation Guide

## Quick Installation

### 1. Clone or Download the Skill
```bash

# Method 1: Using git clone (if public repo)
git clone https://github.com/waisimon/playwright-scraper-skill.git
cd playwright-scraper-skill

# After downloading, enter the directory
```

# Install Playwright (recommended)
npm install

# Install browser (Chromium)
npx playwright install chromium

# Quick test
node scripts/playwright-simple.js https://example.com

# Test Stealth version
node scripts/playwright-stealth.js https://example.com

---

## Advanced Installation

### Using with OpenClaw
If you're using OpenClaw, you can place this skill in the skills directory:

# Assuming your OpenClaw workspace is at ~/.openclaw/workspace
cp -r playwright-scraper-skill ~/.openclaw/workspace/skills/

# Then you can invoke it in OpenClaw

## Verify Installation
Run the example script:

# Discuss.com.hk example (verified working)
bash examples/discuss-hk.sh

If you see output similar to this, installation is successful:

️ Starting Playwright Stealth scraper...
 Navigating to: https://m.discuss.com.hk/#hot
 HTTP Status: 200
 Scraping complete!

## Common Issues

### Issue: Playwright not found
**Error message:** `Error: Cannot find module 'playwright'`

**Solution:**

### Issue: Browser launch failed
**Error message:** `browserType.launch: Executable doesn't exist`

### Issue: Permission errors
**Error message:** `Permission denied`

chmod +x scripts/*.js
chmod +x examples/*.sh

## System Requirements
- **Node.js:** v18+ recommended
- **OS:** macOS / Linux / Windows
- **Disk Space:** ~500MB (including Chromium)
- **RAM:** 2GB+ recommended

## Next Steps
After installation, check out:
- [README.md](README.md) — Quick reference
- [SKILL.md](SKILL.md) — Full documentation
- [examples/](examples/) — Example scripts