# Hisaab-Kitaab

Collab Expense Tracker is a Django-based web application that helps users collaboratively track and manage shared expenses. It supports multiple users, real-time group chat, and visual insights into spending.

## Features
- Add, edit, and delete group expenses
- Track individual member balances
- Visualize contributions with pie charts
- Real-time group chat using WebSockets
- Responsive and user-friendly interface

## Technologies Used
- Backend: Django, Django Channels
- Frontend: HTML, CSS, JavaScript
- Database: SQLite 
- WebSocket Support: Redis
- Deployment: Daphne, WhiteNoise



Apply migrations:

python manage.py migrate


Run the development server:
python manage.py runserver
daphne collab_expense_tracker.asgi:application

Access the app at:

http://127.0.0.1:8000/

Usage Instructions
Register or log in
Create or join a group
Add expenses and view balances
Use the chat feature to communicate with group members
