# Quick Start: Skill Creator Pro Examples

## What is a skill?

A **skill** is a documented procedure that an AI agent can follow reliably. It has:

- A clear name and when to use it
- Step-by-step workflow
- Expected input and output
- Rules and mistakes to avoid
- Test prompts to verify it works
- A quality checklist

## 5-minute setup

### 1. Copy the skill

Copy `SKILL.md` from this folder into any chat where you want to use it (Claude, OpenCode, etc.).

### 2. Use it immediately

```
/skill-creator-pro Create a skill for [your task here]
```

### 3. Get back

You'll receive a complete, tested, ready-to-use skill file.

---

## Example 1: Creating a completely new skill

**Your request:**
```
/skill-creator-pro Create a new skill for generating SEO audit reports. 
Users give me a website URL, and I produce a formatted report with:
- On-page SEO analysis
- Technical SEO issues  
- Readability score
- 5 actionable recommendations
```

**What you'll get back:**

A complete `SKILL.md` file with:
- ✅ Trigger phrases (when to use it)
- ✅ Workflow with specific steps (what to check, how)
- ✅ Output format (exact report structure)
- ✅ Rules (what to always do)
- ✅ Avoid section (mistakes to prevent)
- ✅ Quality checklist (before delivering the report)
- ✅ Test prompts (try it with real URLs)

---

## Example 2: Improving a skill that already exists

**You have:**

A skill called `email-template-writer` but it's too generic and doesn't produce good results.

**Your request:**

```
/skill-creator-pro Improve the email-template-writer skill.

Current version:
---
name: email-template-writer
description: Write email templates
---

# Email Template Writer

## Workflow
1. Ask what the email is for
2. Write an email
3. Done

Problems:
- No guidance on tone
- No output format
- No checklist
- Doesn't handle different industries
- No test prompts
```

**What you'll get back:**

An improved `SKILL.md` with:
- ✅ Better trigger description (now includes industry types)
- ✅ Specific workflow (tone, structure, call-to-action, personalization rules)
- ✅ Output format (exact email structure with sections)
- ✅ Rules for B2B vs B2C vs support vs sales
- ✅ Avoid section (spam triggers, weak CTAs, generic greetings)
- ✅ Quality checklist (before sending)
- ✅ Test prompts for different scenarios

---

## Example 3: Converting a repeated workflow into a skill

**You do this every week:**

1. Look at your website analytics
2. Compare this week vs last week
3. Note what changed
4. List 3 things to improve
5. Send summary to your team

**Your request:**

```
/skill-creator-pro Convert my weekly analytics review into a reusable skill.

What I do:
1. Pull bounce rate, session duration, conversion rate from Google Analytics
2. Compare to last week
3. Calculate % change
4. Write a short summary of wins and problems
5. List top 3 improvements to try
6. Format for my team Slack channel

Tools: Google Analytics (or CSV export)
Output: Slack-friendly summary (1 paragraph + bullet list)
```

**What you'll get back:**

A new skill called `weekly-analytics-brief` with:
- ✅ Clear trigger (when to use: weekly reviews, analytics summaries, etc.)
- ✅ Workflow matching your process (pull data → compare → calculate → summarize → format)
- ✅ Output format (Slack-friendly: emoji, bullet points, clear formatting)
- ✅ Rules (what metrics matter, which to ignore)
- ✅ Checklist (before posting to Slack)
- ✅ Test prompts (with sample analytics data)

---

## Example 4: Adding test prompts to an existing skill

**You have:**

A working skill but want to verify it actually works before deploying it.

**Your request:**

```
/skill-creator-pro Add comprehensive test prompts to the vroid-texture-maker skill.

Current skill does:
- Takes a reference image
- Analyzes the clothing type
- Generates texture mapping instructions
- Produces a UV layout guide
```

**What you'll get back:**

Test prompts covering:
- ✅ Normal case (casual clothing reference)
- ✅ Complex case (detailed/ornate design)
- ✅ Edge case (non-standard proportions)
- ✅ Failure prevention (template compatibility)
- ✅ Each test shows what a "good result" looks like

---

## Example 5: Fixing a skill after it fails

**What happened:**

You used the `vroid-texture-maker` skill, and it created a beautiful design BUT it didn't fit the actual VRoid template zones.

**Your request:**

```
/skill-creator-pro The vroid-texture-maker skill made nice textures but ignored the template zones. 
Fix this so it never happens again.
```

**What you'll get back:**

An updated skill with:
- ✅ New rule: "Analyze the actual template before designing"
- ✅ New checklist item: "Verify all details fit inside UV areas"
- ✅ Reordered workflow (template analysis moved to first step)
- ✅ New test prompt (checks template compatibility)
- ✅ Avoid section warns against generic designs

---

## Example 6: Creating a business/automation skill

**You want to:**

Automate prospecting. Use Firecrawl to scrape target websites, extract company info and contacts, output a CSV for outreach.

**Your request:**

```
/skill-creator-pro Create a skill for lead prospecting with Firecrawl.

What it should do:
1. User gives me a target website URL
2. Crawl the site with Firecrawl API
3. Extract: company name, contacts, email, phone, location
4. Output: CSV file with leads
5. Ready for LinkedIn outreach

Need:
- Firecrawl API key setup instructions
- Privacy/ethics notes (don't scrape sensitive data)
- Fallback for blocked sites
- Test with 3 real websites
```

**What you'll get back:**

A complete automation skill with:
- ✅ Account/setup requirements (Firecrawl API key)
- ✅ Data flow (URL → API → parsing → CSV)
- ✅ Failure handling (what to do if site blocks crawling)
- ✅ Privacy caution (what data to avoid, why)
- ✅ Manual fallback (if automation fails)
- ✅ Test prompts (with real websites)
- ✅ Security checklist (API key handling, data safety)

---

## Common patterns

### Pattern: "Make me a skill for X"

```
/skill-creator-pro Create a skill for [what you want to do]
Details:
- Input: [what users provide]
- Output: [what you deliver]
- Tools: [tools used, if any]
- Audience: [who uses this]
```

### Pattern: "This skill doesn't work"

```
/skill-creator-pro Fix the [skill-name] skill.
Problem: [what went wrong]
Example: [show the bad output]
What it should do: [what you expected]
```

### Pattern: "Improve this skill"

```
/skill-creator-pro Improve [skill-name].
Current issues:
- [problem 1]
- [problem 2]
- [problem 3]
```

### Pattern: "Turn this into a skill"

```
/skill-creator-pro Convert this into a skill:

I do this: [describe your process]
Tools: [tools used]
Input: [what you start with]
Output: [what you end with]
```

---

## Tips for best results

1. **Be specific about output** — Don't say "write a report." Say "Markdown report with sections: Title, Key Findings (3 bullets), Recommendations (5 numbered items), Next Steps."

2. **Show an example if possible** — If you have a previous version or example, paste it. Skills improve with references.

3. **List constraints early** — "Must fit VRoid template," "Privacy-safe scraping only," "Slack-friendly format"

4. **Mention what went wrong** — If a skill failed, tell it exactly how: "It worked great except for X." The skill will add a rule to prevent X.

5. **Use the test prompts** — Don't just create a skill and assume it works. Run the test prompts and see if results match expectations.

---

## Workflow summary

### Creating a skill:

1. Tell skill-creator-pro what you want
2. Receive complete SKILL.md file
3. Copy it to your skills folder
4. Run test prompts to verify
5. Refine based on test results

### Improving a skill:

1. Paste your existing SKILL.md
2. Describe what's not working
3. Receive updated SKILL.md with fixes
4. Run updated test prompts
5. Verify improvements

### Using skills in practice:

1. Trigger skill with `/skill-name [task]`
2. Skill runs its workflow
3. Skill delivers output + quality checklist
4. If something failed, feed that back to improve the skill

---

## Next steps

1. **Start here:** Copy `SKILL.md` and use it in Claude, OpenCode, or your AI agent
2. **First skill:** Use it to create a skill for one of your repeated tasks
3. **Test it:** Run the test prompts included in the skill output
4. **Refine it:** If tests fail, ask the skill to fix itself
5. **Share it:** Keep your skills in a folder so you can reuse them

---

**You're ready to build skills now.** Start with:

```
/skill-creator-pro Create a skill for [your first workflow]
```

Good luck! 🚀
