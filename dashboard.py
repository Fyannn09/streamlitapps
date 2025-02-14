import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Fungsi untuk memuat data
def load_data():
    aoti = pd.read_csv("PRSA_Data_Aotizhongxin_20130301-20170228.csv")
    changping = pd.read_csv("PRSA_Data_Changping_20130301-20170228.csv")
    dingling = pd.read_csv("PRSA_Data_Dingling_20130301-20170228.csv")
    
    return {"Aotizhongxin": aoti, "Changping": changping, "Dingling": dingling}

# Load data
data_dict = load_data()

# Sidebar untuk memilih lokasi
st.sidebar.title("Filter Data")
location = st.sidebar.selectbox("Pilih Lokasi", list(data_dict.keys()))
df = data_dict[location]

# Konversi kolom waktu
if 'year' in df.columns:
    df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df.set_index('date', inplace=True)

# Menampilkan data
st.title(f"Dashboard Data PRSA - {location}")
st.write("Tampilan data mentah:")
st.dataframe(df.head())

# Plot tren polusi
st.subheader("Tren PM2.5")
fig, ax = plt.subplots()
df['PM2.5'].plot(ax=ax, figsize=(10, 4), title='Konsentrasi PM2.5')
st.pyplot(fig)

# Plot tren suhu
st.subheader("Tren Suhu")
fig, ax = plt.subplots()
df['TEMP'].plot(ax=ax, figsize=(10, 4), title='Suhu (°C)', color='red')
st.pyplot(fig)

# Plot tren hujan
st.subheader("Tren Hujan")
fig, ax = plt.subplots()
df['PRES'].plot(ax=ax, figsize=(10, 4), title='Tekanan Udara (hPa)', color='blue')
st.pyplot(fig)

# Fitur tambahan
st.sidebar.subheader("Filter Rentang Waktu")
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [])

if date_range:
    df_filtered = df.loc[date_range[0]:date_range[1]]
else:
    df_filtered = df

st.subheader("Statistik Deskriptif")
st.write(df_filtered.describe())

st.subheader("Distribusi PM2.5")
fig, ax = plt.subplots()
df_filtered['PM2.5'].hist(ax=ax, bins=30, color='green')
ax.set_title("Histogram PM2.5")
st.pyplot(fig)
