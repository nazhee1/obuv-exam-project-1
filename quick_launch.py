from app import ensure_database, ShoeStoreApp
ensure_database()
app=ShoeStoreApp()
app.after(1000, app.destroy)
app.mainloop()
