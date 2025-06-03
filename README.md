# Invoice Tracker Web App
#### Video Demo: [Watch Now](https://youtu.be/hXe5LJzw9hg)
#### Description:

Invoice Tracker is a full-stack web application designed to help freelancers, consultants, and small business owners efficiently manage their billing process. It enables users to create and manage client information, generate itemized invoices, record payments, and monitor outstanding balances via a financial dashboard.

The application is developed using **Flask (Python)** for the backend, **HTML/CSS/JavaScript** for the frontend, and **SQLite** for the database. Users can also export invoices to PDF using **WeasyPrint** and visualize data through simple bar charts rendered via **Chart.js**.

---

## Functional Overview

### 1. **User Authentication**
Users can register, log in, and log out securely. Passwords are hashed using Werkzeug for security. Session tracking ensures that users can only access their own data.

### 2. **Client Management**
Once logged in, users can manage clients using a CRUD interface:
- **Create:** Add new clients with contact info and address.
- **Read:** View a list of all clients.
- **Update:** Edit client details.
- **Delete:** Remove client records.

Each client is linked to a specific user via a foreign key relationship.

### 3. **Invoice Generation**
Users can create invoices by:
- Selecting a client
- Providing an invoice and due date
- Adding up to five individual line items with descriptions, quantities, and prices

Each invoice is stored in the `invoices` table and its associated line items are stored in the `invoice_items` table.

### 4. **Payment Tracking**
Users can add payments to invoices. If total payments match or exceed the invoice total, the invoice status updates to “paid.” Partial payments are supported and visible on each invoice detail page.

### 5. **Dashboard**
A dashboard shows total paid, unpaid, and upcoming due invoices. A simple bar chart (powered by Chart.js) offers a visual overview of payment statuses.

### 6. **PDF Export**
Each invoice can be downloaded as a PDF. The app uses WeasyPrint to render HTML templates into downloadable PDFs with styling and itemized tables.

---

## File Breakdown

### `app.py`
The main application file containing:
- All Flask routes
- Database queries
- Session and authentication logic
- Invoice and client management functions
- PDF export route using WeasyPrint

### `helpers.py`
Currently includes the `login_required` decorator to ensure protected routes are only accessible to logged-in users. Additional reusable helpers could be added here in future iterations.

### `schema.sql`
Defines the database schema for:
- `users`: stores user credentials
- `clients`: stores client contact information
- `invoices`: stores invoice metadata
- `invoice_items`: stores line items linked to invoices
- `payments`: stores payment history per invoice

### `/templates/`
Contains all HTML templates rendered by Flask:
- `layout.html`: the base layout with a shared header/nav
- `index.html`: the main dashboard view
- `register.html`, `login.html`: user auth templates
- `clients.html`, `add_client.html`, `edit_client.html`: client interfaces
- `invoices.html`, `new_invoice.html`, `view_invoice.html`: invoice views
- `invoice_pdf.html`: simplified printable version for PDF generation

### `/static/styles.css`
Custom CSS styles for the frontend. Clean, minimalist look, fully responsive using mobile-friendly elements.

### `requirements.txt`
Lists Python dependencies: Flask, Werkzeug, and WeasyPrint.

### `invoice.db`
The local SQLite database (created after running `schema.sql`). Not included in the GitHub repo per best practices but easy to generate.

---

## Design Choices

### 1. **Flask + SQLite**
Flask was chosen for its simplicity and alignment with CS50’s taught technologies. SQLite allows easy local testing and fits the scope of a small-scale finance app.

### 2. **Separation of Concerns**
HTML templates are modular and use Jinja templating inheritance. Each function handles a single responsibility, from route logic to database commits.

### 3. **PDF Over Email**
While email sending was considered, generating PDFs provides tangible value without email server complexity. Future versions may include emailing invoices directly.

### 4. **Scalability**
Tables were normalized to support multi-user functionality. Each user has their own clients and invoices.

### 5. **Security**
All sensitive routes are protected by the `login_required` decorator. Passwords are hashed, and SQL queries are parameterized to prevent injection attacks.

---

## 🚀 Available on Gumroad

You can now get the complete source code and deploy-ready package of this Invoice Manager Flask App on Gumroad:

👉 [Get it here](https://aabiskar.gumroad.com/l/agpyxn) – One-time purchase, fully open-source, MIT license.

---

## Challenges

- Designing dynamic form fields for invoice line items without JS frameworks
- Formatting consistent PDF outputs from HTML
- Handling edge cases with payment totals and due dates

---

## Future Improvements

- Add drag-and-drop invoice item builder
- Implement recurring invoice logic
- Add dark mode toggle
- Integrate with Stripe or PayPal for live payment processing
- Deploy to Fly.io or Render.com

---

## Citations

This project was developed by me as part of the CS50x final project. The following tools were used for guidance and assistance:

- **OpenAI ChatGPT**: Used for architectural advice, code debugging, and generating example logic
- **GitHub Copilot**: Assisted with autocompletion in VS Code
- **WeasyPrint Docs**: Referenced for configuring PDF generation
- **Chart.js Docs**: Used to build the dashboard chart

All core logic and code integration decisions were made and implemented by me.

---

## License

This project is released under the MIT License.
