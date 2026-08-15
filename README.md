# 🎭 BDRegistro - Facial Recognition Attendance & Automated WhatsApp Notification System

![Java](https://img.shields.io/badge/Java-17+-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Facial_Recognition-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![WhatsApp API](https://img.shields.io/badge/WhatsApp_API-Integration-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)

## 📌 Overview

**BDRegistro** is an Object-Oriented Programming (OOP) application designed to automate attendance management using real-time facial recognition. Developed primarily in Java, the system captures live video feeds, identifies registered individuals through biometric model matching, records attendance timestamps into a local SQL database, and dispatches automated confirmation notifications via a WhatsApp API service.

This project demonstrates key Object-Oriented Design Principles (Encapsulation, Inheritance, Polymorphism, Abstraction) integrated with computer vision frameworks, database persistence, and external RESTful API consumption.

---

## ✨ Key Features

- **Facial Recognition Engine**: Real-time detection and biometric identification using pre-trained feature extraction models.
- **Automated Attendance Logging**: Instant registration of user check-ins and check-outs with exact timestamps.
- **Local SQL Storage**: Structured database schema managing user profiles, and historical attendance logs.
- **Automated WhatsApp Alerts**: Instant notification delivery to users/parents upon successful attendance verification via REST API.
- **Modular OOP Architecture**: Robust decoupling of business logic, database queries, visual interfaces, and third-party services.

---

## 🛠️ Tech Stack

- **Language**: Java (JDK 17+)
- **Computer Vision / ML**: OpenCV 
- **Database**: Local SQL (MySQL) via JDBC
- **API & Messaging**: REST API Integration  for WhatsApp Gateway (Twilio)
- **GUI**: Java Swing / JavaFX
- **Build System**: Maven / Gradle

---

## 🏗️ System Architecture & Design Patterns

The project follows clean architecture practices and OOP design patterns:

- **Model-View-Controller (MVC)**: Separates UI components, business logic, and database entities.
- **Data Access Object (DAO)**: Encapsulated SQL operations for user records and attendance logs.
- **Singleton Pattern**: Ensures single instance management for Database Connections and API HTTP Clients.
- **Strategy Pattern / Interfaces**: Abstracted notification module (`NotificationService`), allowing easy swapping between messaging providers (WhatsApp, Email, SMS).

---
