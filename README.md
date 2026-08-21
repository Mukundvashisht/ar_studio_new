AR Studios Website & Project Management App (Flask)

A modern Flask-based website + lightweight CRM/project management app. It combines a marketing site (home/portfolio/pricing/services/about/contact) with an authenticated workspace for managing projects, users, milestones, tasks, activities, notifications, and real-time project chat. Includes an admin CMS to manage users, clients, and featured works, with file uploads.

Key Features
- Authentication and Roles: email+password auth with optional Google OAuth; roles include admin, designer, client (via Flask-Login)
- Role-Aware Access: admins see/manage all projects; designers/clients see assigned projects only
- Dashboard and Analytics: progress charts, recent activities, in-progress highlights, and quick stats
- Project Management: create, view, edit; auto-computed progress from milestones (fallback to tasks), members, and activity tracking
- Milestones and Tasks: CRUD, status transitions, timestamps, automatic project status updates
- Real-time Chat: per-project chat rooms with messages and file attachments; recent messages are persisted
- Admin CMS: manage users, featured works (portfolio items), and clients; upload or link images/files; enforce admin-only controls
- Profile & Settings: edit profile, change password, manage notifications, view activities and assigned projects
- Public Website: home, services, portfolio, pricing, contact, about pages; portfolio and client logos managed in the admin
- File Uploads: stored under static/uploads with unique naming; safe filenames; project-specific and featured-works uploads
- PostgreSQL-backed: SQLAlchemy models with auto table creation on startup; sample data seeding in development

Architecture Overview
- Tech Stack: Flask 3, Flask-SQLAlchemy (SQLAlchemy 2 DeclarativeBase), Flask-Login, Flask-SocketIO, python-dotenv, Jinja2 templates, vanilla JS
- Persistence: PostgreSQL via psycopg2-binary
- Realtime: Socket.IO for project chat
- Structure:
  - app.py: App factory, DB init, Socket.IO, LoginManager, blueprints, error handlers, DB bootstrapping
  - models.py: ORM models: User, Project, ProjectAssignment, Milestone, Task, ChatMessage, Activity, Comment, Notification, FeaturedWork, Client; init_sample_data() for dev/demo
  - routes.py: Public pages, dashboard, search, chart data helpers, template utilities
  - auth_routes.py: Login, register (client/designer), optional Google OAuth, logout, forgot password
  - profile_routes.py: Profile, notifications, edit profile, change password, settings, activities, projects; profile JSON APIs
  - project_routes.py: Projects list/detail/create/edit/assign, milestones management, auto progress/status, chat (Socket.IO), file uploads to chat
  - admin_routes.py: Admin-only user management, client management, featured works management, upload helpers (save/delete)
  - templates/: Jinja2 templates for public, auth, admin, projects, profile
  - static/: CSS/JS plus uploads under static/uploads
  - requirements.txt: Python dependencies

Data Model Highlights
- User: username, email, password_hash, avatar_url, role (admin/designer/client), status flags (active, restricted, banned), timestamps, preferences
- Project: name, description, status (pending/ongoing/complete), department, priority, computed progress, start/end dates, client_name
- ProjectAssignment: mapping users to projects with role label (e.g., Admin, Owner, Team Member)
- Milestone: title, description, status (pending/in_progress/completed), due/completed timestamps, project and creator refs
- Task: title, description, status (todo/in_progress/completed), priority, project/assignee/creator refs, due/completed timestamps
- ChatMessage: content (supports attachment payloads), user, project, timestamp
- Activity: user, optional project, action, description, timestamp (for auditing)
- Comment: comments on projects or tasks
- Notification: user-targeted notifications with type (info/success/warning/error) and read flag
- FeaturedWork: portfolio items (title/category/description/image/project URL/order/active)
- Client: clients with name/logo/icon_class/website/order/active

Core Application Flows
1) Authentication
   - Email/password login with remember option
   - Client and Designer self-registration forms with validation and auto-login
   - Optional Google OAuth (env-driven); creates a user on first login
   - Logout logs an activity and redirects to home

2) Authorization & Access Control
   - Flask-Login protects authenticated routes
   - Admin-only routes via @admin_required decorator
   - Project access guard: users must be assigned or be admin
   - Dashboard gated by user restriction/ban flags (with flash messages)

3) Dashboard (routes.py -> /dashboard)
   - Summaries: total/pending/ongoing/complete based on user-visible projects
   - Progress: computed from milestones (fallback to tasks) with a 24h not_opened flag for new projects
   - Charts: monthly complete/ongoing counts; donut of projects weighted by progress (min 1% visual slice)
   - Recent activities and in-progress projects scoped to user or global for admins

4) Projects Management (project_routes.py)
   - List projects visible to the user
   - Create project: any authenticated user; auto-assign all admins and the creator
   - Edit project: admin-only
   - Assign users: admin-only, replaces non-admin assignments with provided list
   - Detail page: shows tasks, milestones, members; logs first-time "Project Opened" per user
   - Progress & Status: auto-updated by milestone/task completion; status transitions: pending -> ongoing -> complete

5) Milestones & Tasks
   - Create milestones; update milestone status via JSON endpoint (designer/admin only)
   - When milestones complete, project progress recalculates and updates status
   - Tasks participate in progress calculation only if no milestones exist

6) Real-time Project Chat
   - Socket.IO rooms per project: join/leave, send messages
   - Access check: admins unrestricted; others must be assigned
   - Messages persisted; attachments supported via upload endpoint; client emits new_message to the room

7) Admin CMS
   - Users: list, update role (with safeguard against removing last admin), delete (not self / not last admin)
   - Featured Works: create/edit/delete; upload or link images/projects; local file cleanup on replace/delete
   - Clients: create/edit/delete; order and active flags

8) Profile & Account
   - Profile overview: recent activities and assigned projects
   - Notifications listing
   - Edit profile with username/email uniqueness checks; avatar URL
   - Change password with validation; supports users without password (e.g., OAuth-only)
   - Settings placeholder (theme, notifications)
   - Activities paginated view and assigned projects list
   - Delete account flow with confirmation and password verification when applicable

Public Website
- Home aggregates Featured Works and Clients (ordered and limited for home)
- Service, Portfolio, Pricing, Contact, About pages
- Portfolio and Clients content driven by FeaturedWork and Client tables via admin CMS

Setup and Installation
Prerequisites
- Python 3.11+
- PostgreSQL 13+
- (Optional) Docker for local Postgres

Clone and install
- Create virtualenv and install requirements

Windows PowerShell
1) Clone and enter directory
   git clone <your-repo-url>.git
   cd "try3 - Copy"

2) Virtual environment
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

3) Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt

4) Create .env
   SESSION_SECRET=change-this-in-production
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=127.0.0.1
   DB_PORT=5432
   DB_NAME=crm_db
   GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret

5) Ensure database exists
   Create the database named in DB_NAME. The app will auto-create tables.

6) Run (development)
   python app.py
   Visit http://localhost:5000

Environment & Configuration
- Database URI is constructed in app.py from DB_* parts:
  postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
- SESSION_SECRET secures sessions
- ProxyFix applied for reverse-proxy deployments
- Optional switch to SQLite by changing the SQLALCHEMY_DATABASE_URI (commented example in app.py)

Database & Migrations
- Tables created via db.create_all() on startup
- init_sample_data(): seeds demo users/projects/milestones/tasks/activities/notifications in dev when no users exist
- A reset_database() helper exists in app.py for dev schema changes
- Consider adding Alembic migrations for production

Running in Debug and Reload
- python app.py runs Flask-SocketIO server in debug mode on 0.0.0.0:5000
- If using gunicorn in prod, use eventlet/gevent worker classes for Socket.IO

API Endpoints (Auth Required)
- Base blueprint: /api (see api_routes.py)
  Example patterns:
  - GET /api/projects — list projects JSON (role-aware in implementation)
  - POST /api/projects — create project and log Activity
  Extend api_routes.py for additional resources as needed.

Notable Routes
- Public: /, /service, /portfolio, /pricing, /contact-us, /about-us
- Auth: /auth/login, /auth/register, /auth/register-design, /auth/forgot-password, /auth/google_login
- Dashboard: /dashboard
- Projects: /projects, /projects/new, /projects/<id>, /projects/<id>/edit, /projects/<id>/assign, /projects/<id>/milestones, /projects/<id>/chat
- Admin: /admin/users, /admin/featured-works, /admin/clients, plus their CRUD paths
- Profile: /profile/ (index), /profile/notifications, /profile/edit, /profile/change-password, /profile/settings, /profile/activities, /profile/projects

Realtime Chat Implementation
- Socket events: join_project, leave_project, send_message; room: project_{id}
- Message persistence via ChatMessage model
- Attachments via POST /projects/<id>/chat/upload; saved under static/uploads/projects/<id>/
- Broadcasts include user, avatar, message text or attachment metadata

File Uploads and Storage
- Admin uploads for featured works: static/uploads/featured_works/
- Chat attachments: static/uploads/projects/<id>/
- Unique filenames with UUIDs or timestamps; local file cleanup when replacing/deleting
- In production, consider external object storage (S3/GCS) or persistent volumes

Security Considerations
- Role checks on admin and project routes
- Assignment-based access for project resources and chat
- Basic input validation on forms; consider CSRF protection for mutating endpoints
- Passwords hashed via Werkzeug; supports OAuth-only accounts without local password

Deployment
- Set environment variables on your platform
- Ensure Postgres reachable from app
- Serve static files and persist uploads
- Example gunicorn command with eventlet:
  pip install eventlet
  gunicorn -k eventlet -w 1 app:app --bind 0.0.0.0:5000
- Alternatively, run python app.py behind a reverse proxy (Nginx) with a process manager

Troubleshooting
- column user.role does not exist: development helper may reset DB on schema drift; see app.py logic
- DB connection errors: verify DB_* envs and network access
- Upload failures: ensure static/uploads/ exists and is writable
- Google OAuth missing: ensure GOOGLE_OAUTH_* envs or use email/password auth

Development Tips
- Keep dependencies updated and pinned
- Add Alembic migrations for evolving models
- Consider CSRF and additional validation for production hardening
- Write unit tests for routes and role checks

License
- Add your preferred license (e.g., MIT) if distributing

Contributing
- Open issues/PRs describing changes; discuss larger contributions first
