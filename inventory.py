import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from io import BytesIO
import base64

# Initialize session state
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame({
        'Product ID': ['P001', 'P002', 'P003'],
        'Product Name': ['Laptop', 'Mouse', 'Keyboard'],
        'Category': ['Electronics', 'Accessories', 'Accessories'],
        'Quantity': [50, 200, 150],
        'Price': [80000, 500, 1200],
        'Supplier': ['TechCorp', 'PeriTech', 'KeyMaster'],
        'Location': ['Warehouse A', 'Warehouse B', 'Warehouse A'],
        'Reorder Level': [10, 50, 30],
        'Expiry Date': [None, None, None],
        'Status': ['Active', 'Active', 'Active']
    })

if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame({
        'Transaction ID': ['T001', 'T002'],
        'Product ID': ['P001', 'P002'],
        'Product Name': ['Laptop', 'Mouse'],
        'Quantity': [5, 10],
        'Transaction Type': ['Sale', 'Purchase'],
        'Date': [datetime.now() - timedelta(days=1), datetime.now()]
    })

# Utility functions
def add_product(product_data):
    if product_data['Product ID'] in st.session_state.inventory['Product ID'].values:
        return False, "Product ID already exists"
    
    new_row = pd.DataFrame([product_data])
    st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
    log_transaction(product_data['Product ID'], product_data['Product Name'], 
                   product_data['Quantity'], 'Purchase')
    return True, "Product added successfully"

def update_product(product_id, updates):
    idx = st.session_state.inventory[st.session_state.inventory['Product ID'] == product_id].index[0]
    for key, value in updates.items():
        st.session_state.inventory.at[idx, key] = value
    return "Product updated successfully"

def delete_product(product_id):
    st.session_state.inventory = st.session_state.inventory[
        st.session_state.inventory['Product ID'] != product_id
    ].reset_index(drop=True)
    return "Product deleted successfully"

def log_transaction(product_id, product_name, quantity, trans_type):
    new_trans = pd.DataFrame([{
        'Transaction ID': f"T{len(st.session_state.transactions) + 1:03d}",
        'Product ID': product_id,
        'Product Name': product_name,
        'Quantity': quantity,
        'Transaction Type': trans_type,
        'Date': datetime.now()
    }])
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_trans], ignore_index=True)

def export_to_csv(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download {filename}</a>'
    return href

# Dashboard
def show_dashboard():
    st.title("📊 Inventory Management System")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Products", len(st.session_state.inventory))
    with col2:
        total_qty = st.session_state.inventory['Quantity'].sum()
        st.metric("Total Quantity", total_qty)
    with col3:
        low_stock = len(st.session_state.inventory[
            st.session_state.inventory['Quantity'] <= st.session_state.inventory['Reorder Level']
        ])
        st.metric("Low Stock Items", low_stock)
    with col4:
        total_value = (st.session_state.inventory['Quantity'] * st.session_state.inventory['Price']).sum()
        st.metric("Total Value", f"₹{total_value:,.2f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.pie(st.session_state.inventory, values='Quantity', names='Category',
                     title='Inventory by Category')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(st.session_state.inventory.nlargest(10, 'Quantity'),
                     x='Product Name', y='Quantity', title='Top 10 Products by Quantity')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Low stock alert
    low_stock_items = st.session_state.inventory[
        st.session_state.inventory['Quantity'] <= st.session_state.inventory['Reorder Level']
    ]
    if not low_stock_items.empty:
        st.warning("⚠️ Low Stock Alert")
        st.dataframe(low_stock_items[['Product Name', 'Quantity', 'Reorder Level']])

# Product Management
def manage_products():
    st.title("📦 Product Management")
    
    tab1, tab2, tab3 = st.tabs(["Add Product", "Edit Product", "Delete Product"])
    
    with tab1:
        st.subheader("Add New Product")
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                product_id = st.text_input("Product ID")
                product_name = st.text_input("Product Name")
                category = st.selectbox("Category", ["Electronics", "Accessories", "Furniture", "Stationery", "Other"])
                quantity = st.number_input("Quantity", min_value=0, value=0)
            with col2:
                price = st.number_input("Price", min_value=0.0, value=0.0)
                supplier = st.text_input("Supplier")
                location = st.selectbox("Location", ["Warehouse A", "Warehouse B", "Store Front"])
                reorder_level = st.number_input("Reorder Level", min_value=0, value=10)
            
            submitted = st.form_submit_button("Add Product")
            if submitted:
                product_data = {
                    'Product ID': product_id,
                    'Product Name': product_name,
                    'Category': category,
                    'Quantity': quantity,
                    'Price': price,
                    'Supplier': supplier,
                    'Location': location,
                    'Reorder Level': reorder_level,
                    'Expiry Date': None,
                    'Status': 'Active'
                }
                success, message = add_product(product_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    with tab2:
        st.subheader("Edit Product")
        product_id = st.selectbox("Select Product to Edit", st.session_state.inventory['Product ID'].tolist())
        if product_id:
            product = st.session_state.inventory[st.session_state.inventory['Product ID'] == product_id].iloc[0]
            with st.form("edit_product_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Product Name", value=product['Product Name'])
                    new_category = st.selectbox("Category", 
                                              ["Electronics", "Accessories", "Furniture", "Stationery", "Other"],
                                              index=["Electronics", "Accessories", "Furniture", "Stationery", "Other"].index(product['Category']))
                    new_quantity = st.number_input("Quantity", min_value=0, value=int(product['Quantity']))
                with col2:
                    new_price = st.number_input("Price", min_value=0.0, value=float(product['Price']))
                    new_supplier = st.text_input("Supplier", value=product['Supplier'])
                    new_location = st.selectbox("Location", 
                                               ["Warehouse A", "Warehouse B", "Store Front"],
                                               index=["Warehouse A", "Warehouse B", "Store Front"].index(product['Location']))
                    new_reorder = st.number_input("Reorder Level", min_value=0, value=int(product['Reorder Level']))
                
                update_btn = st.form_submit_button("Update Product")
                if update_btn:
                    updates = {
                        'Product Name': new_name,
                        'Category': new_category,
                        'Quantity': new_quantity,
                        'Price': new_price,
                        'Supplier': new_supplier,
                        'Location': new_location,
                        'Reorder Level': new_reorder
                    }
                    message = update_product(product_id, updates)
                    st.success(message)
    
    with tab3:
        st.subheader("Delete Product")
        del_product_id = st.selectbox("Select Product to Delete", st.session_state.inventory['Product ID'].tolist(), key="del_product")
        if st.button("Delete Product"):
            message = delete_product(del_product_id)
            st.success(message)

# Inventory View
def view_inventory():
    st.title("📋 Inventory View")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.multiselect("Category", st.session_state.inventory['Category'].unique())
    with col2:
        location_filter = st.multiselect("Location", st.session_state.inventory['Location'].unique())
    with col3:
        status_filter = st.multiselect("Status", st.session_state.inventory['Status'].unique(), default=['Active'])
    
    # Apply filters
    filtered_df = st.session_state.inventory.copy()
    if category_filter:
        filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
    if location_filter:
        filtered_df = filtered_df[filtered_df['Location'].isin(location_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
    
    # Search
    search_term = st.text_input("Search products")
    if search_term:
        filtered_df = filtered_df[filtered_df['Product Name'].str.contains(search_term, case=False)]
    
    # Display and edit inventory
    st.data_editor(
        filtered_df,
        key="inventory_editor",
        num_rows="dynamic",
        use_container_width=True
    )
    
    # Export options
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(export_to_csv(filtered_df, "inventory_export"), unsafe_allow_html=True)
    with col2:
        st.markdown(export_to_csv(st.session_state.transactions, "transactions_export"), unsafe_allow_html=True)

# Reports
def show_reports():
    st.title("📈 Reports & Analytics")
    
    report_type = st.selectbox("Select Report Type", [
        "Inventory Summary", "Transaction History", "Low Stock Report", 
        "Category Analysis", "Supplier Analysis"
    ])
    
    if report_type == "Inventory Summary":
        st.subheader("Inventory Summary")
        summary = st.session_state.inventory.groupby('Category').agg({
            'Quantity': 'sum',
            'Price': 'mean'
        }).round(2)
        st.dataframe(summary)
        
        fig = px.bar(summary, y='Quantity', title='Quantity by Category')
        st.plotly_chart(fig)
    
    elif report_type == "Transaction History":
        st.subheader("Transaction History")
        st.dataframe(st.session_state.transactions.sort_values('Date', ascending=False))
        
        fig = px.line(st.session_state.transactions.groupby('Date').size().reset_index(name='Count'),
                     x='Date', y='Count', title='Transactions Over Time')
        st.plotly_chart(fig)
    
    elif report_type == "Low Stock Report":
        st.subheader("Low Stock Items")
        low_stock = st.session_state.inventory[
            st.session_state.inventory['Quantity'] <= st.session_state.inventory['Reorder Level']
        ]
        st.dataframe(low_stock)
        
        if not low_stock.empty:
            fig = px.bar(low_stock, x='Product Name', y='Quantity',
                        color='Reorder Level', title='Low Stock Items')
            st.plotly_chart(fig)
    
    elif report_type == "Category Analysis":
        st.subheader("Category Analysis")
        category_analysis = st.session_state.inventory.groupby('Category').agg({
            'Quantity': 'sum',
            'Price': 'mean',
            'Product ID': 'count'
        }).rename(columns={'Product ID': 'Product Count'})
        st.dataframe(category_analysis)
        
        fig = px.pie(category_analysis, values='Quantity', names=category_analysis.index,
                    title='Inventory Distribution by Category')
        st.plotly_chart(fig)
    
    elif report_type == "Supplier Analysis":
        st.subheader("Supplier Analysis")
        supplier_analysis = st.session_state.inventory.groupby('Supplier').agg({
            'Quantity': 'sum',
            'Price': 'mean',
            'Product ID': 'count'
        }).rename(columns={'Product ID': 'Product Count'})
        st.dataframe(supplier_analysis)

# Main app
def main():
    # Sidebar for navigation
    with st.sidebar:
        st.title("📦 IMS")
        st.divider()
        
    # Main navigation
    pages = {
        "Dashboard": show_dashboard,
        "Product Management": manage_products,
        "Inventory View": view_inventory,
        "Reports": show_reports
    }
    
    choice = st.sidebar.radio("Navigation", list(pages.keys()))
    
    # Display the selected page
    pages[choice]()

if __name__ == "__main__":
    main()
