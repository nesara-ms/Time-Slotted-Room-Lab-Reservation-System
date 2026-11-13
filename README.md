# Time-Slotted-Room-Lab-Reservation-System
A Django-based room and laboratory reservation system that manages hourly time slots, prevents double bookings, and streamlines resource allocation for universities and collaborative workspaces.

A web application developed as part of the **SKILL CLASS journey at PES College of Engineering (PESCE)**. The project focuses on simplifying the reservation and management of university meeting rooms, laboratories, and shared equipment through structured time-slot scheduling.

## 🎓 Academic Context

- **Institution:** PES College of Engineering (PESCE)
- **Activity:** SKILL CLASS
- **Project:** Time-Slotted Room & Lab Reservation System
- **Development Approach:** Phase 1 & Phase 2

This project is undertaken as part of the SKILL CLASS activity, which encourages students to identify real-world problems, develop practical solutions, and strengthen their technical and problem-solving skills through hands-on implementation.

## 📌 Problem Statement

**9. Time-Slotted Room & Lab Reservation System**

University research groups and co-working spaces suffer from double-booked meeting rooms and conflict over equipment availability.

## 💡 Proposed Solution

The Time-Slotted Room & Lab Reservation System is designed to provide a centralized platform where users can view resource availability, request reservations for specific time slots, and manage bookings efficiently.

The system aims to minimize scheduling conflicts, improve resource utilization, and introduce a structured approval process for room and laboratory reservations.

## 🎯 Key Objectives

- Simplify the reservation process for university rooms and laboratories.
- Prevent overlapping bookings and scheduling conflicts.
- Provide a clear visual representation of resource availability.
- Establish an organized approval mechanism for reservation requests.
- Improve transparency and efficient utilization of shared resources.

## ✨ Core Features

### 1. Visual Calendar View
- Display hourly availability of rooms, laboratories, and equipment.
- Allow users to identify available and occupied time slots.
- Provide a structured view of existing reservations.
- Help users make informed booking decisions.

### 2. Conflict Prevention
- Implement form validation to reject overlapping reservation times.
- Prevent multiple users from reserving the same resource for conflicting time slots.
- Validate booking dates, start times, and end times.
- Maintain consistency in reservation records.

### 3. Approval Hierarchy
- Introduce a moderation queue for reservation requests.
- Allow designated room managers to review booking requests.
- Provide options to approve or decline reservations.
- Maintain booking statuses to track the approval process.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web application framework |
| HTML5 | Page structure |
| CSS3 | Styling and layout |
| JavaScript | Client-side interactions |
| SQLite | Database management |
| Visual Studio Code | Development environment |
| Git & GitHub | Version control and project hosting |

## ⚙️ Project Development

The project follows a two-phase development approach as part of the SKILL CLASS activity.

### Phase 1 – Problem Identification & Planning
- Understanding the given problem statement.
- Identifying challenges in existing room and laboratory reservation processes.
- Defining project objectives and proposed functionality.
- Planning the application workflow and system requirements.

### Phase 2 – Design & Implementation
- Developing the web application using Django.
- Implementing reservation management functionality.
- Designing booking forms and resource management interfaces.
- Implementing validation to prevent scheduling conflicts.
- Developing the approval workflow for room managers.
- Testing the application and refining its functionality.

## 📂 Project Structure

```text
Time-Slotted-Room-Lab-Reservation-System/
│
├── bookings/
├── config/
├── templates/
├── static/
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

*Note: The directory structure may vary depending on the final implementation.*

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Django
- Visual Studio Code
- Git

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/YOUR-USERNAME/Time-Slotted-Room-Lab-Reservation-System.git
```

**2. Navigate to the project directory**

```bash
cd Time-Slotted-Room-Lab-Reservation-System
```

**3. Create a virtual environment**

```bash
python -m venv venv
```

**4. Activate the virtual environment (Windows)**

```powershell
venv\Scripts\activate
```

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

**6. Apply database migrations**

```bash
python manage.py migrate
```

**7. Start the development server**

```bash
python manage.py runserver
```

Open the following address in your browser:

```text
http://127.0.0.1:8000/
```

## 📈 Learning Outcomes

Through this project, the development process provides practical exposure to:

- Python and Django web development.
- Database design and management.
- CRUD operations and form handling.
- Server-side validation and booking conflict detection.
- Authentication and role-based access concepts.
- Software development lifecycle and collaborative problem-solving.
- Git and GitHub version control.

## 👨‍💻 Academic Project

Developed as part of the **SKILL CLASS – Phase 1 & Phase 2** activity at **PES College of Engineering (PESCE)**.

---

*Building practical solutions through learning, experimentation, and implementation.*
