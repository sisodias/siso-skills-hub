# Testing Agent Plan

## Purpose
Automated visual testing agent for SISO Internal Lab.

## Responsibilities

1. **Load app** - Open browser to SISO Internal
2. **Capture pages** - Screenshot all key pages
3. **Timestamp screenshots** - Save with timestamps
4. **Test flows** - Go through user flows (login, create task, etc.)
5. **Report results** - Log test results with screenshots

## Pages to Test

- `/admin/lifelock/daily` - Daily planning
- `/admin/lifelock/weekly` - Weekly view
- `/admin/lifelock/stats` - Statistics
- `/admin/tasks` - Task management
- `/admin/settings` - Settings

## Test Flows

1. **Login Flow** - Sign in, verify dashboard
2. **Create Task** - Add new task, verify appears
3. **Daily Planning** - Create morning routine
4. **Weekly View** - Navigate week

## Tech Stack

- Playwright CLI for automation
- Screenshots saved to `/tmp/`
- Results logged with timestamps

## Skills Needed

- Playwright CLI
- Screenshot & snapshot
- Console error checking
- File system for reports
