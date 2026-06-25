# Balemuya - Location-Based Service Marketplace

Balemuya is a location-based service marketplace that connects customers with verified skilled professionals such as electricians, plumbers, satellite dish installers, and other service providers. The platform enables customers to discover nearby professionals, post service requests, book services, communicate directly, and review completed work, while helping professionals increase their visibility, build credibility, and access new job opportunities.

---

## Problem Statement

Many skilled professionals rely on traditional advertising methods such as flyers, referrals, and word-of-mouth to find customers. This often limits their visibility, makes it difficult to build a professional reputation, and creates challenges for customers trying to find trusted service providers nearby.

Balemuya was developed to bridge this gap by providing a centralized digital platform that connects customers with verified professionals through location-based matching, booking workflows, and reputation management features.

---

## Key Features

### Customer Features

* User registration and authentication
* Search nearby professionals using geolocation
* View professional profiles and ratings
* Post service requests and job opportunities
* Book professionals directly
* Real-time notifications
* Rate and review completed services
* Report disputes or service-related issues

### Professional Features

* Professional registration and profile management
* Verification and approval workflow
* Apply for available service requests
* Manage bookings and job applications
* Receive customer requests and notifications
* Build reputation through ratings and reviews
* Track completed jobs and service history

### Administration Features

* Professional verification and approval
* User management
* Service category management
* Platform moderation
* Report and dispute handling
* Conflict resolution workflows
* System monitoring and administration

### Platform Features

* Real-time location-based service discovery
* Nearby professional recommendations
* Booking and scheduling workflows
* Reputation and rating system
* Telegram Bot integration
* Web application support
* Mobile application support
* Notification system
* Role-based access control

---

## My Contribution

### Backend & Telegram Bot Developer

As part of a three-member Software Engineering final-year project team, I was responsible for:

* Designing and developing RESTful APIs
* Implementing core business logic and workflows
* Authentication and authorization systems
* Professional verification workflows
* Job application and booking workflows
* User and role management
* Database design and backend architecture
* Telegram Bot integration
* Administrative backend services
* Platform moderation and reporting workflows

---

## System Workflow

### Professional Verification

1. Professional creates an account.
2. Professional submits verification information.
3. Administrator reviews submitted information.
4. Administrator approves or rejects the application.
5. Verified professionals become visible on the platform.

### Service Booking

1. Customer searches for nearby professionals.
2. Customer views professional profiles and ratings.
3. Customer submits a booking request.
4. Professional accepts the request.
5. Service is completed.
6. Customer provides rating and feedback.

### Job Marketplace Workflow

1. Customer posts a service request.
2. Professionals apply for the available job.
3. Customer reviews applicants.
4. Customer selects a professional.
5. Work is completed.
6. Ratings and reviews are recorded.

---

## Technology Stack

### Backend

* Django
* Django REST Framework (DRF)
* PostgreSQL
* Cloudinary Cloude storage
* Chapa Api
* JWT Authentication

### Frontend
*Next Js
* React.js

### Mobile Application

* Flutter

### Integration

* Telegram Bot API

### Location Services

* Geolocation Services
* Real-Time Location Matching

---

## Project Architecture

```text
Customer Web Application
          │
          ▼
    Django REST API
          │
 ┌────────┼────────┐
 ▼        ▼        ▼
Users   Jobs   Bookings
          │
          ▼
   PostgreSQL Database
          │
          ▼
 Telegram Bot Services

Professional Web Application
          │
          ▼
      Mobile App
```

---

## Project Links

### Repository
https://github.com/balemuya-LSMP/Balemuya-backend/

### Liveve Demo
https://balemuya-fe.vercel.app

### Telegram Bot

https://t.me/balemuyaBot

---

## Recognition

🏆 **Awarded 3rd Place in the Software Engineering Faculty Final Year Project Competition**

The project was recognized for providing a practical technology-driven solution that improves professional visibility, customer access to trusted service providers, and digital service delivery through location-based matching and reputation management.

---

## Team

This project was developed as a Final Year Software Engineering Project.

### Team Roles

* Backend & Telegram Bot Development — Yikeber Misganaw
* Frontend Development — Ephrem Habtamu
* Mobile Application Development — Esubalew Kunta

---

## Future Enhancements

* AI-powered professional recommendations
* Advanced analytics and reporting
* Service demand forecasting
---


