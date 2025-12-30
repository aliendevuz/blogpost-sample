from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# CORS middleware qo'shish
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Blog modeli
class Blog(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: str

# Database faylining manzili
DATABASE = "blogs.db"

# Databaseni tayyorlash
def init_database():
    """Database va blogs jadvalni yaratish"""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Blogs jadvalini yaratish
        cursor.execute('''
            CREATE TABLE blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 3 ta sample blogni qo'shish
        sample_blogs = [
            ("FastAPI bilan RESTful API qurish", 
             "FastAPI - bu zamonaviy va tez Python web framework. Unda type hints va async/await qo'llab-quvvatlanadi.", 
             "Sevara"),
            ("Python dasturlashni o'rganish", 
             "Python - bu eng oson o'rganish uchun mos bo'lgan dasturlash tili. Uni har xil sohalarda ishlatish mumkin.", 
             "Ali"),
            ("Veb sayt qurish asoslar", 
             "Frontend va backend qo'llab-quvvatlovchi naqshni tushunish veb sayt qurish uchun muhim.", 
             "Nodira")
        ]
        
        for title, content, author in sample_blogs:
            cursor.execute('''
                INSERT INTO blogs (title, content, author, created_at) 
                VALUES (?, ?, ?, ?)
            ''', (title, content, author, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        print("✅ Database yaratildi va 3 ta sample blog qo'shildi!")

# Database bilan ishlash funksiyalari
def get_db_connection():
    """Database ulanishini ochish"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Barcha bloglarni olish (GET - http://localhost:8000/blogs)
@app.get("/blogs", response_model=List[Blog])
async def get_all_blogs():
    """Barcha bloglarni qaytaradi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content, author, created_at FROM blogs ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    blogs = [Blog(
        id=row['id'],
        title=row['title'],
        content=row['content'],
        author=row['author'],
        created_at=row['created_at']
    ) for row in rows]
    
    return blogs

# Bitta blogni ID bo'yicha olish
@app.get("/blogs/{blog_id}", response_model=Blog)
async def get_blog(blog_id: int):
    """ID bo'yicha bitta blogni qaytaradi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, content, author, created_at FROM blogs WHERE id = ?', (blog_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return Blog(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            author=row['author'],
            created_at=row['created_at']
        )
    return {"error": "Blog topilmadi"}

# Yangi blog qo'shish
@app.post("/blogs", response_model=Blog)
async def create_blog(blog: Blog):
    """Yangi blog qo'shadi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    created_at = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO blogs (title, content, author, created_at) 
        VALUES (?, ?, ?, ?)
    ''', (blog.title, blog.content, blog.author, created_at))
    
    conn.commit()
    blog_id = cursor.lastrowid
    conn.close()
    
    return Blog(
        id=blog_id,
        title=blog.title,
        content=blog.content,
        author=blog.author,
        created_at=created_at
    )

# Serverni ishga tushirish
if __name__ == "__main__":
    import uvicorn
    init_database()
    uvicorn.run(app, host="0.0.0.0", port=8000)

