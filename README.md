# 🚀 AI Drive-Thru System

An AI-powered **drive-thru ordering system** that processes natural language orders, tracks them in real-time, and supports cancellations with an interactive stats display.

---

# Live Application Link: [AI Drive-Thru System](https://appealing-determination-production.up.railway.app/)

## 🎥 Demo  
![ScreenRecording2025-01-28at11 29 18AM-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/9d3767ac-83a6-48e0-a820-936136641784)

---

## ✨ Features  
✅ **Live Application**  
✅ **Natural language order processing**  
✅ **Real-time order tracking**  
✅ **Order cancellation support**  
✅ **Interactive stats display**
✅ **Multi-tenant architecture**
✅ **User authentication & authorization**
✅ **PostgreSQL database with migrations**
✅ **Input validation & error handling**
✅ **API documentation (Swagger UI on /docs)**

## 🔒 Security Features
- JWT-based authentication
- Password hashing
- Rate limiting
- Input sanitization
- CORS protection

---

## 🛠 Backend Local Setup  

1. **Navigate to the backend directory**  
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   python3 -m pip install uvicorn fastapi python-dotenv requests
   echo "TOGETHER_API_KEY=your_api_key_here" > .env
   uvicorn main:app --reload
   
## 🛠 Fronted Local Setup  

2. **Navigate to the frontend directory**  
   ```bash
   # Navigate to frontend directory
   cd frontend

   # Install dependencies
   npm install
    
   # Run the development server
   npm run dev

   # You will need to create a .env file in the frontend directory with the following variables:
   VITE_API_URL=http://localhost:8000 
   Clerk Keys for authentication



   

