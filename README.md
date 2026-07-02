# ContextGuard AI

ContextGuard AI is a governed enterprise intelligence hub for natural-language analytics over structured warehouse data and enterprise documents.

The first implementation path is Snowflake-first. The POC will use Snowflake Cortex, semantic modeling, role-based access control, masking policies, document intelligence, automatic charting, and evaluation workflows to help business users get trusted answers without writing SQL.

## Current Status

This repository has been reset for the new Snowflake-first POC. The previous repository contents are preserved on the `archive/old-version` branch.

## Project Areas

- `docs/` - project blueprint, Jira plan, architecture notes, and demo documentation.
- `snowflake/` - Snowflake setup, raw tables, curated views, semantic model, security, document, and evaluation SQL.
- `app/` - application code. The Next.js frontend will be scaffolded here.
- `data/` - synthetic data and sample documents for the POC.
- `scripts/` - data generation and evaluation utilities.

## First POC Goal

Build a Snowflake-first governed intelligence platform with:

- Natural-language questions over Snowflake data.
- Semantic model based SQL generation using Cortex Analyst.
- Automatic chart rendering.
- Persona-based business dashboards.
- Admin governance studio.
- PHI/PII-style masking and row-level access examples.
- PDF/document upload and semantic Q&A.
- Evaluation dataset for hallucination and accuracy testing.

## Team Model

The project is organized as a two-resource delivery model:

- Data/AI Engineer: Snowflake, synthetic data, semantic layer, Cortex, security, evaluation.
- Product/Frontend Engineer: Next.js app, dashboards, admin studio, charts, document UI, demo polish.

## Key Documents

- [Project Blueprint](docs/ContextGuard_AI_Project_Blueprint.md)
- [Day-Wise Jira Plan](docs/Jira_Day_Wise_Two_Resource_Plan.md)

## Security Notes

Do not commit real secrets, Snowflake passwords, API keys, private keys, or customer data. Use `.env.local` for local secrets and keep `.env.example` as the documented template.

