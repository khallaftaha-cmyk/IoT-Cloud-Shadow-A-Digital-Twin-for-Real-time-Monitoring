import React, { useState, useEffect } from 'react';
import DigitalTwin3D from './DigitalTwin3D';
import { 
  Activity, 
  Thermometer, 
  Droplets, 
  Gauge, 
  Battery, 
  Power, 
  AlertTriangle, 
  CheckCircle2, 
  Wifi, 
  Cpu, 
  RefreshCw 
} from 'lucide-react';

const envApiUrl = import.meta.env.VITE_API_URL;
const API_BASE = envApiUrl ? envApiUrl.replace(/\/$/, '') : '/api';

const getWsUrl = () => {
  if (envApiUrl) {
    const isHttps = envApiUrl.startsWith('https');
    const host = envApiUrl.replace(/^https?:\/\//, '').replace(/\/$/, '');
    return `${isHttps ? 'wss:' : 'ws:'}//${host}/ws/twin-status`;
  }
  return `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/twin-status`;
};

const WS_URL = getWsUrl();

export default function App() {
  const [telemetry, setTelemetry] = useState({
    device_id: 'sensor_01',
    temperature: 22.5,
    humidity: 45.0,
    pressure: 1013.2,
    battery_level: 98.0,
    status: 'online',
    last_seen: 'Just now'
  });

  const [alerts, setAlerts] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [actuationStatus, setActuationStatus] = useState('');

  // WebSocket Connection
  useEffect(() => {
    let ws;
    let reconnectDelay = 1000;

    const connectWS = () => {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        setWsConnected(true);
        reconnectDelay = 1000; // reset backoff on successful connect
        console.log('[WS] Connected to Digital Twin stream at', WS_URL);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Ignore server-side keepalive pings (they just prevent nginx timeout)
          if (data.event === 'ping') return;
          if (data.event === 'twin_update' && data.data) {
            setTelemetry((prev) => ({ ...prev, ...data.data, device_id: data.device_id }));
          } else if (data.event === 'alert_triggered') {
            setAlerts((prev) => [data, ...prev.slice(0, 9)]);
          }
        } catch (e) {
          console.error('[WS] Parse error:', e);
        }
      };

      ws.onerror = (err) => {
        console.error('[WS] Connection error — will reconnect in', reconnectDelay, 'ms', err);
      };

      ws.onclose = () => {
        setWsConnected(false);
        // Exponential backoff reconnect (1s → 2s → 4s → … max 30s)
        setTimeout(connectWS, reconnectDelay);
        reconnectDelay = Math.min(reconnectDelay * 2, 30000);
      };
    };

    connectWS();
    return () => ws && ws.close();
  }, []);

  // Send Remote Actuation Command
  const handleActuate = async (command) => {
    setActuationStatus(`Issuing ${command}...`);
    try {
      const res = await fetch(`${API_BASE}/actuate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id: telemetry.device_id, command })
      });
      if (res.ok) {
        setActuationStatus(`Command '${command}' sent successfully!`);
      } else {
        setActuationStatus(`Failed to send '${command}'`);
      }
    } catch (err) {
      setActuationStatus(`Error sending command`);
    }
    setTimeout(() => setActuationStatus(''), 4000);
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="brand">
          <div className="brand-icon">
            <Cpu size={24} color="#000" />
          </div>
          <div>
            <h1>IoT Digital Twin System</h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Real-time 3D Telemetry & AI Control</p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div className="status-badge">
            <div className="status-pulse" style={{ backgroundColor: wsConnected ? 'var(--accent-green)' : 'var(--accent-orange)' }}></div>
            <span>{wsConnected ? 'LIVE STREAM' : 'RECONNECTING'}</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="main-grid">
        {/* Left Column: 3D Viewport & Telemetry Cards */}
        <div>
          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={18} color="var(--accent-cyan)" />
                <span style={{ fontWeight: 600 }}>3D Virtual Twin Viewport</span>
              </div>
              <span className="device-name">{telemetry.device_id}</span>
            </div>

            <div className="canvas-wrapper">
              <DigitalTwin3D telemetry={telemetry} status={telemetry.status} />
            </div>

            {/* Telemetry Stat Cards */}
            <div className="telemetry-grid">
              <div className="metric-card">
                <div className="metric-label">
                  <Thermometer size={16} color="var(--accent-cyan)" />
                  Temperature
                </div>
                <div className="metric-value" style={{ color: telemetry.temperature > 30 ? 'var(--accent-red)' : 'var(--accent-cyan)' }}>
                  {telemetry.temperature}°C
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">
                  <Droplets size={16} color="var(--accent-cyan)" />
                  Humidity
                </div>
                <div className="metric-value">
                  {telemetry.humidity}%
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">
                  <Gauge size={16} color="var(--accent-cyan)" />
                  Pressure
                </div>
                <div className="metric-value">
                  {telemetry.pressure} hPa
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">
                  <Battery size={16} color="var(--accent-green)" />
                  Battery
                </div>
                <div className="metric-value">
                  {telemetry.battery_level}%
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Controls & Alert Feed */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Actuation Control Card */}
          <div className="glass-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Power size={18} color="var(--accent-cyan)" />
              <span style={{ fontWeight: 600 }}>Remote Device Control</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <button 
                className="btn btn-primary"
                onClick={() => handleActuate('COOLING_ON')}
              >
                <RefreshCw size={16} />
                Activate Cooling System
              </button>

              <button 
                className="btn btn-danger"
                onClick={() => handleActuate('EMERGENCY_SHUTDOWN')}
              >
                <Power size={16} />
                Emergency Shutdown
              </button>
            </div>

            {actuationStatus && (
              <div style={{ marginTop: '12px', fontSize: '0.85rem', color: 'var(--accent-cyan)', textAlign: 'center' }}>
                {actuationStatus}
              </div>
            )}
          </div>

          {/* Real-time Alert Feed */}
          <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <AlertTriangle size={18} color="var(--accent-red)" />
              <span style={{ fontWeight: 600 }}>Real-time Alert Feed</span>
            </div>

            <div className="alert-list" style={{ flex: 1 }}>
              {alerts.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px 0', fontSize: '0.85rem' }}>
                  No threshold breaches detected
                </div>
              ) : (
                alerts.map((alert, idx) => (
                  <div key={idx} className={`alert-item ${alert.severity === 'critical' ? 'critical' : 'warning'}`}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{alert.device_id}</span>
                      <span style={{ fontSize: '0.75rem', opacity: 0.8 }}>{alert.severity.toUpperCase()}</span>
                    </div>
                    <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem', opacity: 0.9 }}>{alert.message}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
