---
name: data-hub
description: Use when selecting document or data-format skills for DOCX, PDF, PPTX, XLSX, office-file manipulation, tabular data work, or financial analysis workflows.
version: 1.0.0
author: walva
license: MIT
tags:
  - documents
  - data
  - office
  - finance
  - pdf
agents:
  - claude-code
---

# Data Hub

5 skills for working with documents, spreadsheets, presentations, and financial data.

## Skills

| Skill | Purpose |
|-------|---------|
| docx | Read and write Microsoft Word documents |
| pdf | Parse, extract, and generate PDF files |
| pptx | Create and modify PowerPoint presentations |
| xlsx | Read, write, and analyze Excel spreadsheets |
| finance | Financial analysis: DCF valuation, SaaS metrics, budgeting, forecasting |

## Usage

To load a specific skill, read its SKILL.md:
```
/read data-hub/pdf/SKILL.md
/read data-hub/xlsx/SKILL.md
/read data-hub/finance/SKILL.md
```

