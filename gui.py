import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from db_config import DatabaseManager

class ContactManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Initialize database connection
        try:
            self.db = DatabaseManager()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            root.destroy()
            return
            
        # Contact ID for editing (None for new contact)
        self.current_contact_id = None
            
        # Create UI components
        self._create_menu()
        self._create_contact_form()
        self._create_contact_list()
        self._create_search_bar()
        
        # Load contacts
        self.load_contacts()
        
    def _create_menu(self):
        """Create the application menu"""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Contact", command=self.new_contact)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
        
    def _create_search_bar(self):
        """Create search bar"""
        search_frame = ttk.Frame(self.root, padding="10 5 10 0")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(search_frame, text="Search", command=self.search_contacts).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=(5, 0))
        
    def _create_contact_list(self):
        """Create the contact list view"""
        # Contact list frame
        list_frame = ttk.LabelFrame(self.root, text="Contacts")
        list_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("id", "name", "email", "phone")
        self.contact_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Set column headings
        self.contact_tree.heading("id", text="ID")
        self.contact_tree.heading("name", text="Name")
        self.contact_tree.heading("email", text="Email")
        self.contact_tree.heading("phone", text="Phone")
        
        # Set column widths
        self.contact_tree.column("id", width=50)
        self.contact_tree.column("name", width=200)
        self.contact_tree.column("email", width=200)
        self.contact_tree.column("phone", width=150)
        
        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.contact_tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.contact_tree.xview)
        self.contact_tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        
        # Pack everything
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.contact_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.contact_tree.bind("<<TreeviewSelect>>", self.on_contact_select)
        
        # Button frame
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(pady=5, fill=tk.X)
        
        ttk.Button(button_frame, text="New", command=self.new_contact).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Edit", command=self.edit_selected_contact).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete", command=self.delete_selected_contact).pack(side=tk.LEFT, padx=2)
        
    def _create_contact_form(self):
        """Create the contact entry form"""
        form_frame = ttk.LabelFrame(self.root, text="Contact Details")
        form_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Create a grid for form fields
        form_grid = ttk.Frame(form_frame)
        form_grid.pack(padx=10, pady=5, fill=tk.X)
        
        # Name field
        ttk.Label(form_grid, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(form_grid, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Email field
        ttk.Label(form_grid, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.email_var = tk.StringVar()
        ttk.Entry(form_grid, textvariable=self.email_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Phone field
        ttk.Label(form_grid, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.phone_var = tk.StringVar()
        ttk.Entry(form_grid, textvariable=self.phone_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Address field
        ttk.Label(form_grid, text="Address:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.address_var = tk.StringVar()
        ttk.Entry(form_grid, textvariable=self.address_var, width=40).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Notes field
        ttk.Label(form_grid, text="Notes:").grid(row=4, column=0, sticky=tk.NW, pady=2)
        self.notes_text = scrolledtext.ScrolledText(form_grid, width=38, height=4)
        self.notes_text.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=5, fill=tk.X)
        
        ttk.Button(button_frame, text="Save", command=self.save_contact).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=2)
        
    def load_contacts(self):
        """Load all contacts into the treeview"""
        # Clear the treeview
        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)
            
        # Get all contacts from database
        contacts = self.db.get_all_contacts()
        
        # Insert contacts into treeview
        for contact in contacts:
            self.contact_tree.insert("", tk.END, values=(
                contact["id"], 
                contact["name"], 
                contact["email"] or "", 
                contact["phone"] or ""
            ))
            
    def search_contacts(self):
        """Search contacts based on search term"""
        search_term = self.search_var.get().strip()
        
        # If search is empty, load all contacts
        if not search_term:
            self.load_contacts()
            return
            
        # Clear the treeview
        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)
            
        # Search contacts in database
        contacts = self.db.search_contacts(search_term)
        
        # Insert matching contacts into treeview
        for contact in contacts:
            self.contact_tree.insert("", tk.END, values=(
                contact["id"], 
                contact["name"], 
                contact["email"] or "", 
                contact["phone"] or ""
            ))
            
    def clear_search(self):
        """Clear search and reload all contacts"""
        self.search_var.set("")
        self.load_contacts()
            
    def on_contact_select(self, event):
        """Handle contact selection in treeview"""
        selected_items = self.contact_tree.selection()
        if not selected_items:
            return
            
        # Get the selected item's ID
        selected_item = selected_items[0]
        contact_id = self.contact_tree.item(selected_item)["values"][0]
        
        # Get contact details from database
        contact = self.db.get_contact_by_id(contact_id)
        if not contact:
            return
            
        # Fill the form with selected contact data
        self.current_contact_id = contact["id"]
        self.name_var.set(contact["name"])
        self.email_var.set(contact["email"] or "")
        self.phone_var.set(contact["phone"] or "")
        self.address_var.set(contact["address"] or "")
        
        # Clear and fill notes
        self.notes_text.delete(1.0, tk.END)
        if contact["notes"]:
            self.notes_text.insert(tk.END, contact["notes"])
            
    def save_contact(self):
        """Save the current contact (create new or update existing)"""
        # Get values from form
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        address = self.address_var.get().strip()
        notes = self.notes_text.get(1.0, tk.END).strip()
        
        # Validate name (required field)
        if not name:
            messagebox.showerror("Validation Error", "Name is required")
            return
            
        try:
            if self.current_contact_id:  # Update existing contact
                success = self.db.update_contact(
                    self.current_contact_id, name, email, phone, address, notes
                )
                if success:
                    messagebox.showinfo("Success", "Contact updated successfully")
                else:
                    messagebox.showerror("Error", "Failed to update contact")
            else:  # Create new contact
                contact_id = self.db.create_contact(name, email, phone, address, notes)
                if contact_id:
                    messagebox.showinfo("Success", "Contact created successfully")
                    self.current_contact_id = contact_id
                else:
                    messagebox.showerror("Error", "Failed to create contact")
                    
            # Refresh contact list
            self.load_contacts()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def new_contact(self):
        """Clear the form for a new contact"""
        self.current_contact_id = None
        self.clear_form()
        
    def clear_form(self):
        """Clear all form fields"""
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.address_var.set("")
        self.notes_text.delete(1.0, tk.END)
        
    def edit_selected_contact(self):
        """Edit the selected contact"""
        selected_items = self.contact_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Please select a contact to edit")
            return
            
        # Selection event will trigger on_contact_select
        # which will populate the form
            
    def delete_selected_contact(self):
        """Delete the selected contact"""
        selected_items = self.contact_tree.selection()
        if not selected_items:
            messagebox.showinfo("Information", "Please select a contact to delete")
            return
            
        # Get the selected contact ID
        selected_item = selected_items[0]
        contact_id = self.contact_tree.item(selected_item)["values"][0]
        contact_name = self.contact_tree.item(selected_item)["values"][1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete contact '{contact_name}'?"
        )
        if not confirm:
            return
            
        # Delete the contact
        try:
            success = self.db.delete_contact(contact_id)
            if success:
                messagebox.showinfo("Success", "Contact deleted successfully")
                # Clear form if deleted contact was being edited
                if self.current_contact_id == contact_id:
                    self.clear_form()
                    self.current_contact_id = None
                # Refresh contact list
                self.load_contacts()
            else:
                messagebox.showerror("Error", "Failed to delete contact")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About Contact Manager",
            "Contact Manager v1.0\n\n"
            "A simple contact management application that stores data in MySQL database.\n\n"
            "Created with Python and Tkinter."
        )
        
    def __del__(self):
        """Clean up database connection on exit"""
        if hasattr(self, 'db'):
            self.db.close()