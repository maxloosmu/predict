import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense
from sklearn.svm import SVR

# Step 1: Load the CSV data
data = pd.read_csv('test.csv', encoding='ISO-8859-1')

# Step 2: Preprocessing the data
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
data = data.sort_values('Date')
data.dropna(subset=['Close'], inplace=True)
data['Volume'] = data['Volume'].str.replace(',', '').astype(int)

# Define features and target
features = ['Open', 'High', 'Low', 'Close', 'Volume']
X = data[features].values[:-1]
y = data['Close'].values[1:]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler_X = StandardScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)

# Scale the target (Close prices)
scaler_y = StandardScaler()
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

# Reshape X for CNN
X_train_cnn = X_train_scaled.reshape(X_train_scaled.shape[0], X_train_scaled.shape[1], 1)
X_test_cnn = X_test_scaled.reshape(X_test_scaled.shape[0], X_test_scaled.shape[1], 1)

# Define and train the CNN model
cnn_model = Sequential([
    Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(X_train_cnn.shape[1], 1)),
    MaxPooling1D(pool_size=2),
    Flatten(),
    Dense(50, activation='relu'),
    Dense(50, activation='relu'),
    Dense(1)
])
cnn_model.compile(optimizer='adam', loss='mse')
cnn_model.fit(X_train_cnn, y_train_scaled, epochs=50, batch_size=32, verbose=0)

# Create CNN feature extractor
cnn_feature_extractor = Sequential(cnn_model.layers[:-1])

# Extract features for SVM
X_train_features = cnn_feature_extractor.predict(X_train_cnn)
X_test_features = cnn_feature_extractor.predict(X_test_cnn)

# Train SVM model
svm_model = SVR(kernel='rbf')
svm_model.fit(X_train_features, y_train_scaled)

def predict_next_day(cnn_model, svm_model, scaler_X, scaler_y, last_day_data):
    input_data = scaler_X.transform(last_day_data.reshape(1, -1))
    input_data_cnn = input_data.reshape(1, input_data.shape[1], 1)
    features = cnn_feature_extractor.predict(input_data_cnn)
    prediction_scaled = svm_model.predict(features)
    prediction = scaler_y.inverse_transform(prediction_scaled.reshape(-1, 1))
    return prediction[0][0]

# Get the last day of data
last_day = data[features].iloc[-1].values

# Make prediction
next_day_close = predict_next_day(cnn_model, svm_model, scaler_X, scaler_y, last_day)

print(f"Predicted Close price for the next day: {next_day_close:.2f}")
last_known_close = data['Close'].iloc[-1]
print(f"Last known Close price: {last_known_close:.2f}")
print(f"Prediction difference from last known Close: {abs(next_day_close - last_known_close):.2f}")