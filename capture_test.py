
from app import ShoeStoreApp
app = ShoeStoreApp()
app.after(1000, lambda: app.destroy())
app.mainloop()
