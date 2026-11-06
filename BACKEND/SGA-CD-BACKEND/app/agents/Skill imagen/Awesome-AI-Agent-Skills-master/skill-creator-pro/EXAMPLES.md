# Example Skills - Real-World Reference

These are example skills created WITH skill-creator-pro. Use them as reference for what good skills look like.

---

## Example 1: SEO Audit Basic Skill

```md
---
name: seo-audit-basic
description: Create SEO audit reports for websites. Use when the user asks to audit a site, find SEO issues, or generate an audit report. Produces a formatted report with on-page analysis, technical issues, and 5 actionable recommendations.
---

# SEO Audit Basic

## Purpose

Systematically analyze a website's SEO performance and produce an actionable audit report covering on-page, technical, and content factors.

## When to use this skill

- User asks: "Audit my website for SEO"
- User provides a URL and wants SEO recommendations
- User asks: "What SEO issues does [site] have?"
- User wants: "SEO report for [URL]"

## Inputs needed

- Website URL (required)
- Specific focus area, if any (optional): e.g., "focus on mobile," "blog posts only"

## Workflow

1. **Access and analyze the homepage**
   - Visit the URL and read the full page
   - Note the visible content, structure, and design

2. **Analyze on-page SEO**
   - Check title tag (length, keyword presence, clarity)
   - Check meta description (length, keyword, CTA)
   - Analyze H1 tag (present? Matches title? Clear?)
   - Check H2/H3 hierarchy and keyword relevance
   - Count word count (minimum 300 words for blog posts)

3. **Check technical factors**
   - Is the site HTTPS? (green lock present?)
   - Mobile responsive? (check design on mobile view)
   - Page speed perception (does it load quickly?)
   - Readability (font size, contrast, line spacing)

4. **Identify internal linking opportunities**
   - Find 3-5 potential internal link anchors
   - Suggest where to link from/to

5. **Rate overall score**
   - 80-100: Strong (minimal changes needed)
   - 60-79: Good (several improvements possible)
   - 40-59: Fair (significant work needed)
   - Below 40: Weak (major overhaul needed)

## Output format

```
# SEO Audit Report: [Site Name]

**Date:** [Today's date]
**URL:** [The URL audited]
**Overall Score:** [0-100]

## On-Page SEO

**Title Tag**
- Current: "[Actual title]"
- Analysis: [Length, keywords, clarity check]
- Score: [✓ Good / ⚠ Needs work / ✗ Missing]
- Recommendation: [Specific improvement]

**Meta Description**
- Current: "[Actual description]"
- Analysis: [Length check, CTA presence]
- Score: [✓ Good / ⚠ Needs work / ✗ Missing]
- Recommendation: [Specific improvement]

**H1 Tag**
- Current: "[Actual H1]"
- Analysis: [Does it match title? Include keyword?]
- Score: [✓ Good / ⚠ Needs work / ✗ Missing]

**Header Hierarchy (H2/H3)**
- Found: [Number of headers]
- Structure: [Is it logical?]
- Keyword coverage: [Do headers reflect main topics?]
- Recommendation: [If any improvements needed]

**Content Quality**
- Word count: [Number]
- Readability: [Good / Could improve]
- Unique value: [What does this page offer?]

## Technical SEO

**Security:** [HTTPS ✓ / HTTP ✗]
**Mobile-responsive:** [Yes ✓ / No ✗]
**Page speed:** [Fast / Moderate / Slow]
**Readability:** [Font size, contrast, line spacing assessment]

## Internal Linking Opportunities

1. Anchor: "[Text]" → Link to: "[Suggestion]"
2. Anchor: "[Text]" → Link to: "[Suggestion]"
3. Anchor: "[Text]" → Link to: "[Suggestion]"

## Top 5 Actionable Recommendations

1. **[Priority action]**
   - Why: [Impact explanation]
   - How: [Specific steps]
   - Expected benefit: [SEO impact]

2. **[Priority action]**
   - Why: [Impact explanation]
   - How: [Specific steps]
   - Expected benefit: [SEO impact]

3. **[Priority action]**
   - Why: [Impact explanation]
   - How: [Specific steps]
   - Expected benefit: [SEO impact]

4. **[Priority action]**
   - Why: [Impact explanation]
   - How: [Specific steps]
   - Expected benefit: [SEO impact]

5. **[Priority action]**
   - Why: [Impact explanation]
   - How: [Specific steps]
   - Expected benefit: [SEO impact]

## Summary

- Strengths: [2-3 strong points]
- Main challenges: [2-3 problem areas]
- Quick wins: [1-2 easiest improvements]
- Long-term improvements: [1-2 harder but important changes]
```

## Rules

- Always check HTTPS security first
- Title tag must be 50-60 characters
- Meta description must be 150-160 characters
- Include specific, actionable recommendations (not generic advice)
- Rate based on SEO best practices, not opinion

## Avoid

- Making assumptions about mobile experience without checking
- Suggesting changes without explaining the SEO benefit
- Being too harsh or too generous with scores
- Missing the obvious (title tag, meta, H1)
- Recommending changes that hurt user experience

## Quality checklist

- [ ] URL was successfully analyzed
- [ ] All 5 sections (title, meta, H1, headers, content) are complete
- [ ] Technical SEO checks are present
- [ ] Score is justified by findings
- [ ] Top 5 recommendations are specific and actionable
- [ ] Internal linking suggestions are relevant
- [ ] Recommendations explain "why" and "how to"
- [ ] Report is ready to share or implement

## Test prompts

### Test 1: Blog homepage
**Prompt:** Audit https://www.example.com/blog/ for SEO
**Expected:** Report with homepage analysis, H1/H2 structure, internal linking ideas, 5 specific recommendations

### Test 2: Missing meta description
**Prompt:** Audit a site that doesn't have a meta description
**Expected:** Report notes missing meta and includes it as Priority 1 recommendation

### Test 3: Mobile-only site
**Prompt:** Audit a mobile-optimized site without much content
**Expected:** Report acknowledges mobile focus, rates based on mobile SEO, suggests content expansion

---

**Version:** 1.0  
**Platform compatible:** Claude, OpenCode, Agent Skills
```

---

## Example 2: Email Template Writer Skill

```md
---
name: email-template-writer
description: Create persuasive, industry-specific email templates for sales, support, marketing, and newsletters. Use when the user asks to write an email template, needs an email example, or wants to improve email tone. Produces pre-filled templates with tone, CTA, and personalization guidance.
---

# Email Template Writer

## Purpose

Generate professionally-written, ready-to-use email templates tailored to specific industries, purposes, and audiences.

## When to use this skill

- User asks: "Write an email template for [industry/purpose]"
- User provides an email they wrote and wants it improved
- User asks: "What should a [type] email look like?"
- User wants: "Template for [specific scenario]"

## Inputs needed

- Email purpose (sales pitch, customer support, newsletter, outreach, etc.)
- Target audience/industry (B2B, B2C, healthcare, SaaS, etc.)
- Tone preference (professional, casual, urgent, friendly, formal)
- Key message or goal of the email

## Workflow

1. **Identify the email purpose and audience**
   - What is the main goal? (close deal, resolve issue, announce news, etc.)
   - Who is reading this? (cold prospect, existing customer, team, etc.)
   - What action do you want them to take?

2. **Determine tone and personality**
   - B2B formal: Professional, respectful, value-focused
   - B2B casual: Friendly, conversational, helpful
   - B2C: Conversational, benefit-focused, urgency-aware
   - Support: Empathetic, solution-focused, reassuring

3. **Structure the email**
   - Subject line (attention-grabbing, benefit-focused)
   - Opening (personalized, relevant to recipient)
   - Body (single idea per paragraph, clear value)
   - Call-to-action (specific, easy, beneficial)
   - Closing (professional signature)

4. **Add personalization markers**
   - [NAME] for recipient name
   - [COMPANY] for their company
   - [SPECIFIC_DETAIL] for research-based personalization

5. **Create alternative versions**
   - Provide 1 "confident" version
   - Provide 1 "soft" version
   - Note when to use each

## Output format

```
# Email Template: [Purpose]

**Target Audience:** [Industry/Role]
**Tone:** [Professional/Casual/Urgent/Friendly]
**Goal:** [What action should recipient take?]

---

## Subject Line Options

**Option 1 (Confident):** [Subject]
**Option 2 (Soft):** [Subject]
**Option 3 (Curiosity-based):** [Subject]

---

## Email Body

**[CONFIDENT VERSION]**

Hi [NAME],

[Opening paragraph - 1-2 sentences, personalized, relevant to their situation]

[Body paragraph 1 - The key insight or value proposition]

[Body paragraph 2 - Social proof, specific benefit, or data point]

[Body paragraph 3 - The specific ask or next step]

[CTA paragraph - Clear, benefit-focused call to action]

Best regards,
[YOUR NAME]
[YOUR TITLE]
[YOUR COMPANY]

---

**[SOFT VERSION]**

[Same structure, but softer language, more questions, less assumption]

---

## Personalization Checklist

- [ ] Research [NAME]'s recent company news
- [ ] Mention a specific detail about [COMPANY] (not generic)
- [ ] Reference their industry/role in opening
- [ ] Use [NAME] naturally (not forced)
- [ ] Explain benefit for THEM (not your company)

## When to use each version

- **Confident:** High-priority prospect, direct referral, existing relationship
- **Soft:** Cold outreach, sensitive decision, long sales cycle

## Common mistakes to avoid

- Don't make it about you, make it about them
- Don't use generic subject lines
- Don't include too many paragraphs (max 4)
- Don't forget the specific CTA
- Don't personalize with name alone (add relevant detail)

## Success signals

- Email is under 200 words (easy to read on mobile)
- CTA is specific and clear
- Value proposition is in first 2 paragraphs
- Personalization feels natural, not forced
```

## Rules

- Every email must have a clear CTA (not vague)
- Tone must match the audience (B2B ≠ B2C)
- Personalization must be genuine (research-backed, not just the name)
- Subject lines must be benefit-focused or curiosity-focused
- Keep body under 200 words

## Avoid

- Generic openers ("I hope this email finds you well")
- Multiple CTAs (confuses the reader)
- Salesy language in B2B contexts
- Assuming the recipient knows who you are
- Long paragraphs (break them up)
- Typos or grammar errors

## Quality checklist

- [ ] Purpose and audience are clear
- [ ] Subject lines are benefit-focused or curiosity-based
- [ ] Personalization is genuine (not just name insertion)
- [ ] Body is under 200 words
- [ ] CTA is specific and clear
- [ ] Tone matches audience
- [ ] Both versions provided (if applicable)
- [ ] Email ready to copy and send

## Test prompts

### Test 1: Sales outreach
**Prompt:** Write a cold sales email template for a SaaS tool, targeting marketing directors
**Expected:** Professional tone, personalized opening, benefit-focused body, clear CTA, subject line options

### Test 2: Customer support
**Prompt:** Write an apology email for a delayed order
**Expected:** Empathetic tone, solution-focused, reassuring closing, soft touch

### Test 3: Newsletter announcement
**Prompt:** Write an email announcing a new blog post series
**Expected:** Casual-friendly tone, value-focused, benefit to reader, soft CTA (no hard sell)

---

**Version:** 1.0  
**Platform compatible:** Claude, OpenCode, Agent Skills
```

---

## Example 3: Weekly Analytics Brief Skill

```md
---
name: weekly-analytics-brief
description: Generate weekly website analytics summaries with key metrics, comparison to last week, and 3 actionable improvements. Use when the user asks for a weekly report, analytics summary, or performance overview. Produces Slack-friendly briefs with wins, problems, and improvement priorities.
---

# Weekly Analytics Brief

## Purpose

Transform raw analytics data into a weekly executive summary highlighting key metrics, week-over-week changes, and prioritized improvements.

## When to use this skill

- Every Monday morning for last week's analytics
- User asks: "Summarize last week's traffic"
- User wants: "What's changed in analytics?"
- User needs: Weekly report for team Slack/email

## Inputs needed

- Analytics data (Google Analytics export, custom CSV, or summary)
- Key metrics to track: bounce rate, sessions, conversions, pages/session, avg. duration
- Previous week's data (for comparison)
- Any unusual events (campaign launch, outage, etc.)

## Workflow

1. **Extract key metrics**
   - Total sessions
   - Bounce rate (%)
   - Avg. session duration
   - Conversion rate (if tracked)
   - Top 3 pages by traffic

2. **Calculate week-over-week changes**
   - Sessions: [This week] vs [Last week] = [% change, ↑ or ↓]
   - Bounce rate: [Change] (↑ = bad, ↓ = good)
   - Duration: [Change] (↑ = good, ↓ = bad)
   - Track which direction each metric moved

3. **Identify wins**
   - What improved from last week?
   - What was the best-performing content?
   - Any metrics hitting targets?

4. **Identify problems**
   - What declined?
   - High bounce rate pages?
   - Traffic sources that underperformed?

5. **Prioritize 3 improvements**
   - Pick the highest-impact action
   - Pick the easiest quick-win action
   - Pick the strategic long-term action

## Output format

```
📊 **Weekly Analytics Brief**
*Week of [Date] - [Date]*

---

**📈 Key Metrics**

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Sessions | [###] | [###] | [+X% ↑] |
| Bounce Rate | [##%] | [##%] | [-X% ↓] |
| Avg. Duration | [#m ##s] | [#m ##s] | [+X% ↑] |
| Conversion Rate | [#.#%] | [#.#%] | [+X.X% ↑] |

---

**🎯 What Worked**
- [Win 1]: [Specific page/source] brought [#] new sessions (↑#%)
- [Win 2]: [Content type] conversion rate improved by #%
- [Win 3]: [Traffic source] outperformed last week

---

**⚠️ What Needs Attention**
- [Problem 1]: [Page/source] bounce rate at ##% (target: ##%)
- [Problem 2]: [Traffic source] declined #% week-over-week
- [Problem 3]: [Content type] saw less engagement

---

**🎯 Top 3 Actions This Week**

**1. Quick Win:** [Easiest improvement]
   - Impact: [Expected result]
   - Owner: [Who does it]
   - Timeline: [Days/hours]

**2. High Priority:** [Biggest impact opportunity]
   - Impact: [Expected result]
   - Owner: [Who does it]
   - Timeline: [Days/weeks]

**3. Strategic:** [Long-term improvement]
   - Impact: [Expected result]
   - Owner: [Who does it]
   - Timeline: [Weeks/months]

---

**Next check:** [Next week's date]
```

## Rules

- Always show week-over-week comparison
- Highlight bounces rate down (↓) as good, up (↑) as bad
- Highlight session duration up (↑) as good, down (↓) as bad
- Include at least 1 quick-win action
- Format for Slack (emojis, bullets, tables for readability)
- Make actions specific and assignable

## Avoid

- Generic commentary ("we had traffic")
- Not explaining WHAT the data means
- Forgetting to mention problem areas
- Overloading with metrics (max 8)
- Actions without owners or timelines

## Quality checklist

- [ ] All key metrics are present with week-over-week comparison
- [ ] Change directions are correct (↑ or ↓)
- [ ] At least 2 wins and 2 problems identified
- [ ] All 3 actions are specific and actionable
- [ ] Actions have owners and timelines
- [ ] Format is Slack-friendly (emojis, tables, short lines)
- [ ] Report is under 500 words
- [ ] Ready to copy-paste into Slack

## Test prompts

### Test 1: Normal week with good growth
**Prompt:** Create a weekly brief for a site with +15% traffic, -5% bounce rate, +10% conversions this week
**Expected:** Report highlights wins, comparison is clear, 3 actions proposed

### Test 2: Problem week
**Prompt:** Create a weekly brief for a site with -20% traffic, bounce rate up 8%, duration down 30 seconds
**Expected:** Report acknowledges problems, suggests diagnostic actions, problem priorities clear

### Test 3: Campaign week
**Prompt:** Create a weekly brief mentioning a new campaign launched mid-week that caused spike
**Expected:** Report distinguishes campaign impact from organic trends, actions account for campaign results

---

**Version:** 1.0  
**Platform compatible:** Claude, OpenCode, Agent Skills
```

---

## How to use these examples

1. **Copy the SKILL.md section** of any example above
2. **Paste into your skills folder** (or directly into Claude/OpenCode)
3. **Test using the test prompts** included in each skill
4. **Adapt for your needs** (change metrics, add custom fields, etc.)

## What makes these good skills

✅ **Clear purpose** — No confusion about what it does  
✅ **Specific trigger** — Knows when to activate  
✅ **Operational workflow** — Step-by-step, actionable  
✅ **Exact output format** — Shows structure, not just advice  
✅ **Test prompts** — You can verify it works  
✅ **Quality checklist** — Knows when it's "done"  
✅ **Real-world rules** — Based on actual best practices  
✅ **Narrow scope** — Does one thing well  

---

**Use these as templates** for the skills you create with skill-creator-pro!
