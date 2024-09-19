import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Data Gathering
customers_df = pd.read_csv("../data/customers_dataset.csv")
geolocation_df = pd.read_csv("../data/geolocation_dataset.csv")
orders_df = pd.read_csv("../data/orders_dataset.csv")
order_items_df = pd.read_csv("../data/order_items_dataset.csv")
order_payments_df = pd.read_csv("../data/order_payments_dataset.csv")
order_reviews_df = pd.read_csv("../data/order_reviews_dataset.csv")
products_df = pd.read_csv("../data/products_dataset.csv")
product_category_name_translations_df = pd.read_csv("../data/product_category_name_translation.csv")
sellers_df = pd.read_csv("../data/sellers_dataset.csv")
datetime_columns = ['review_creation_date', 'review_answer_timestamp']
for column in datetime_columns:
    order_reviews_df[column] = pd.to_datetime(order_reviews_df[column])
products_df = products_df[['product_id', 'product_category_name']]
products_df["product_category_name"].fillna("other", inplace=True)

# Data Cleaning
geolocation_df.drop_duplicates(inplace=True)
orders_df.dropna(subset=["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date"], inplace=True)
datetime_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
for column in datetime_columns:
    orders_df[column] = pd.to_datetime(orders_df[column])
order_reviews_df.drop(columns=["review_comment_title", "review_comment_message"], inplace=True)

# Exploratory Data Analysis
orders_df['year_of_purchase'] = orders_df['order_purchase_timestamp'].dt.year
order_per_year_df = orders_df.groupby(by='year_of_purchase').agg({
    'order_id': 'count'
}).reset_index().sort_values(by='year_of_purchase', ascending=True)
order_per_year_df.rename(columns={'order_id': 'total_order'}, inplace=True)
order_customer_df = pd.merge(
    left=orders_df,
    right=customers_df,
    how='left',
    left_on='customer_id',
    right_on='customer_id'
)
order_per_state_df = order_customer_df.groupby(by='customer_state').agg({
    'order_id': 'count'
}).reset_index()
order_per_state_df.rename(columns={'customer_state': 'state', 'order_id': 'total_order'}, inplace=True)
customer_status_df = pd.DataFrame()
customer_status_df["customer_id"] = customers_df["customer_id"]
customer_status_df["status"] = customers_df["customer_id"].isin(orders_df["customer_id"]).map({True: "Active", False: "Inactive"})
customer_status_df = customer_status_df.groupby(by='status').agg({
    'customer_id': 'count'
}).reset_index()
customer_status_df.rename(columns={
    'customer_id': 'total_customer'
}, inplace=True)
review_score_df = order_reviews_df.groupby(by='review_score').agg({
    'review_id': 'count'
}).reset_index()

review_score_df.rename(columns={
    'review_id': 'total_review'
}, inplace=True)
translated_product_category_df = pd.merge(
    left=products_df,
    right=product_category_name_translations_df,
    how="left",
    left_on="product_category_name",
    right_on="product_category_name"
)
translated_product_category_df.drop(columns='product_category_name', inplace=True)
order_items_df.groupby(by='order_item_id').agg({
    'order_id': 'nunique'
})
order_items_product_df = pd.merge(
    left=order_items_df,
    right=translated_product_category_df,
    how="left",
    left_on="product_id",
    right_on="product_id"
)
order_product_category_df = order_items_product_df[['order_id', 'product_category_name_english']].groupby(by='product_category_name_english').agg({
    'order_id': 'count'
}).reset_index()
order_product_category_df.rename(columns={'order_id': 'total_order'}, inplace=True)


# Streamlit Dashboard
st.title("E-Commerce Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.metric(label="Total User", value=customers_df.customer_id.nunique())

with col2:
    st.metric(label="Total Order 2018", value=order_per_year_df[order_per_year_df.year_of_purchase == 2018].total_order, delta=str(int(order_per_year_df[order_per_year_df.year_of_purchase == 2018].total_order) - int(order_per_year_df[order_per_year_df.year_of_purchase == 2017].total_order)) + ' Orders From 2017')

st.header("Pertanyaan Bisnis")
with st.expander("Jumlah Order Berdasarkan State"):
    tab1, tab2 = st.tabs(['Terbanyak', 'Tersedikit'])
    with tab1:
        top_state_df = order_per_state_df.sort_values(by='total_order', ascending=False).head(5)
        
        fig, ax = plt.subplots(figsize=(16,7))
        ax = sns.barplot(data=top_state_df, x='state', y='total_order', hue='state', palette=["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"])
        plt.xticks(rotation=45, ha="right")
        plt.title("Top State based on Order Count")
        plt.xlabel("State")
        plt.ylabel("Order Count")
        st.pyplot(fig)
        st.text("{} merupakan state dengan order terbanyak!".format(top_state_df[top_state_df.total_order == top_state_df.total_order.max()].state.sum()))

    with tab2:
        worst_state_df = order_per_state_df.sort_values(by='total_order', ascending=True).head(5)
        
        fig, ax = plt.subplots(figsize=(16,7))
        ax = sns.barplot(data=worst_state_df, x='state', y='total_order', hue='state', palette=["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"])
        plt.xticks(rotation=45, ha="right")
        plt.title("Worst State based on Order Count")
        plt.xlabel("State")
        plt.ylabel("Order Count")
        st.pyplot(fig)
        st.text("{} merupakan state dengan order paling sedikit!".format(worst_state_df[worst_state_df.total_order == worst_state_df.total_order.min()].state.sum()))
        
with st.expander("Pertumbuhan Jumlah Order per Tahun"):
    fig, ax = plt.subplots(figsize=(16,7))
    
    ax = sns.lineplot(data=order_per_year_df, x=order_per_year_df['year_of_purchase'].astype(str), y='total_order', marker='o')
    plt.xlabel("Year")
    plt.ylabel("Total Order")
    plt.yticks(order_per_year_df.total_order)
    st.pyplot(fig)
    
    st.text("Terdapat peningkatan jumlah order setiap tahunnya yaitu dari {} order di tahun 2016 menjadi {} order di tahun 2017 lalu menjadi {} di tahun 2018".format('272', '43411', '52778'))

with st.expander("Customer Active vs Inactive"):
    fig, ax = plt.subplots(figsize=(16,7))
    
    ax = plt.pie(customer_status_df['total_customer'], labels=customer_status_df['status'], autopct='%1.1f%%', explode=(0, 0.1), colors=["#72BCD4", "#D3D3D3"])
    plt.title('Active vs Inactive Customer')
    st.pyplot(fig)
    
    st.text("Hanya 3% customer yang belum pernah melakukan order!")
    
with st.expander("Order Reviews"):
    fig, ax = plt.subplots(figsize=(16,7))
    
    ax = sns.barplot(data=review_score_df, x='review_score', y='total_review', hue='review_score', palette=["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"])
    plt.title("Review Score Comparison")
    plt.xlabel("Review Score")
    plt.ylabel("Total Review")
    plt.yticks(review_score_df.total_review)
    plt.legend(title="Review Score")
    st.pyplot(fig)
    
    st.text("Score review yang paling banyak diberikan adalah 5!")
    
with st.expander("Best Category"):
    best_category_df = order_product_category_df.sort_values(by='total_order', ascending=False).head(5)
    
    fig, ax = plt.subplots(figsize=(16,7))
    
    ax = sns.barplot(data=best_category_df, x='product_category_name_english', y='total_order', hue='product_category_name_english', palette=["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"])
    plt.xticks(rotation=45, ha="right")
    plt.title("Top Product Category")
    plt.xlabel("Product Category")
    plt.ylabel("Order Count")
    st.pyplot(fig)
    
    st.text("Kategori dengan order paling banyak adalah bed_bath_table!")
    
