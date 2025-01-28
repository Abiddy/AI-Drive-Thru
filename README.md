# 🚀 AI Drive-Thru System

An AI-powered **drive-thru ordering system** that processes natural language orders, tracks them in real-time, and supports cancellations with an interactive stats display.

---

## 🎥 Demo  
![ScreenRecording2025-01-28at11 29 18AM-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/9d3767ac-83a6-48e0-a820-936136641784)

---

## ✨ Features  
✅ **Natural language order processing**  
✅ **Real-time order tracking**  
✅ **Order cancellation support**  
✅ **Interactive stats display** 

---

## 🛠 Backend Setup  

1. **Navigate to the backend directory**  
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   python3 -m pip install uvicorn fastapi python-dotenv requests
   echo "TOGETHER_API_KEY=your_api_key_here" > .env
   uvicorn main:app --reload
   
## 🛠 Fronted Setup  

2. **Navigate to the frontend directory**  
   ```bash
   # Navigate to frontend directory
   cd frontend

   # Install dependencies
   npm install
    
   # Run the development server
   npm run dev



   

