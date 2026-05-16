# ECC for Gemini CLI

This file provides Gemini CLI with the baseline ECC workflow, review standards, and security checks for repositories that install the Gemini target.

## Overview

Everything Claude Code (ECC) is a cross-harness coding system with 36 specialized agents, 142 skills, and 68 commands.

Gemini support is currently focused on a strong project-local instruction layer via `.gemini/GEMINI.md`, plus the shared MCP catalog and package-manager setup assets shipped by the installer.

## Core Workflow

1. Plan before editing large features.
2. Prefer test-first changes for bug fixes and new functionality.
3. Review for security before shipping.
4. Keep changes self-contained, readable, and easy to revert.

## Coding Standards

- Prefer immutable updates over in-place mutation.
- Keep functions small and files focused.
- Validate user input at boundaries.
- Never hardcode secrets.
- Fail loudly with clear error messages instead of silently swallowing problems.

## Security Checklist

Before any commit:

- No hardcoded API keys, passwords, or tokens
- All external input validated
- Parameterized queries for database writes
- Sanitized HTML output where applicable
- Authz/authn checked for sensitive paths
- Error messages scrubbed of sensitive internals

## Delivery Standards

- Use conventional commits: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`
- Run targeted verification for touched areas before shipping
- Prefer contained local implementations over adding new third-party runtime dependencies

## ECC Areas To Reuse

- `AGENTS.md` for repo-wide operating rules
- `skills/` for deep workflow guidance
- `commands/` for slash-command patterns worth adapting into prompts/macros
- `mcp-configs/` for shared connector baselines

POI Scraping


Here are the strict requirements for the script:
1. Input Data: Read a CSV file (e.g., `data/silver/outlet_master_cleaned.csv`) containing the columns `Outlet_ID`, `Latitude`, and `Longitude`.
2. API Query: For each location, use an Overpass QL query to count the number of specific POIs within a 1000-meter radius. The specific amenities/POIs to extract counts for are: schools, hospitals, bus stops (highway=bus_stop), restaurants, fuel stations, and tourist places (tourism=*).
3. Error Handling: Include robust `try-except` blocks. If a request fails or a location is invalid, the script should not crash; it should log the error and return 0 for those counts.
4. Rate Limiting: Add a `time.sleep(1)` between requests to respect the Overpass API rate limits and avoid our IP getting blocked.
5. Output Data: Save the final aggregated dataset (containing the `Outlet_ID` and the respective individual POI counts) as a new CSV file directly to `data/gold/poi_data.csv`.

Please provide clean, modular, and well-commented code suitable for a data Lakehouse architecture.