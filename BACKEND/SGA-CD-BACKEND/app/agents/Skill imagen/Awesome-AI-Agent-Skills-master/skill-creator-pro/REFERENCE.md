# Skill Creator Pro - Quick Reference

## Folder structure ready to install

```
skill-creator-pro/
├── SKILL.md                 ← The main skill (copy this anywhere)
├── README.md                ← Installation & setup guide
├── QUICK_START.md           ← Examples and common patterns
├── TEMPLATE.md              ← Template for creating new skills
└── REFERENCE.md             ← This file
```

## How to install

### Claude (Web or Desktop)
1. Copy full `SKILL.md` content
2. Paste in conversation
3. Done ✅

### OpenCode / Agent Skills
1. Create folder: `~/.agent-skills/skill-creator-pro/`
2. Copy `SKILL.md` into folder
3. Platform auto-loads it ✅

### Local (Git)
1. Clone or download this folder
2. Add to your skills registry
3. Reference by name ✅

---

## How to use in 30 seconds

```
/skill-creator-pro [Your task]
```

### Examples

```
/skill-creator-pro Create a skill for SEO audits
/skill-creator-pro Improve my email-writer skill
/skill-creator-pro Convert my analytics process into a reusable skill
/skill-creator-pro Add test prompts to the vroid-texture skill
/skill-creator-pro Fix my skill, it's not respecting template constraints
```

---

## What you get back

Every skill includes:

| Part | What it contains |
|------|-----------------|
| **Frontmatter** | Name + clear trigger description |
| **Purpose** | What the skill does |
| **When to use** | Trigger phrases and situations |
| **Inputs needed** | What the user provides |
| **Workflow** | Step-by-step operational process |
| **Output format** | Exact deliverable structure |
| **Rules** | Must-always behaviors |
| **Avoid** | Must-never mistakes |
| **Quality checklist** | Before final delivery |
| **Test prompts** | 3-7 examples to verify it works |

---

## Naming conventions

### Good skill names ✅

- `seo-audit-basic`
- `vroid-texture-maker`
- `email-template-writer`
- `firecrawl-lead-prospector`
- `weekly-analytics-brief`

### Bad skill names ❌

- `helper`
- `business`
- `ai-agent`
- `do-everything`
- `super`

**Rule:** Lowercase, hyphens, specific (not generic)

---

## Trigger description formula

**Best structure:**

```
[What it does]. Use when the user asks to [task 1], [task 2], or [common phrase].
Produces [output format] with [constraints].
```

**Example:**

```
Create SEO audit reports for websites. Use when the user asks to audit a site,
find SEO issues, or generate an audit report. Produces a formatted report with
on-page analysis, technical issues, and 5 actionable recommendations.
```

---

## Workflow best practices

### ❌ Don't write advice

```
1. Think about the content
2. Consider the audience
3. Write something good
```

### ✅ Write operational steps

```
1. Read the target page and identify main topic
2. Analyze title tag (verify it includes keyword)
3. Check H1-H3 hierarchy (H1 first, numbered hierarchy)
4. Extract 5 key points for internal linking
```

---

## Output format best practices

### ❌ Don't be vague

```
Output: A report
```

### ✅ Show the actual structure

```
Output format:

**[Page Name] - SEO Audit Report**

**Score:** [0-100]

**On-Page Findings**
- Title tag: [✓ or ✗] [explanation]
- Meta description: [✓ or ✗] [explanation]
- Headers: [✓ or ✗] [explanation]

**Technical Issues**
- [Issue 1]
- [Issue 2]
- [Issue 3]

**Top 5 Recommendations**
1. [Action + expected impact]
2. [Action + expected impact]
...
```

---

## Test prompts structure

```md
### Test 1: [Case type]
**Prompt:** [User example]
**Expected:** [What good result looks like]

---

### Test 2: [Case type]
**Prompt:** [User example]
**Expected:** [What good result looks like]
```

### Case types to include

- **Normal:** Standard, straightforward case
- **Edge:** Unusual constraint or condition
- **Missing info:** User gives incomplete data
- **Reference:** User provides example to follow
- **Failure prevention:** Test that prevents known problems

---

## Common workflows

### Create new skill

```
/skill-creator-pro Create a skill for [what I do]

Input:
- [What users give me]
- [What tools I use]

Output:
- [What I deliver]
- [Format/structure]

Example:
- [Show one example result]
```

### Improve existing skill

```
/skill-creator-pro Improve [skill-name]

Current problems:
- [Problem 1]
- [Problem 2]

What I want:
- [Improvement 1]
- [Improvement 2]
```

### Convert workflow

```
/skill-creator-pro Turn this into a skill:

I currently:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Tools: [What I use]
Input: [What I start with]
Output: [What I end with]
```

### Fix after failure

```
/skill-creator-pro Fix [skill-name]

What happened:
- [The bad result]
- [What I expected instead]

Make sure it never does X again
```

---

## Quick checklist before submitting a skill

- [ ] Name is lowercase with hyphens
- [ ] Description explains what + when + output
- [ ] Workflow steps are numbered and operational
- [ ] Output format shows actual structure
- [ ] Rules section covers key behaviors
- [ ] Avoid section lists real mistakes
- [ ] Quality checklist exists
- [ ] At least 3 test prompts included
- [ ] A beginner could use this immediately
- [ ] Skill is narrow (does one thing well)

---

## File locations

### After creating skills, organize them

```
~/.claude/skills/
├── seo-audit-basic/SKILL.md
├── email-template/SKILL.md
├── vroid-texture-maker/SKILL.md
└── skill-creator-pro/SKILL.md
```

Or in your AI platform's skills folder.

---

## Platform compatibility

Works on:

- ✅ Claude (Web, Desktop, API)
- ✅ OpenCode
- ✅ Agent Skills (standard SKILL.md format)
- ✅ Custom systems using SKILL.md
- ✅ Any LLM that can read Markdown + YAML

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Skill not loading | Check YAML frontmatter is valid |
| Vague results | Add more specific rules/checklist |
| Test prompts fail | Update workflow or output format |
| Too many edge cases | Narrow the scope of the skill |
| Hard to trigger | Improve the description with user phrases |

---

## One-page workflow

1. **Describe** what you want (workflow, output, constraints)
2. **Receive** complete SKILL.md file
3. **Copy** to your skills folder
4. **Test** using included test prompts
5. **Refine** if tests reveal issues
6. **Deploy** and use
7. **Improve** based on real-world failures

---

## Support

If a skill doesn't work:

1. Run a test prompt from the skill
2. Compare output to expected result
3. Ask: "Fix [skill-name], it's doing X instead of Y"
4. The skill will improve itself

---

**Last updated:** May 4, 2026  
**Version:** 1.0  
**Format:** Compatible with SKILL.md standard
