# Units Plan

## Overview
Group the 24 user stories into independently buildable units, ordered by dependency. Each unit gets a `specs/<unit>/` folder with `requirements.md`, `design.md`, and `tasks.md`.

## Proposed Units (in build order)

1. **Unit 1 — Auth & User Management** (US-001 to US-009)
   - Foundation: DynamoDB tables, session management, login/logout, initial admin, CRUD users
   - Must be built first — everything else depends on authenticated users existing

2. **Unit 2 — Folder Management & Assignments** (US-010 to US-015)
   - Folders CRUD, user-folder assignments, folder browsing
   - Depends on Unit 1 (users must exist to assign folders)

3. **Unit 3 — File Upload & Browsing** (US-016 to US-021)
   - File browsing, search, sort, upload via pre-signed URLs, size limit, versioning
   - Depends on Unit 2 (folders must exist to upload into)

4. **Unit 4 — File Download & View-Only Access** (US-022 to US-024)
   - Download via pre-signed URLs, version download, viewer role enforcement
   - Depends on Unit 3 (files must exist to download/view)

## Deliverables
For each unit:
- `specs/<unit>/requirements.md` — User stories and acceptance criteria
- `specs/<unit>/design.md` — Technical design (API, DynamoDB schema, Lambda, React components)
- `specs/<unit>/tasks.md` — Implementation tasks with checkboxes

## Plan

- [x] **Step 1:** Create Unit 1 spec — `specs/unit-1-auth-and-users/`
  - ✅ **Clarified:** Single-table DynamoDB design (all entities in one table)

- [x] **Step 2:** Create Unit 2 spec — `specs/unit-2-folders-and-assignments/`

- [x] **Step 3:** Create Unit 3 spec — `specs/unit-3-file-upload-and-browsing/`

- [x] **Step 4:** Create Unit 4 spec — `specs/unit-4-file-download-and-viewing/`

- [x] **Step 5:** Final review — verify all 24 user stories are covered and unit ordering is correct
