import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import folium
from streamlit_folium import folium_static

# Fungsi untuk memuat data
def load_data():
    aoti = pd.read_csv("PRSA_Data_Aotizhongxin_20130301-20170228.csv")
    changping = pd.read_csv("PRSA_Data_Changping_20130301-20170228.csv")
    dingling = pd.read_csv("PRSA_Data_Dingling_20130301-20170228.csv")
    
    return {"Aotizhongxin": aoti, "Changping": changping, "Dingling": dingling}

# Koordinat lokasi
location_coords = {
    "Aotizhongxin": [39.982, 116.304],
    "Changping": [40.218, 116.234],
    "Dingling": [40.295, 116.220]
}

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

# Sidebar untuk rentang tanggal
st.sidebar.subheader("Filter Rentang Waktu")
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [])
if date_range:
    df_filtered = df.loc[date_range[0]:date_range[1]]
else:
    df_filtered = df

# Statistik Deskriptif
st.subheader("Statistik Deskriptif")
st.write(df_filtered.describe())

# Histogram PM2.5
st.subheader("Distribusi PM2.5")
fig, ax = plt.subplots()
sns.histplot(df_filtered['PM2.5'].dropna(), bins=30, kde=True, ax=ax)
ax.set_xlabel("PM2.5")
ax.set_ylabel("Frekuensi")
st.pyplot(fig)

# Tren PM2.5
st.subheader("Tren PM2.5")
fig, ax = plt.subplots()
df_filtered['PM2.5'].plot(ax=ax, figsize=(10, 4), title='Konsentrasi PM2.5')
st.pyplot(fig)

# Geoanalysis - Peta Polusi PM2.5
st.subheader("Peta Polusi PM2.5")
avg_pm25 = df_filtered['PM2.5'].mean()
map_center = location_coords[location]
m = folium.Map(location=map_center, zoom_start=10)
folium.CircleMarker(
    location=map_center,
    radius=avg_pm25 / 10,
    color='red' if avg_pm25 > 75 else 'orange' if avg_pm25 > 35 else 'green',
    fill=True,
    fill_color='red' if avg_pm25 > 75 else 'orange' if avg_pm25 > 35 else 'green',
    fill_opacity=0.6,
    popup=f"{location}: {avg_pm25:.2f} µg/m³"
).add_to(m)
folium_static(m)

# Tren Suhu
st.subheader("Tren Suhu")
fig, ax = plt.subplots()
df_filtered['TEMP'].plot(ax=ax, figsize=(10, 4), title='Suhu (°C)', color='red')
st.pyplot(fig)

# Tren Tekanan Udara
st.subheader("Tren Tekanan Udara")
fig, ax = plt.subplots()
df_filtered['PRES'].plot(ax=ax, figsize=(10, 4), title='Tekanan Udara (hPa)', color='blue')
st.pyplot(fig)

# Tren Musiman PM2.5
st.subheader("Tren Musiman PM2.5")
df_filtered['month'] = df_filtered.index.month
df_monthly = df_filtered.groupby('month')['PM2.5'].mean()
fig, ax = plt.subplots()
df_monthly.plot(kind='bar', ax=ax, title='Rata-rata PM2.5 Bulanan')
st.pyplot(fig)

# Scatter Plot: Hubungan Suhu dan PM2.5
st.subheader("Hubungan Suhu dan PM2.5")
fig, ax = plt.subplots()
sns.scatterplot(x=df_filtered['TEMP'], y=df_filtered['PM2.5'], ax=ax)
ax.set_xlabel("Suhu (°C)")
ax.set_ylabel("PM2.5")
st.pyplot(fig)

# Heatmap Korelasi (Hanya Kolom Numerik)
st.subheader("Heatmap Korelasi")
df_numeric = df_filtered.select_dtypes(include=[np.number]).dropna()
fig, ax = plt.subplots(figsize=(8,6))
sns.heatmap(df_numeric.corr(), annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

# Moving Average PM2.5
st.subheader("Rata-rata Pergerakan PM2.5")
window_size = st.slider("Pilih Window Size", 1, 48, 24)
df_filtered['PM2.5 MA'] = df_filtered['PM2.5'].rolling(window=window_size).mean()
fig, ax = plt.subplots()
df_filtered[['PM2.5', 'PM2.5 MA']].plot(ax=ax, figsize=(10, 4), title=f'Rata-rata Pergerakan {window_size}-Jam')
st.pyplot(fig)

# Perbandingan Rata-rata PM2.5 antar Lokasi
st.subheader("Perbandingan Polusi Antar Lokasi")
locations_avg = {loc: data['PM2.5'].mean() for loc, data in data_dict.items()}
st.bar_chart(pd.Series(locations_avg, name='Rata-rata PM2.5'))

# Analisis Hari dengan Polusi Tertinggi
st.subheader("Hari dengan PM2.5 Tertinggi")
highest_pm25 = df_filtered['PM2.5'].idxmax()
st.write(f"Hari dengan PM2.5 tertinggi: {highest_pm25}")

# Boxplot Distribusi PM2.5
st.subheader("Boxplot PM2.5")
fig, ax = plt.subplots()
sns.boxplot(y=df_filtered['PM2.5'], ax=ax)
ax.set_title("Distribusi PM2.5")
st.pyplot(fig)

# Tombol Unduh Data
st.sidebar.subheader("Unduh Data")
csv = df_filtered.to_csv().encode('utf-8')
st.sidebar.download_button("Download Data", csv, "filtered_data.csv", "text/csv")
