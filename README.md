# Give & Take - Item Sharing Platform

"Give & Take" is a web application built with Django that allows users to easily give away items they no longer need and find items they want, creating a community of sharing and reuse.

## Project Background

This project was originally a group project for the course "ERB-SCOPE, Python網站框架開發助理證書 (PE081DS-7)". It has since been remastered from a single-app architecture into a more robust three-app design, and has been significantly enhanced with a focus on user experience and a modern, clean UI.

## Key Features

*   **User Management:**
    *   User registration using an 8-digit phone number.
    *   Secure login and session management.
    *   Password change and reset functionality.

*   **Item Sharing & Discovery:**
    *   **Give:** Users can post items with a name, description, type, and up to six images. The form is enhanced with interactive image previews before uploading.
    *   **Take:** Users can browse a list of available items.
    *   **Search & Filter:** The item list is fully searchable and can be filtered by category, providing a powerful way for users to find what they need.
    *   **History:** Logged-in users can view a personal history of items they have given and taken.

*   **User Experience (UI/UX):**
    *   **Unified Interface:** A consistent and modern design is used for both guests and logged-in users, with a unified card design for all items.
    *   **Streamlined Navigation:** A clean, user-centric navigation bar features a dropdown menu for logged-in users to easily access their profile, history, and settings.
    *   **Interactive Item Cards:** Item cards feature a zoom-on-hover effect, relative timestamps (e.g., "Posted 2 hours ago"), and a modal with a carousel for multiple images.
    *   **Image Previews:** The item creation form includes interactive image previews, allowing users to see their uploaded images before submitting.
    *   **Guest Access:** Guests can browse, search, and filter all available items, providing a rich experience even before registration.

*   **Administration:**
    *   A Django admin interface for site management, with an enhanced dashboard featuring charts and tables for at-a-glance insights.
    *   System administrators can view user activity logs.
    *   Admins can reset user passwords.

*   **Logging:**
    *   All major user actions are logged for administrative review.

## Getting Started

Follow these instructions to get a local copy of the project up and running for development and testing purposes.

### Prerequisites

*   Python 3.10 or higher
*   `pip` for package management

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd gat_project
    ```

2.  **Create and activate a virtual environment:**
    *   On Windows:
        ```bash
        python -m venv .venv
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    This will set up the necessary tables in the SQLite database.
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser:**
    This account will have access to the Django admin panel. Follow the prompts to set a username, email, and password.
    ```bash
    python manage.py createsuperuser
    ```

6.  **Configure Admin Privileges:**
    After creating a superuser, you need to grant them admin access within the application itself.
    *   First, run the development server:
        ```bash
        python manage.py runserver
        ```
    *   Navigate to the Django admin panel at `http://127.0.0.1:8000/admin/` and log in with the superuser credentials you just created.
    *   In the admin panel, go to the **"User Profiles"** section and click **"Add user profile"**.
    *   Select your superuser account from the **"User"** dropdown.
    *   Enter a phone number. This is required for logging into the site's admin dashboard.
    *   Check the **"Is admin"** box to grant admin privileges.
    *   Click **"Save"**.

7.  **Log in as an Admin:**
    You can now navigate to the main site at `http://127.0.0.1:8000/` and log in using the phone number you just entered to access the admin dashboard and features.

## Testing

The project includes a comprehensive test suite to ensure code quality and functionality.

To run all tests, make sure your virtual environment is activated and run the following command:
```bash
python manage.py test
```

To run tests for a specific application (e.g., `users`, `items`, or `logs`):
```bash
# Run tests for the 'users' app
python manage.py test users

# Run tests for the 'items' app
python manage.py test items

# Run tests for the 'logs' app
python manage.py test logs
```

## Code Quality

This project uses `pylint` with the `pylint-django` plugin to enforce code quality and style. The configuration is defined in the `.pylintrc` file.

To check the codebase, ensure you have installed the dependencies from `requirements.txt` (which includes `pylint` and `pylint-django`), and then run the following command from the project root:

```bash
pylint users/ items/ logs/
```

## Project Structure

The project is organized into three main Django apps:

*   `/users`: Handles all user-related functionality, including authentication, registration, profiles, and views for the main index page.
*   `/items`: Manages item-related logic, such as creating, editing, deleting, and taking items.
*   `/logs`: Provides a service for logging user actions and an interface for administrators to view those logs.
*   `/templates`: Contains the base HTML templates and the main `index.html`.
*   `/static`: Stores static assets like images and CSS.
