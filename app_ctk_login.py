# app_ctk_login.py
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

#############################################
#         DATABASE CONFIGURATION
#############################################
DB = dict(
    host="127.0.0.1",
    user="root",
    password="",
    database="rental"
)

#############################################
#           DATABASE HELPERS
#############################################
def db_conn():
    try:
        return mysql.connector.connect(**DB)
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not connect: {e}")
        return None

def db_fetch(query, params=()):
    conn = db_conn()
    if not conn: return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        return cur.fetchall()
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        return []
    finally:
        try:
            cur.close(); conn.close()
        except: pass

def db_exec(query, params=()):
    conn = db_conn()
    if not conn: return False, "Connection Failed"
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        try:
            cur.close(); conn.close()
        except: pass

#############################################
#           ADMIN LOGIN HELPERS
#############################################
def verify_admin(username, password):
    """Plain-text login (NO HASHING)."""
    r = db_fetch("SELECT * FROM admins WHERE username=%s", (username,))
    if not r:
        return False, "User not found"
    # r is list of dicts; safe access to 'password' key expected
    if 'password' not in r[0]:
        return False, "Admin table missing 'password' column"
    return (r[0]['password'] == password), ("OK" if r[0]['password'] == password else "Incorrect password")

#############################################
#       QUICK VEHICLE & CUSTOMER HELPERS
#############################################
def get_rate(vehicle_id):
    r = db_fetch("SELECT rate_per_day FROM vehicles WHERE id=%s", (vehicle_id,))
    if not r: return None
    try:
        return float(r[0]['rate_per_day'])
    except:
        return None

#############################################
#                 UI APP
#############################################
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vehicle Rental Management")
        self.state("zoomed")                    # start maximized
        self.configure(fg_color="white")
        self._setup_styles()
        self._create_navbar()
        self._create_container()
        self.switch("vehicles")

    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("default")
        except:
            pass
        # table font and row height
        style.configure("Treeview", font=("Segoe UI", 14), rowheight=48)
        style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"))

    def _create_navbar(self):
        nav = ctk.CTkFrame(self, fg_color="white", height=72)
        nav.pack(side="top", fill="x")
        tk.Label(nav, text="Vehicle Rental Management", bg="white",
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=12)
        btn_frame = tk.Frame(nav, bg="white")
        btn_frame.pack(side="left", padx=8)
        self.btn_vehicles = ctk.CTkButton(btn_frame, text="Vehicles", width=160, command=lambda: self.switch("vehicles"))
        self.btn_customers = ctk.CTkButton(btn_frame, text="Customers", width=160, command=lambda: self.switch("customers"))
        self.btn_rentals = ctk.CTkButton(btn_frame, text="Rentals", width=160, command=lambda: self.switch("rentals"))
        self.btn_vehicles.grid(row=0, column=0, padx=6)
        self.btn_customers.grid(row=0, column=1, padx=6)
        self.btn_rentals.grid(row=0, column=2, padx=6)
        ctk.CTkButton(nav, text="Logout", fg_color="#d9534f", width=120, command=self._logout).pack(side="right", padx=12)

    def _create_container(self):
        self.container = ctk.CTkFrame(self, fg_color="white")
        self.container.pack(fill="both", expand=True, padx=12, pady=12)
        # frames for each section
        self.frames = {}
        for name in ("vehicles", "customers", "rentals"):
            f = ctk.CTkFrame(self.container, fg_color="white")
            f.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.frames[name] = f

        # build pages
        self._build_vehicles_page(self.frames["vehicles"])
        self._build_customers_page(self.frames["customers"])
        self._build_rentals_page(self.frames["rentals"])

    def switch(self, name):
        # bring frame to front and refresh its data
        self.frames[name].lift()
        if name == "vehicles":
            self.load_vehicles()
            self._highlight(self.btn_vehicles)
        elif name == "customers":
            self.load_customers()
            self._highlight(self.btn_customers)
        elif name == "rentals":
            self.load_rentals()
            self._highlight(self.btn_rentals)

    def _highlight(self, active_btn):
        for b in (self.btn_vehicles, self.btn_customers, self.btn_rentals):
            b.configure(fg_color="transparent")
        active_btn.configure(fg_color="#cfe8ff")

    def _logout(self):
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            self.destroy()
            LoginWindow().mainloop()

    # ---------------- Vehicles Page ----------------
    def _build_vehicles_page(self, parent):
        tk.Label(parent, text="Vehicles", bg="white", font=("Segoe UI", 18, "bold")).pack(anchor="nw", padx=8, pady=(6,0))
        top = ctk.CTkFrame(parent, fg_color="white")
        top.pack(fill="x", padx=8, pady=8)
        ctk.CTkButton(top, text="Add Vehicle", width=160, command=lambda: self._vehicle_modal()).pack(side="left", padx=6)
        tv_frame = ctk.CTkFrame(parent, fg_color="white")
        tv_frame.pack(fill="both", expand=True, padx=8, pady=8)
        cols = ("id","reg_no","make","model","year","rate","status","edit","delete")
        self.tree_vehicles = ttk.Treeview(tv_frame, columns=cols, show="headings")
        headings = [("ID",80),("Reg No",220),("Make",180),("Model",180),("Year",100),("Rate/Day",140),("Status",120),("✏️",100),("🗑️",100)]
        for col, (txt,w) in zip(cols, headings):
            self.tree_vehicles.heading(col, text=txt)
            self.tree_vehicles.column(col, width=w, anchor="center")
        self.tree_vehicles.tag_configure("odd", background="#f7fbff")
        self.tree_vehicles.tag_configure("even", background="white")
        sb = ttk.Scrollbar(tv_frame, command=self.tree_vehicles.yview)
        self.tree_vehicles.configure(yscrollcommand=sb.set)
        self.tree_vehicles.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        # bind clicks for edit/delete cells
        self.tree_vehicles.bind("<Button-1>", self._on_vehicle_click)
        self.tree_vehicles.bind("<Motion>", lambda e: self._tree_motion(e, self.tree_vehicles, edit_col=8, delete_col=9))

    def load_vehicles(self):
        rows = db_fetch("SELECT * FROM vehicles ORDER BY id DESC")
        self.tree_vehicles.delete(*self.tree_vehicles.get_children())
        for i, r in enumerate(rows):
            tag = "even" if i%2==0 else "odd"
            try:
                rate = f"{r['rate_per_day']:.2f}" if r.get('rate_per_day') is not None else ""
            except:
                rate = ""
            # use emoji stickers for edit and delete
            self.tree_vehicles.insert(
                "", "end",
                values=(
                    r['id'],
                    r['reg_no'],
                    r['make'],
                    r['model'],
                    r['year'],
                    rate,
                    r['status'],
                    "✏️",   # edit sticker
                    "🗑️"    # delete sticker
                ),
                tags=(tag,)
            )

    def _on_vehicle_click(self, event):
        if self.tree_vehicles.identify_region(event.x, event.y) != "cell": return
        col = int(self.tree_vehicles.identify_column(event.x).replace("#",""))
        item = self.tree_vehicles.identify_row(event.y)
        if not item: return
        vals = self.tree_vehicles.item(item, "values")
        vid = vals[0]
        if col == 8:   # Edit column (index 8)
            rec = db_fetch("SELECT * FROM vehicles WHERE id=%s", (vid,))
            self._vehicle_modal(data=(rec[0] if rec else None), vid=vid)
        elif col == 9: # Delete (index 9)
            if messagebox.askyesno("Delete", f"Delete vehicle {vid}? This will also delete related rentals."):
                ok, err = db_exec("DELETE FROM rentals WHERE vehicle_id=%s", (vid,))
                if not ok:
                    messagebox.showerror("Error", err)
                    return
                ok, err = db_exec("DELETE FROM vehicles WHERE id=%s", (vid,))
                if not ok:
                    messagebox.showerror("Error", err)
                else:
                    messagebox.showinfo("Deleted", "Vehicle deleted")
                    self.load_vehicles()
                    self.load_rentals()

    # ---------------- Customers Page ----------------
    def _build_customers_page(self, parent):
        tk.Label(parent, text="Customers", bg="white", font=("Segoe UI", 18, "bold")).pack(anchor="nw", padx=8, pady=(6,0))
        top = ctk.CTkFrame(parent, fg_color="white")
        top.pack(fill="x", padx=8, pady=8)
        ctk.CTkButton(top, text="Add Customer", width=160, command=lambda: self._customer_modal()).pack(side="left", padx=6)
        tv_frame = ctk.CTkFrame(parent, fg_color="white")
        tv_frame.pack(fill="both", expand=True, padx=8, pady=8)
        cols = ("id","name","phone","email","edit","delete")
        self.tree_customers = ttk.Treeview(tv_frame, columns=cols, show="headings")
        headings = [("ID",80),("Name",420),("Phone",200),("Email",360),("✏️",100),("🗑️",100)]
        for col, (txt,w) in zip(cols, headings):
            self.tree_customers.heading(col, text=txt)
            self.tree_customers.column(col, width=w, anchor="center")
        self.tree_customers.tag_configure("odd", background="#f7fbff")
        self.tree_customers.tag_configure("even", background="white")
        sb = ttk.Scrollbar(tv_frame, command=self.tree_customers.yview)
        self.tree_customers.configure(yscrollcommand=sb.set)
        self.tree_customers.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.tree_customers.bind("<Button-1>", self._on_customer_click)
        self.tree_customers.bind("<Motion>", lambda e: self._tree_motion(e, self.tree_customers, edit_col=5, delete_col=6))

    def load_customers(self):
        rows = db_fetch("SELECT * FROM customers ORDER BY id DESC")
        self.tree_customers.delete(*self.tree_customers.get_children())
        for i, r in enumerate(rows):
            tag = "even" if i%2==0 else "odd"
            # emoji stickers for edit/delete
            self.tree_customers.insert(
                "", "end",
                values=(
                    r['id'],
                    r['name'],
                    r['phone'],
                    r['email'],
                    "✏️",  # edit
                    "🗑️"   # delete
                ),
                tags=(tag,)
            )

    def _on_customer_click(self, event):
        if self.tree_customers.identify_region(event.x, event.y) != "cell": return
        col = int(self.tree_customers.identify_column(event.x).replace("#",""))
        item = self.tree_customers.identify_row(event.y)
        if not item: return
        vals = self.tree_customers.item(item, "values")
        cid = vals[0]
        if col == 5:
            rec = db_fetch("SELECT * FROM customers WHERE id=%s", (cid,))
            self._customer_modal(data=(rec[0] if rec else None), cid=cid)
        elif col == 6:
            if messagebox.askyesno("Delete", f"Delete customer {cid}? This will also delete related rentals."):
                ok, err = db_exec("DELETE FROM rentals WHERE customer_id=%s", (cid,))
                if not ok:
                    messagebox.showerror("Error", err)
                    return
                ok, err = db_exec("DELETE FROM customers WHERE id=%s", (cid,))
                if not ok:
                    messagebox.showerror("Error", err)
                else:
                    messagebox.showinfo("Deleted", "Customer deleted")
                    self.load_customers()
                    self.load_rentals()

    # ---------------- Rentals Page ----------------
    def _build_rentals_page(self, parent):
        tk.Label(parent, text="Rentals", bg="white", font=("Segoe UI", 18, "bold")).pack(anchor="nw", padx=8, pady=(6,0))
        top = ctk.CTkFrame(parent, fg_color="white")
        top.pack(fill="x", padx=8, pady=8)
        ctk.CTkButton(top, text="Add Rental", width=160, command=lambda: self._rental_modal()).pack(side="left", padx=6)
        tv_frame = ctk.CTkFrame(parent, fg_color="white")
        tv_frame.pack(fill="both", expand=True, padx=8, pady=8)
        cols = ("id","vehicle","customer","start","expected","actual","status","amount","edit","delete")
        self.tree_rentals = ttk.Treeview(tv_frame, columns=cols, show="headings")
        headings = [("ID",80),("Vehicle",140),("Customer",160),("Start",140),("Expected",140),("Actual",140),("Status",120),("Amount",140),("✏️",100),("🗑️",100)]
        for col, (txt,w) in zip(cols, headings):
            self.tree_rentals.heading(col, text=txt)
            self.tree_rentals.column(col, width=w, anchor="center")
        self.tree_rentals.tag_configure("odd", background="#f7fbff")
        self.tree_rentals.tag_configure("even", background="white")
        sb = ttk.Scrollbar(tv_frame, command=self.tree_rentals.yview)
        self.tree_rentals.configure(yscrollcommand=sb.set)
        self.tree_rentals.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.tree_rentals.bind("<Button-1>", self._on_rental_click)
        self.tree_rentals.bind("<Motion>", lambda e: self._tree_motion(e, self.tree_rentals, edit_col=9, delete_col=10))

    def load_rentals(self):
        rows = db_fetch("SELECT * FROM rentals ORDER BY id DESC")
        self.tree_rentals.delete(*self.tree_rentals.get_children())
        for i, r in enumerate(rows):
            tag = "even" if i%2==0 else "odd"
            amt = ""
            try:
                # prefer stored amount if available
                if r.get('amount') is not None:
                    amt = f"{float(r.get('amount')):.2f}"
                else:
                    rate = get_rate(r['vehicle_id'])
                    if rate and r.get('start_date'):
                        sd = datetime.strptime(r['start_date'], "%Y-%m-%d")
                        ed = datetime.strptime(r['expected_return_date'], "%Y-%m-%d") if r.get('expected_return_date') else sd
                        days = max(1, (ed - sd).days + 1)
                        amt = f"{(rate or 0) * days:.2f}"
            except:
                amt = ""
            # insert with emoji stickers for actions
            self.tree_rentals.insert(
                "", "end",
                values=(
                    r['id'],
                    r['vehicle_id'],
                    r['customer_id'],
                    r.get('start_date') or "",
                    r.get('expected_return_date') or "",
                    r.get('actual_return_date') or "",
                    r.get('status') or "",
                    amt,
                    "✏️",  # edit
                    "🗑️"   # delete
                ),
                tags=(tag,)
            )

    def _on_rental_click(self, event):
        if self.tree_rentals.identify_region(event.x, event.y) != "cell": return
        col = int(self.tree_rentals.identify_column(event.x).replace("#",""))
        item = self.tree_rentals.identify_row(event.y)
        if not item: return
        vals = self.tree_rentals.item(item, "values")
        rid = vals[0]
        if col == 9:
            rec = db_fetch("SELECT * FROM rentals WHERE id=%s", (rid,))
            self._rental_modal(data=(rec[0] if rec else None), rid=rid)
        elif col == 10:
            if messagebox.askyesno("Delete", f"Delete rental {rid}? This will free the vehicle if not returned."):
                # free vehicle if needed
                r = db_fetch("SELECT vehicle_id, status FROM rentals WHERE id=%s", (rid,))
                if r and r[0].get('status') != 'returned':
                    db_exec("UPDATE vehicles SET status='available' WHERE id=%s", (r[0]['vehicle_id'],))
                ok, err = db_exec("DELETE FROM rentals WHERE id=%s", (rid,))
                if not ok:
                    messagebox.showerror("Error", err)
                    return
                messagebox.showinfo("Deleted", "Rental deleted")
                self.load_rentals()
                self.load_vehicles()

    def _tree_motion(self, event, tree, edit_col, delete_col):
        try:
            col = int(tree.identify_column(event.x).replace("#",""))
            if col in (edit_col, delete_col):
                tree.configure(cursor="hand2")
            else:
                tree.configure(cursor="")
        except:
            tree.configure(cursor="")

    # ---------------- Vehicle modal ----------------
    def _vehicle_modal(self, data=None, vid=None):
        modal = tk.Toplevel(self); modal.transient(self); modal.grab_set(); modal.title("Vehicle")
        modal.geometry("560x460"); modal.minsize(520,420); modal.configure(bg="white")
        frm = tk.Frame(modal, bg="white"); frm.pack(padx=12, pady=12, fill="both")
        entries = {}
        labels = [("Reg No","reg_no"),("Make","make"),("Model","model"),("Year","year"),("Rate/Day","rate_per_day")]
        for i,(lbl,key) in enumerate(labels):
            tk.Label(frm, text=lbl, bg="white", font=("Segoe UI",12)).grid(row=i, column=0, sticky="w", pady=8)
            e = ctk.CTkEntry(frm, width=420); e.grid(row=i, column=1, pady=8, sticky="w"); entries[key]=e
        tk.Label(frm, text="Status", bg="white", font=("Segoe UI",12)).grid(row=5,column=0, sticky="w", pady=8)
        status_var = tk.StringVar(value=(data['status'] if data else "available"))
        status_cb = ttk.Combobox(frm, textvariable=status_var, values=["available","rented"], state="readonly", width=20); status_cb.grid(row=5,column=1, pady=8, sticky="w")
        if data:
            for k in entries: entries[k].insert(0, str(data.get(k,"")))
        def save_vehicle():
            try:
                payload = {
                    'reg_no': entries['reg_no'].get().strip(),
                    'make': entries['make'].get().strip(),
                    'model': entries['model'].get().strip(),
                    'year': int(entries['year'].get().strip()),
                    'rate_per_day': float(entries['rate_per_day'].get().strip()),
                    'status': status_var.get()
                }
            except Exception:
                return messagebox.showerror("Input Error", "Please check Year and Rate fields.")
            ok, err = (db_exec("UPDATE vehicles SET reg_no=%s,make=%s,model=%s,year=%s,rate_per_day=%s,status=%s WHERE id=%s", (payload['reg_no'],payload['make'],payload['model'],payload['year'],payload['rate_per_day'],payload['status'],vid)) if vid else db_exec("INSERT INTO vehicles (reg_no,make,model,year,rate_per_day,status) VALUES (%s,%s,%s,%s,%s,%s)", (payload['reg_no'],payload['make'],payload['model'],payload['year'],payload['rate_per_day'],payload['status'])))
            if not ok: messagebox.showerror("DB Error", err); return
            modal.destroy(); self.load_vehicles()
        btnf = tk.Frame(modal, bg="white"); btnf.pack(pady=10)
        ctk.CTkButton(btnf, text="Save", width=140, command=save_vehicle).grid(row=0,column=0,padx=8)
        ctk.CTkButton(btnf, text="Cancel", width=120, command=modal.destroy).grid(row=0,column=1,padx=8)

    # ---------------- Customer modal ----------------
    def _customer_modal(self, data=None, cid=None):
        modal = tk.Toplevel(self); modal.transient(self); modal.grab_set(); modal.title("Customer")
        modal.geometry("520x300"); modal.minsize(480,260); modal.configure(bg="white")
        frm = tk.Frame(modal, bg="white"); frm.pack(padx=12, pady=12, fill="both")
        name = ctk.CTkEntry(frm, width=420); phone = ctk.CTkEntry(frm, width=420); email = ctk.CTkEntry(frm, width=420)
        tk.Label(frm, text="Name", bg="white", font=("Segoe UI",12)).grid(row=0,column=0, sticky="w"); name.grid(row=0,column=1,pady=8)
        tk.Label(frm, text="Phone", bg="white", font=("Segoe UI",12)).grid(row=1,column=0, sticky="w"); phone.grid(row=1,column=1,pady=8)
        tk.Label(frm, text="Email", bg="white", font=("Segoe UI",12)).grid(row=2,column=0, sticky="w"); email.grid(row=2,column=1,pady=8)
        if data:
            name.insert(0,data['name']); phone.insert(0,data['phone']); email.insert(0,data['email'])
        def save_customer():
            if not (name.get().strip() and phone.get().strip() and email.get().strip()):
                return messagebox.showerror("Input Error", "All fields required")
            payload = {'name':name.get().strip(),'phone':phone.get().strip(),'email':email.get().strip()}
            ok, err = (db_exec("UPDATE customers SET name=%s,phone=%s,email=%s WHERE id=%s", (payload['name'],payload['phone'],payload['email'],cid)) if cid else db_exec("INSERT INTO customers (name,phone,email) VALUES (%s,%s,%s)", (payload['name'],payload['phone'],payload['email'])))
            if not ok: messagebox.showerror("DB Error", err); return
            modal.destroy(); self.load_customers()
        btnf = tk.Frame(modal, bg="white"); btnf.pack(pady=8)
        ctk.CTkButton(btnf, text="Save", width=140, command=save_customer).grid(row=0,column=0,padx=8)
        ctk.CTkButton(btnf, text="Cancel", width=120, command=modal.destroy).grid(row=0,column=1,padx=8)

    # ---------------- Rental modal (auto-calc amount and save to DB) ----------------
    def _rental_modal(self, data=None, rid=None):
        modal = tk.Toplevel(self); modal.transient(self); modal.grab_set(); modal.title("Rental")
        modal.geometry("760x520"); modal.minsize(700,480); modal.configure(bg="white"); modal.lift(); modal.focus_force()
        content = tk.Frame(modal, bg="white"); content.pack(fill="both", expand=True, padx=20, pady=(20,10))

        vehicle = ctk.CTkEntry(content, width=260)
        customer = ctk.CTkEntry(content, width=260)
        start = ctk.CTkEntry(content, width=260)
        expected = ctk.CTkEntry(content, width=260)
        actual = ctk.CTkEntry(content, width=260)

        tk.Label(content, text="Vehicle ID", bg="white", font=("Segoe UI",12)).grid(row=0, column=0, sticky="w", pady=8)
        vehicle.grid(row=0, column=1, pady=8, sticky="w")
        tk.Label(content, text="Customer ID", bg="white", font=("Segoe UI",12)).grid(row=1, column=0, sticky="w", pady=8)
        customer.grid(row=1, column=1, pady=8, sticky="w")
        tk.Label(content, text="Start (YYYY-MM-DD)", bg="white", font=("Segoe UI",12)).grid(row=2, column=0, sticky="w", pady=8)
        start.grid(row=2, column=1, pady=8, sticky="w")
        tk.Label(content, text="Expected (YYYY-MM-DD)", bg="white", font=("Segoe UI",12)).grid(row=3, column=0, sticky="w", pady=8)
        expected.grid(row=3, column=1, pady=8, sticky="w")
        tk.Label(content, text="Actual (YYYY-MM-DD)", bg="white", font=("Segoe UI",12)).grid(row=4, column=0, sticky="w", pady=8)
        actual.grid(row=4, column=1, pady=8, sticky="w")

        tk.Label(content, text="Status", bg="white", font=("Segoe UI",12)).grid(row=5, column=0, sticky="w", pady=8)
        status_var = tk.StringVar(value=(data['status'] if data else 'ongoing'))
        status_cb = ttk.Combobox(content, textvariable=status_var, values=["ongoing","returned"], state="readonly", width=22)
        status_cb.grid(row=5, column=1, pady=8, sticky="w")

        # read-only amount entry (visible like vehicle)
        amt_var = tk.StringVar()
        tk.Label(content, text="Amount (auto-calculated)", bg="white", font=("Segoe UI",12,"bold")).grid(row=6, column=0, sticky="w", pady=10)
        amt_entry = ctk.CTkEntry(content, textvariable=amt_var, width=340, state="readonly")
        amt_entry.grid(row=6, column=1, sticky="w", pady=10)

        computed_amount = {'value': None}

        if data:
            vehicle.insert(0, data.get('vehicle_id',''))
            customer.insert(0, data.get('customer_id',''))
            start.insert(0, data.get('start_date','') or "")
            expected.insert(0, data.get('expected_return_date','') or "")
            actual.insert(0, data.get('actual_return_date','') or "")
            if data.get('amount') is not None:
                try:
                    computed_amount['value'] = float(data.get('amount'))
                    amt_var.set(f"{computed_amount['value']:.2f}")
                except:
                    pass

        def parse_date_flexible(s):
            if not s or not s.strip():
                return None
            s = s.strip()
            fmts = ["%Y-%m-%d", "%d-%m-%Y", "%d-%m-%y", "%Y/%m/%d", "%d/%m/%Y"]
            for f in fmts:
                try:
                    dt = datetime.strptime(s, f)
                    return dt.strftime("%Y-%m-%d")
                except:
                    continue
            raise ValueError(f"Unrecognized date format: {s!r}. Use YYYY-MM-DD or DD-MM-YYYY.")

        def compute_amount():
            amt_var.set("")
            computed_amount['value'] = None
            try:
                vid_text = vehicle.get().strip()
                sd_text = start.get().strip()
                ed_text = expected.get().strip() or sd_text

                if not vid_text or not sd_text:
                    return
                try:
                    vid = int(vid_text)
                except:
                    return
                rate = get_rate(vid)
                if rate is None:
                    return
                try:
                    sd_iso = parse_date_flexible(sd_text)
                    ed_iso = parse_date_flexible(ed_text) or sd_iso
                except:
                    return
                d1 = datetime.strptime(sd_iso, "%Y-%m-%d")
                d2 = datetime.strptime(ed_iso, "%Y-%m-%d")
                days = max(1, (d2 - d1).days + 1)
                total = (rate or 0) * days
                computed_amount['value'] = float(total)
                amt_var.set(f"{total:.2f}   ( {days} days @ {rate:.2f} )")
            except:
                amt_var.set("")
                computed_amount['value'] = None

        # polling for reliable updates
        def poll():
            compute_amount()
            try:
                modal._after_id = modal.after(300, poll)
            except:
                pass

        modal._after_id = None
        poll()

        def _on_close():
            try:
                if getattr(modal, "_after_id", None):
                    modal.after_cancel(modal._after_id)
            except:
                pass
            try: modal.destroy()
            except: pass

        modal.protocol("WM_DELETE_WINDOW", _on_close)

        btn_frame = tk.Frame(modal, bg="white"); btn_frame.pack(fill="x", side="bottom", pady=(6,12))

        def on_save_rental():
            # validate IDs
            vid_text = vehicle.get().strip(); cid_text = customer.get().strip()
            if not vid_text or not cid_text:
                return messagebox.showerror("Input Error", "Vehicle ID and Customer ID are required.")
            try:
                vid = int(vid_text)
            except:
                return messagebox.showerror("Input Error", "Vehicle ID must be an integer.")
            try:
                cid = int(cid_text)
            except:
                return messagebox.showerror("Input Error", "Customer ID must be an integer.")
            # parse dates
            try:
                sd_iso = parse_date_flexible(start.get().strip())
                if not sd_iso:
                    return messagebox.showerror("Input Error", "Start date required.")
            except ValueError as ve:
                return messagebox.showerror("Start Date", str(ve))
            try:
                ed_iso = parse_date_flexible(expected.get().strip()) or sd_iso
            except ValueError as ve:
                return messagebox.showerror("Expected Date", str(ve))
            try:
                act_iso = parse_date_flexible(actual.get().strip())
            except ValueError as ve:
                return messagebox.showerror("Actual Date", str(ve))

            # logical check
            try:
                sd_dt = datetime.strptime(sd_iso, "%Y-%m-%d")
                ed_dt = datetime.strptime(ed_iso, "%Y-%m-%d")
                if ed_dt < sd_dt:
                    return messagebox.showerror("Input Error", "Expected return date cannot be before start date.")
            except:
                return messagebox.showerror("Input Error", "Invalid dates.")

            # compute and include amount
            compute_amount()
            amt_val = computed_amount['value']

            payload = (vid, cid, sd_iso, ed_iso, act_iso, status_var.get(), amt_val)

            if rid:
                ok, err = db_exec("UPDATE rentals SET vehicle_id=%s,customer_id=%s,start_date=%s,expected_return_date=%s,actual_return_date=%s,status=%s,amount=%s WHERE id=%s", (vid, cid, sd_iso, ed_iso, act_iso, status_var.get(), amt_val, rid))
            else:
                # check vehicle availability if starting ongoing
                if status_var.get() == 'ongoing':
                    v = db_fetch("SELECT status FROM vehicles WHERE id=%s", (vid,))
                    if not v:
                        return messagebox.showerror("Error", "Vehicle not found.")
                    if v[0].get('status') != 'available':
                        return messagebox.showerror("Error", "Vehicle is not available.")
                ok, err = db_exec("INSERT INTO rentals (vehicle_id,customer_id,start_date,expected_return_date,actual_return_date,status,amount) VALUES (%s,%s,%s,%s,%s,%s,%s)", payload)
                if ok and status_var.get() == 'ongoing':
                    db_exec("UPDATE vehicles SET status='rented' WHERE id=%s", (vid,))

            if not ok:
                # helpful hint if 'amount' missing in DB
                if err and ("unknown column" in err.lower() and "amount" in err.lower()):
                    messagebox.showerror("DB Error", "Missing 'amount' column. Run:\nALTER TABLE rentals ADD COLUMN amount DECIMAL(12,2) NULL AFTER status;")
                else:
                    messagebox.showerror("DB Error", err)
                return

            # cancel poll then close
            try:
                if getattr(modal, "_after_id", None):
                    modal.after_cancel(modal._after_id)
            except:
                pass
            modal.destroy()
            self.load_rentals()
            self.load_vehicles()

        ctk.CTkButton(btn_frame, text="Save", width=170, fg_color="#28a745", command=on_save_rental).pack(side="right", padx=(6,14))
        ctk.CTkButton(btn_frame, text="Cancel", width=140, fg_color="#6c757d", command=_on_close).pack(side="right", padx=6)

# -------- Login Window (plain-text password) --------
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Admin Login")
        self.state("zoomed")
        self.configure(fg_color="white")
        self._build_ui()

    def _build_ui(self):
        page = ctk.CTkFrame(self, fg_color="white")
        page.pack(fill="both", expand=True)
        tk.Label(page, text="Vehicle Rental Admin", bg="white", font=("Segoe UI",28,"bold")).pack(pady=(40,12))
        card = ctk.CTkFrame(page, width=640, height=360)
        card.pack(pady=8); card.pack_propagate(False)
        tk.Label(card, text="Username", bg="white", font=("Segoe UI",12)).pack(anchor="w", padx=24, pady=(18,6))
        self.entry_user = ctk.CTkEntry(card, width=520); self.entry_user.pack(padx=24)
        tk.Label(card, text="Password", bg="white", font=("Segoe UI",12)).pack(anchor="w", padx=24, pady=(12,6))
        self.entry_pass = ctk.CTkEntry(card, width=520); self.entry_pass.pack(padx=24)
        f = ctk.CTkFrame(card, fg_color="white"); f.pack(pady=14)
        ctk.CTkButton(f, text="Login", width=160, command=self._login).grid(row=0,column=0,padx=8)
        ctk.CTkButton(f, text="Exit", width=140, command=self.destroy).grid(row=0,column=1,padx=8)
        self.bind("<Return>", lambda e: self._login())

    def _login(self):
        user = self.entry_user.get().strip(); pwd = self.entry_pass.get().strip()
        if not user or not pwd:
            return messagebox.showwarning("Input Error", "Enter username and password")
        ok, msg = verify_admin(user, pwd)
        if ok:
            messagebox.showinfo("Welcome", "Login successful")
            self.destroy()
            app = App(); app.mainloop()
        else:
            messagebox.showerror("Login Failed", msg)

if __name__ == "__main__":
    LoginWindow().mainloop()
