
# Vehicle Record Management System

A Python-based desktop application for efficiently managing vehicle records using a modern GUI and a structured SQL database.

---

## Overview
The **Vehicle Record Management System** is a desktop application developed with **Python and CustomTkinter** that allows administrators to store, manage, and retrieve vehicle-related information efficiently.  
The system uses an **admin login mechanism** to ensure authorized access to vehicle records.

---

## Admin Login Credentials
Use the following credentials to access the system:

- **Admin Email:** admin@example.com  
- **Admin Password:** admin123  

> *Note: These credentials are for demonstration and educational purposes only.*

---

## Key Features
- Secure admin login system
- Modern and responsive GUI using CustomTkinter
- Add and manage vehicle records
- Persistent data storage using SQL database
- Clean separation of UI and database logic
- Easy to use and maintain

---

##  Tech Stack
- **Language:** Python 3  
- **GUI Framework:** CustomTkinter, Tkinter  
- **Database:**  SQL  
- **Other Tools:** Xampp

---

## Project Structure
app_ctk_login.py # Main application (GUI + login + logic)
db_init.sql # Database schema and admin credentials setup
requirements.txt # Python dependencies
README.md # Project documentation






---

## Installation & Setup

```bash
1-
git clone <repository-url>
cd vehicle-record-management-system

---

2-
pip install -r requirements.txt

3-

Run the db_init.sql file using SQL or any compatible SQL tool to create tables and admin credentials.

4. -
python app_ctk_login.py

