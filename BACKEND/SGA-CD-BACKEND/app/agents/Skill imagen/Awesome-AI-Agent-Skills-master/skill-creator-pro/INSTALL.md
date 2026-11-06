# 🚀 Installation Guide - All Platforms

Complete step-by-step instructions for installing Skill Creator Pro on any platform.

---

## Platform selection

Choose your platform:

- **[1. Claude](#1-claude-web-desktop-api)** — Easiest, no setup needed
- **[2. OpenCode](#2-opencode)** — Recommended for power users  
- **[3. Agent Skills](#3-agent-skills)** — For agents-based systems
- **[4. Custom LLM](#4-custom-llm-system)** — For custom setups

---

## 1. Claude (Web, Desktop, API)

### ✅ Easiest option - Works in seconds

**Step 1: Copy the skill**
```
Open: skill-creator-pro/SKILL.md
Select all text (Ctrl+A or Cmd+A)
Copy (Ctrl+C or Cmd+C)
```

**Step 2: Paste into Claude**
```
Open: Claude (Web, Desktop, or API client)
New conversation
Right-click → Paste (or Ctrl+V / Cmd+V)
```

**Step 3: Verify it loaded**
```
You should see the skill content in the conversation
The skill is now active
```

**Step 4: Use it**
```
Type: /skill-creator-pro Create a skill for [your task]
Get back: Complete SKILL.md file
```

### Optional: Save for reuse
If you want to use it repeatedly:

1. In Claude Web: Save conversation to favorites
2. In Claude Desktop: Create a preset in the settings
3. In API: Add to your system prompt

---

## 2. OpenCode

### Installation

**Step 1: Create the folder structure**
```
Linux/Mac:
mkdir -p ~/.agent-skills/skill-creator-pro

Windows PowerShell:
New-Item -ItemType Directory -Path "$env:USERPROFILE\.agent-skills\skill-creator-pro" -Force
```

**Step 2: Copy the SKILL.md file**
```
Copy skill-creator-pro/SKILL.md 
To: ~/.agent-skills/skill-creator-pro/SKILL.md

On Windows, use:
Copy-Item SKILL.md -Destination "$env:USERPROFILE\.agent-skills\skill-creator-pro\"
```

**Step 3: Verify installation**
```
List files in the directory:
ls ~/.agent-skills/skill-creator-pro/

Should show:
SKILL.md ✓
```

**Step 4: Configure OpenCode (if needed)**

Edit your OpenCode config file (usually `~/.agent-skills/config.yaml` or similar):

```yaml
skills_folder: ~/.agent-skills/
auto_load_skills: true
```

**Step 5: Restart OpenCode**
```
Close and reopen OpenCode
It should auto-load skill-creator-pro
```

**Step 6: Use it**
```
Type: /skill-creator-pro Create a skill for [your task]
Get back: Complete SKILL.md file
```

---

## 3. Agent Skills

### Installation

**Step 1: Create the folder**
```
Linux/Mac:
mkdir -p ~/.skills/skill-creator-pro

Windows PowerShell:
New-Item -ItemType Directory -Path "$env:USERPROFILE\.skills\skill-creator-pro" -Force
```

**Step 2: Copy SKILL.md**
```
Copy skill-creator-pro/SKILL.md 
To: ~/.skills/skill-creator-pro/SKILL.md
```

**Step 3: Verify**
```
List files:
ls ~/.skills/skill-creator-pro/

Should show:
SKILL.md ✓
```

**Step 4: Configure if needed**

In your Agent Skills config:
```yaml
skills_path: ~/.skills/
auto_discover: true
```

**Step 5: Restart the agent**
```
Restart your Agent Skills system
Should detect skill-creator-pro automatically
```

**Step 6: Use it**
```
Type: /skill-creator-pro Create a skill for [your task]
Get back: Complete SKILL.md file
```

---

## 4. Custom LLM System

For any system using SKILL.md format:

### Option A: File-based (Recommended)

**Step 1: Add to your skills folder**
```
Your system's skills folder (check documentation):
Copy SKILL.md there
OR
Create: ./skills/skill-creator-pro.md
```

**Step 2: Register the skill**

Depending on your system, you might need to:
- Add to a manifest file
- Update a skills registry
- Update a configuration file

Check your system's documentation.

**Step 3: Use it**
```
Follow your system's convention for triggers:
/skill-creator-pro [task]
OR
skill: skill-creator-pro, task: [task]
OR
[Whatever your system uses]
```

### Option B: Prompt-based

If your system doesn't have a skills folder:

**Step 1: Copy SKILL.md content**

**Step 2: Add to your system prompt or context**
```
Include the full SKILL.md content in your 
system context or custom instructions
```

**Step 3: Use normally**
```
The skill will be available in all conversations
```

---

## ✅ Verification checklist

After installation, verify it works:

- [ ] You can reference skill-creator-pro by name
- [ ] The skill loads without errors
- [ ] You can see the skill's purpose and workflow
- [ ] You can create a test skill:
  ```
  /skill-creator-pro Create a skill for [simple test task]
  ```
- [ ] You receive a complete SKILL.md back
- [ ] The returned skill has all sections (purpose, workflow, etc.)
- [ ] The skill is ready to copy to your skills folder

---

## 🐛 Troubleshooting

### Problem: Skill doesn't load

**Claude:**
- Make sure you copied the ENTIRE SKILL.md
- Check for copy errors (missing lines, corruption)
- Try copying a smaller test first

**OpenCode/Agent Skills:**
- Check file is in correct directory
- Check file name is exactly: SKILL.md
- Check config points to correct folder
- Restart the application
- Check logs for errors

### Problem: Skill loads but doesn't work

- Run a test prompt to see what's happening
- Check the error message
- Verify SKILL.md wasn't corrupted during copy

### Problem: Can't find the folder

**Create it manually:**

Linux/Mac:
```bash
mkdir -p ~/.agent-skills/skill-creator-pro
# Then copy SKILL.md into it
cp SKILL.md ~/.agent-skills/skill-creator-pro/
```

Windows PowerShell:
```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.agent-skills\skill-creator-pro" -Force
Copy-Item SKILL.md -Destination "$env:USERPROFILE\.agent-skills\skill-creator-pro\"
```

### Problem: SKILL.md syntax error

- Make sure file encoding is UTF-8
- Check YAML frontmatter for valid syntax:
  ```yaml
  ---
  name: skill-creator-pro
  description: [rest of description]
  ---
  ```
- No special characters in the YAML part

---

## 🎯 Which platform should I choose?

### Choose Claude if:
- You want easiest setup (literally 30 seconds)
- You mostly use Claude
- You don't need file-based persistence

### Choose OpenCode if:
- You want professional agent platform
- You work with multiple skills regularly
- You need version control / backup

### Choose Agent Skills if:
- You have existing Agent Skills setup
- You want standardized skill management
- Your team uses that platform

### Choose Custom if:
- You have your own LLM integration
- You want maximum flexibility
- You're building your own system

---

## 📚 Post-installation

After successful installation:

1. **Read:** START_HERE.md (5 min)
2. **Create:** Your first skill using the main SKILL.md
3. **Test:** Run included test prompts
4. **Copy:** Your created skills to the skills folder
5. **Use:** Across all platforms where you installed

---

## 🆘 Getting help

If installation isn't working:

1. **Read:** README.md (platform-specific notes)
2. **Check:** VISUAL_MAP.md (troubleshooting section)
3. **See:** This file (installation guide)
4. **Test:** Run a simple test prompt

---

## ✨ You're installed!

After completing installation for your platform:

✅ Skill Creator Pro is ready  
✅ You can create skills immediately  
✅ All documentation is available  
✅ Test prompts are included  

**Next:** Open START_HERE.md and create your first skill!

---

**Installation guide version:** 1.0  
**Last updated:** May 4, 2026  
**Platforms covered:** Claude, OpenCode, Agent Skills, Custom
