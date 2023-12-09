import sys
from PySide6.QtWidgets import QApplication
from Pyside6_UI_Classes.MainWindow_Class import MainWindow

if __name__ == "__main__":
    app = QApplication([])  # Create a single instance of QApplication

    main_window = MainWindow(app)  # Pass the QApplication instance to MainWindow
    main_window.show()
    sys.exit(app.exec_())  # Call exec_() on the QApplication instance
    
    
# import csv
# import re
# import numpy as np
# import tensorflow as tf
# from sklearn.model_selection import train_test_split
# from datetime import datetime
# import pandas as pd
# import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt
# import pprint

 
# def str_to_datetime(s):   
#     split = s.split('-')
#     year, month, day = int(split[0]), int(split[1]), int(split[2])
#     return datetime(year = year, month = month, day = day)

# def str_to_float(s):
#     # Use regular expression to remove non-numeric characters
#     cleaned_s = re.sub(r'[^0-9.-]', '', s)
#     # Convert to float
#     try:
#         return float(cleaned_s)
#     except ValueError:
#         # If the conversion fails, return None (or any other default value)
#         return None
    
# df = pd.read_csv("Amazon_Test_Data_1.csv")

# df['end'] = df['end'].apply(str_to_datetime)
# # Apply the str_to_float function to convert dollar amounts to float for the next three columns

# df['LiabilitiesCurrent'] = df['LiabilitiesCurrent'].apply(str_to_float)
# df['AssetsCurrent'] = df['AssetsCurrent'].apply(str_to_float)
# df['CostOfGoodsAndServicesSold'] = df['CostOfGoodsAndServicesSold'].apply(str_to_float)

# df.index = df.pop('end')
# df.to_csv("new_file.csv", index=True)


# # print(df)
# # plt.plot(df.index, df['LiabilitiesCurrent'])
# # plt.show()

# def window_data(data, n=3):
#     windowed_data = pd.DataFrame()
#     for i in range(n, 0, -1):
#         windowed_data[f'LiabilitiesCurrent-{i}'] = data['LiabilitiesCurrent'].shift(i)
#         windowed_data[f'AssetsCurrent-{i}'] = data['AssetsCurrent'].shift(i)
#         windowed_data[f'CostOfGoodsAndServicesSold-{i}'] = data['CostOfGoodsAndServicesSold'].shift(i)
#     windowed_data['LiabilitiesCurrent'] = data['LiabilitiesCurrent']
#     windowed_data['AssetsCurrent'] = data['AssetsCurrent']
#     windowed_data['CostOfGoodsAndServicesSold'] = data['CostOfGoodsAndServicesSold']
#     return windowed_data.dropna()

# windowed_dataframe_values = window_data(df)
# windowed_dataframe_values.to_csv("new_file.csv", index=True)
     
# def windowed_df_to_date_X_y(windowed_dataframe):
#     print(windowed_dataframe)
#     windowed_dataframe = windowed_dataframe.reset_index(drop=True)
#     def_as_np = windowed_dataframe.to_numpy()
#     print(def_as_np)
#     dates = def_as_np[:, 0]
#     # print(dates)
    
    
#     middle_Matrix = def_as_np[:, 1:-3]  # Extract the input features (excluding the last three columns)
#     # X = middle_Matrix.reshape((len(dates), -1, 3))  # Reshape for LSTM input
#     X = middle_Matrix
#     Y = def_as_np[:, -3:]  # Extract the last three columns as the target values
    
#     return dates, X.astype(np.float32), Y.astype(np.float32)


# # print(windowed_dataframe_values)

# dates, X, y = windowed_df_to_date_X_y(windowed_dataframe_values)    

# print(dates.shape)
# print(X.shape)
# print(y.shape)
    
# Load and preprocess the data
# data = []
# with open("Amazon_Test_Data_1.csv") as f:
#     reader = csv.reader(f)
#     next(reader)  # Skip the header

#     for row in reader:
#         # Convert the first column to datetime using the str_to_datetime function
#         date_value = str_to_datetime(row[0])
#         # Convert columns 2, 3, and 4 to floating-point numbers
#         input_features = [float(re.sub(r'[^\d.]', '', cell)) for cell in row[1:4]]
#         # Combine the datetime value with the floating-point values
#         input_features.insert(0, date_value)
#         data.append(input_features)

# data = np.array(data)


# # Reshape data for LSTM (samples, timesteps, features)
# X = data[:-1] # (n_samples, 1, n_features)
# y = data[1:]  # Shifted by one row to represent future data (predict the next row)

# # print(f"X start with:{X}")
# # print(f"y start with:{y}")
# # Split the data into training and testing sets while maintaining the chronological order
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)






# # Create an LSTM model
# model = tf.keras.Sequential()
# model.add(tf.keras.layers.LSTM(64, activation='relu', input_shape=(1, 3)))  # LSTM layer with 64 units
# model.add(tf.keras.layers.Dense(32, activation='relu'))
# model.add(tf.keras.layers.Dense(3))  # 3 output neurons for the 3 input features

# model.compile(optimizer='adam', loss='mean_squared_error')

# # Train the LSTM model
# model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test))

# # Use the trained LSTM model to predict the future values
# future_predictions = model.predict(X_test)
# print("Predicted outputs for the future year:")
# print(future_predictions)