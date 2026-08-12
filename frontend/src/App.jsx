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

const API_BASE = '/api';
const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/twin-status`;

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
    const connectWS = () => {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        setWsConnected(true);
        console.log('[WS] Connected to Digital Twin stream');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === 'twin_update' && data.data) {
            setTelemetry((prev) => ({ ...prev, ...data.data, device_id: data.device_id }));
          } else if (data.event === 'alert_triggered') {
            setAlerts((prev) => [data, ...prev.slice(0, 9)]);
          }
        } catch (e) {
          console.error('[WS] Parse error:', e);
        }
      };

      ws.onclose = () => {
        setWsConnected(false);
        setTimeout(connectWS, 3000); // Auto reconnect
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
                  <Droplets size={16} color="var(--accent-blue)" />
                  Humidity
                </div>
                <div className="metric-value">
                  {telemetry.humidity || 45.0}%
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">
                  <Gauge size={16} color="var(--accent-green)" />
                  Pressure
                </div>
                <div className="metric-value">
                  {telemetry.pressure || 1013.2} hPa
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">
                  <Battery size={16} color="var(--accent-orange)" />
                  Battery
                </div>
                <div className="metric-value">
                  {telemetry.battery_level || 98.0}%
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Actuation & Alert Management */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Actuation Control Panel */}
          <div className="glass-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Power size={18} color="var(--accent-cyan)" />
              <span style={{ fontWeight: 600 }}>Remote Actuation Control</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Send bi-directional control signals directly to physical device or digital twin.
            </p>

            <div className="actuation-buttons">
              <button className="btn btn-primary" onClick={() => handleActuate('COOLING_ON')}>
                <RefreshCw size={16} /> Activate Cooling System
              </button>
              <button className="btn btn-primary" style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }} onClick={() => handleActuate('HEATING_OFF')}>
                <CheckCircle2 size={16} /> Disengage Heater
              </button>
              <button className="btn btn-danger" onClick={() => handleActuate('EMERGENCY_SHUTDOWN')}>
                <AlertTriangle size={16} /> Emergency Thermal Cutoff
              </button>
            </div>

            {actuationStatus && (
              <div style={{ marginTop: '12px', fontSize: '0.85rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                {actuationStatus}
              </div>
            )}
          </div>

          {/* Live Alert Engine Feed */}
          <div className="glass-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <AlertTriangle size={18} color="var(--accent-orange)" />
              <span style={{ fontWeight: 600 }}>Real-Time Threshold Alerts</span>
            </div>

            <div className="alerts-list">
              {alerts.length === 0 ? (
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>
                  No threshold breaches detected. All systems nominal.
                </div>
              ) : (
                alerts.map((alert, idx) => (
                  <div key={idx} className={`alert-item alert-${alert.severity}`}>
                    <AlertTriangle size={16} color={alert.severity === 'critical' ? 'var(--accent-red)' : 'var(--accent-orange)'} />
                    <div>
                      <div style={{ fontWeight: 600 }}>{alert.message}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{new Date(alert.triggered_at).toLocaleTimeString()}</div>
                    </div>
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
