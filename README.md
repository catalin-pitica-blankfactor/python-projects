# 🚀 FastAPI User and Group Management Application

---

## **Description**

This application it is built based on clean arhitecture using FastAPI and SQLAlchemy to manage users and groups with features like: 
* CRUD operations
* many-to-many relationships 
* background tasks
* JSON data handling
* Validation and Error Handling
---

## **Features**

### **User Management**
- create, read, update, delete users
- assign a group to a user during creation
- store additional data (URL) as JSON
- background task to process the content of the url

### **Group Management**
- create, read, update, delete group
- validate group existing during user creation or update 

### **Relationships**
- many-to-many relationship between users and groups

---
## **Tehnologies used**
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- httpx
- JSON