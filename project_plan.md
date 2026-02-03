# CSC.289 Programming Capstone Project Plan
 Project Name: BookHive \
 Team Number: 1 \
 Team Project Manager / Scrum Master: James Hardin

## Team Member Details

| Name | Email | Role |
|---|---|---|
| Alex Shelley | ashelley@my.waketech.edu | Software Engineer |
| Alejandro Jesus Vilchis-Orozco | ajvilchisorozco@my.waketech.edu | Software Engineer |
| Charles Rasberry | cfrasberry@my.waketech.edu | Software Engineer |
| Yazeed Nedal Ahmad Herz Allah | ynherzallah@waketech.edu | Software Engineer |
| Matthew Dove | madove@my.waketech.edu | Software Engineer |
| Emmanuel Rudy Dawah | erdawah@my.waketech.edu | Software Engineer |



## Project Goal
The goal BookHive is to provide library and bookstore managers’ informatics support to improve the organization of business operations and to provide insights for managerial decisions to improve decision making through integrated business intelligence dashboards.



## Project Objectives
Deliver a locally runnable MVP that supports core manager workflows—secure sign-in, book inventory CRUD, search/filter, member CRUD, checkout/return with due dates, and manual sales recording—meeting all Must-Have (MoSCoW “M”) requirements by the final sprint.

Provide actionable insights by implementing BI dashboards with at least three charts (e.g., checkouts by genre, top titles, sales by month) plus CSV export for books, members, loans, and sales; verify charts and exports using a seeded demo dataset.

Meet quality and security targets: passwords hashed (bcrypt), JWT-based authentication, input validation with Pydantic, and basic manual QA + smoke tests so key pages load in ≤2 seconds with a dataset of ~5,000 titles on mid-range hardware and provide setup documentation enabling a new dev to run the project locally..



## Scope

### Included
- Manager-only web app (single manager role)
- Books CRUD + metadata enrichment via OpenLibrary ISBN lookup
- Inventory tracking: stock levels per title and stock adjustments; low/zero-stock views with configurable threshold.
- Location mapping: aisle/shelf assignment and display.
- Members: registration & management (CRUD).
- Circulation: checkout/return workflows with due dates and due/overdue lists.
- Simple sales capture: manual sales records (date, title, quantity, unit price) and stock decrement—no payment processing.
- BI dashboards and on-demand reports; CSV exports.
- OpenLibrary API lookup by ISBN for metadata enrichment (title/authors/year/cover).


### Excluded
- Customer-facing login / patron self-service
- POS features (payments, receipts) and payment processing
- Email/SMS notifications
- Role-based access control beyond the single manager role
- Vendor purchase orders and automated reordering
- Advanced BI forecasting/recommendations (beyond basic descriptive dashboards).



## Project Assumptions
- All team members have access to MS Teams, Trello, and GitHub.
- Developers can run the solution locally on Windows/macOS machines with required tooling (Node/Vue, Python, SQL Server).
- Internet access is available for dependency installs and repo sync.
- OpenLibrary API is reachable (or cached) during development/demo.
- Seeded sample datasets exist for testing and demo.



## Project Constraints
- Course timeline and sprint deadlines constrain scope and feature depth.
- Novice development team: the stack must remain simple and well-documented.
- Priority is working software each sprint (Agile/Scrum); incomplete “nice-to-haves” may be deferred.
- Local-first hosting for demos; cloud deployment (e.g., AWS) is optional.
- Performance targets must be met on mid-range developer hardware.



## Projct Resources Required

- People: 1 Project Manager/Scrum Master (James Hardin) + 6 Software Engineers.
- Hardware (dev): ≥8 GB RAM, ≥4 CPU cores, ≥20 GB free disk per developer workstation; stable internet.
- Software: Python 3.x, FastAPI, SQLAlchemy + mysqlclient, MySQL, Node.js(dev), Nuxt/Vue.js, Plotly, Git client, VS Code (or equivalent IDE).
- Services/tools: GitHub (repo + PRs), Trello (backlog/sprints), MS Teams (chat/meetings/files).
- External dependency: OpenLibrary API for book metadata lookup.



## Team Collaboration and Communication

- MS Teams: daily communication in the team channel via posts and chat messages; weekly sprint meeting via Teams call for planning/collaborating/retrospectives; files shared in the Teams Files tab.
- Trello: Scrum board for backlog, sprint planning, and task tracking (Backlog / To Do / In Progress / In Review / Done). Each card maps to a user story or task with acceptance criteria and a checklist.
- GitHub: source control with feature branches per Trello card; pull requests required for merges to main; code review before merge.



## Project Documentation
- Markdown: the authoritative project plan, architecture notes, setup instructions, and sprint notes stored in the project’s GitHub repository.
- MS Word: formal submissions stored in the MS Teams channel Files tab; exported PDFs when required.
- Diagrams: ERD and flow diagrams stored in the repo (images) and referenced from Markdown/Word as needed.



## Project Management Plan and Methodologies

- Methodology: Agile/Scrum with short iterations (1–2 weeks) aligned to the course schedule.
- Ceremonies: sprint planning, weekly sync, sprint review/demo, and sprint retrospective.
- Definition of Done: code merged to main via pull request, acceptance criteria met, basic manual QA pass, feature documented, and demo-ready using seeded data.
- Backlog management: Project manager maintains product backlog in Trello; sprint backlog committed during planning; scope changes handled via MoSCoW reprioritization.

### Version Control:
- Branch naming: `feature/<trello-card-id>-short-title`.
- Pull request required for merges to `main`.
- Project manager is code owner of the repo so he will approve pull requests.
- Adhere to squash merge merging practices to keep commit history clean.


