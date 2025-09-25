import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import pandas as pd

# --------------------------
# CONFIG
# --------------------------
st.set_page_config(page_title="Smart Fence Guardian 2.0", layout="wide")

st.title("⚡ Smart Fence Guardian 2.0 | Voltage Vikings")
st.subheader("Unauthorized Electric Fence Detection, Localization & Alerts")

feeders = ["Feeder-1", "Feeder-2", "Feeder-3"]
substations = ["Substation-A", "Substation-B"]

if "events" not in st.session_state:
    st.session_state["events"] = []

# --------------------------
# SIMULATION HELPERS
# --------------------------
fs = 20000   # sampling frequency
t = np.linspace(0, 0.04, fs)  # 40ms window

def simulate_signal(unauth=False):
    base = np.sin(2*np.pi*50*t)   # 50 Hz sine (mains)
    noise = 0.02*np.random.randn(len(t))  # small noise
    if unauth:
        pulse = np.zeros_like(t)
        pulse[500:800] = 8 + np.random.rand() * 2  # stronger pulse
        return base + noise + pulse
    return base + noise

def detect_event(signal):
    if np.max(signal) > 3.0:
        feeder = random.choice(feeders)
        substation = random.choice(substations)
        location_km = round(random.uniform(0.5, 2.5), 2)
        return {
            "time": time.strftime("%H:%M:%S"),
            "substation": substation,
            "feeder": feeder,
            "location": f"{location_km} km",
            "status": "Unauthorized Fence"
        }
    return None

# --------------------------
# SIDEBAR CONTROLS
# --------------------------
st.sidebar.header("⚙️ Simulation Controls")
unauth = st.sidebar.checkbox("Inject Unauthorized Fence Pulse", value=False)
show_fft = st.sidebar.checkbox("Show FFT Spectrum", value=True)
show_psd = st.sidebar.checkbox("Show Power Spectral Density", value=True)
show_rms = st.sidebar.checkbox("Show RMS Trend", value=True)
show_heatmap = st.sidebar.checkbox("Show Feeder Event Count", value=True)
send_sms = st.sidebar.checkbox("Simulate SMS Alerts", value=True)
sound_alarm = st.sidebar.checkbox("Activate Siren Alarm", value=True)

# --------------------------
# SIGNAL GENERATION
# --------------------------
signal = simulate_signal(unauth)
event = detect_event(signal)

# --------------------------
# WAVEFORM PLOT
# --------------------------
col1, col2 = st.columns(2)
with col1:
    st.write("### 📈 Line Voltage Signal (40 ms window)")
    fig, ax = plt.subplots()
    ax.plot(t*1000, signal, lw=1)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

# --------------------------
# FFT PLOT
# --------------------------
if show_fft:
    with col2:
        st.write("### 🔍 Frequency Spectrum (FFT)")
        fft_vals = np.abs(np.fft.fft(signal))[:fs//2]
        freqs = np.fft.fftfreq(len(signal), 1/fs)[:fs//2]
        fig2, ax2 = plt.subplots()
        ax2.plot(freqs, fft_vals, lw=1, color="orange")
        ax2.set_xlim(0, 1000)
        ax2.set_xlabel("Frequency (Hz)")
        ax2.set_ylabel("Magnitude")
        st.pyplot(fig2)

# --------------------------
# POWER SPECTRAL DENSITY
# --------------------------
if show_psd:
    st.write("### 📊 Power Spectral Density (Welch Method)")
    from scipy.signal import welch
    f, Pxx = welch(signal, fs, nperseg=1024)
    fig3, ax3 = plt.subplots()
    ax3.semilogy(f, Pxx, color="green")
    ax3.set_xlim(0, 1000)
    ax3.set_xlabel("Frequency (Hz)")
    ax3.set_ylabel("Power/Frequency (dB/Hz)")
    st.pyplot(fig3)

# --------------------------
# RMS TREND
# --------------------------
if show_rms:
    st.write("### 📉 Rolling RMS Trend")
    window = 500
    rms_vals = np.sqrt(np.convolve(signal**2, np.ones(window)/window, mode="valid"))
    fig4, ax4 = plt.subplots()
    ax4.plot(rms_vals, lw=1, color="purple")
    ax4.set_xlabel("Sample Index")
    ax4.set_ylabel("RMS Amplitude")
    st.pyplot(fig4)

# --------------------------
# DETECTION & ALERTS
# --------------------------
if event:
    st.error(f"🚨 Unauthorized Fence Detected at {event['substation']} - {event['feeder']} | {event['location']}")
    if send_sms:
        st.info("📩 SMS Alert Sent to Utility Crew")
    if sound_alarm:
        st.warning("🔊 Siren Alarm Activated at Substation")
    st.session_state["events"].insert(0, event)
else:
    st.success("✅ System Stable - No Unauthorized Fence Detected")

# --------------------------
# MAP VIEW (Kerala)
# --------------------------
st.write("### 🗺️ Map View (Kerala)")
lat = 8.5 + random.random()*0.3
lon = 76.9 + random.random()*0.3
st.map(pd.DataFrame([[lat, lon]], columns=["lat", "lon"]))

# --------------------------
# EVENT HISTORY + HEATMAP
# --------------------------
st.write("### 📜 Event History")
if len(st.session_state["events"]) > 0:
    df_events = pd.DataFrame(st.session_state["events"])
    st.table(df_events)

    if show_heatmap:
        st.write("### 🔥 Feeder Event Count")
        feeder_counts = df_events["feeder"].value_counts()
        fig5, ax5 = plt.subplots()
        feeder_counts.plot(kind="bar", ax=ax5, color="red")
        ax5.set_ylabel("Count")
        st.pyplot(fig5)

    csv = df_events.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Event Log (CSV)", csv, "event_log.csv", "text/csv")
else:
    st.info("No events detected yet.")


