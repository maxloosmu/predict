import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices, slow=26, fast=12, signal=9):
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd - signal_line

# Load and preprocess data
data = pd.read_csv('test2.csv', encoding='ISO-8859-1')
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
data = data.sort_values('Date')
data.dropna(subset=['Close'], inplace=True)
data['Volume'] = data['Volume'].str.replace(',', '').astype(int)

# Feature engineering
data['Returns'] = data['Close'].pct_change()
data['MA5'] = data['Close'].rolling(window=5).mean()
data['MA20'] = data['Close'].rolling(window=20).mean()
data['Volatility'] = data['Returns'].rolling(window=20).std()
data['RSI'] = calculate_rsi(data['Close'], window=14)  # New RSI feature
data['MACD'] = calculate_macd(data['Close'])  # New MACD feature
data = data.dropna()

features = ['Open', 'High', 'Low', 'Close', 'Volume', 'Returns', 'MA5', 'MA20', 'Volatility', 'RSI', 'MACD']
X = data[features].values[:-1]
y = data['Close'].values[1:]

# Use MinMaxScaler for better performance with neural networks
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()

# Time series split with a longer history
tscv = TimeSeriesSplit(n_splits=5, test_size=30)  # Increased test_size
for train_index, test_index in tscv.split(X_scaled):
    X_train, X_test = X_scaled[train_index], X_scaled[test_index]
    y_train, y_test = y_scaled[train_index], y_scaled[test_index]

# Reshape X for CNN-LSTM
X_train_reshaped = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test_reshaped = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# Define and train the CNN-LSTM model
model = Sequential([
    Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(X_train_reshaped.shape[1], 1)),
    MaxPooling1D(pool_size=2),
    LSTM(100, return_sequences=True),  # Increased units
    LSTM(100),  # Increased units
    Dense(50, activation='relu'),  # Increased units
    Dropout(0.3),  # Increased dropout
    Dense(1)
])

model.compile(optimizer=Adam(learning_rate=0.0005), loss='mse')  # Reduced learning rate
early_stopping = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)  # Increased patience

history = model.fit(X_train_reshaped, y_train, epochs=200, batch_size=32, validation_split=0.2,
                    callbacks=[early_stopping], verbose=1)

# Make predictions
def predict_next_day(model, scaler_X, scaler_y, last_day_data):
    input_data = scaler_X.transform(last_day_data.reshape(1, -1))
    input_data_reshaped = input_data.reshape((1, input_data.shape[1], 1))
    prediction_scaled = model.predict(input_data_reshaped)
    prediction = scaler_y.inverse_transform(prediction_scaled)
    return prediction[0][0]

# Get the last day of data
last_day = data[features].iloc[-1].values

# Print the last day's data
print("Last day's data used for prediction:")
print(data[['Date'] + features].iloc[-1])
print("\n")

# Make prediction
next_day_close = predict_next_day(model, scaler_X, scaler_y, last_day)
print(f"Predicted Close price for the next day: {next_day_close:.2f}")

last_known_close = data['Close'].iloc[-1]
print(f"Last known Close price: {last_known_close:.2f}")
print(f"Prediction difference from last known Close: {abs(next_day_close - last_known_close):.2f}")

# Print the shape of the data
print(f"\nShape of the data: {data.shape}")
print(f"Date range: from {data['Date'].min()} to {data['Date'].max()}")
