import pandas as pd
import geopandas as gp
import folium as fo
import streamlit as st
from streamlit_folium import folium_static


st.title('Streamlit Buffer Example')
add_select = st.sidebar.selectbox("What basemap do you want to see?",("OpenStreetMap", "Stamen Terrain","Stamen Toner"))


df = pd.read_csv('https://raw.githubusercontent.com/Maplub/MonthlyAirQuality/master/sensorlist.csv')


crs = "EPSG:4326"
geometry = gp.points_from_xy(df.lon,df.lat)
geo_df  = gp.GeoDataFrame(df,crs=crs,geometry=geometry)

nan_boundary  = gp.read_file('https://github.com/Maplub/AirQualityData/blob/master/nan_shp_wgs84.zip?raw=true')
nanall = nan_boundary.unary_union


# select only stations within Nan province
nan_sta = geo_df.loc[geo_df.geometry.within(nanall)]


#create buffer
nan_UTM = nan_sta.to_crs("EPSG:32647")

buffersize = 500
nan_UTM['buffer'] = nan_UTM['geometry'].buffer(buffersize)
#change buffer column to WGS84
nan_UTM['buffer'] = nan_UTM['buffer'].to_crs("EPSG:4326")


#create map
longitude = 100.819200
latitude = 19.331900

station_map = fo.Map(
  tiles=add_select,
	location = [latitude, longitude], 
	zoom_start = 10)

latitudes = list(nan_UTM.lat)
longitudes = list(nan_UTM.lon)
labels = list(nan_UTM.name)


for lat, lng, name in zip(latitudes, longitudes, labels):
    fo.CircleMarker(
      location = [lat, lng], 
      radius = 1,
      color='#f56042',
      fill=True,
      fill_opacity=1
     ).add_to(station_map)

for _,r in nan_UTM.iterrows():
    sim_geo = gp.GeoSeries(r['buffer'])
    geo_j = sim_geo.to_json()
    geo_j = fo.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'orange'})
    geo_j.add_to(station_map)