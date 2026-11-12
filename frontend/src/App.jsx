import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  Car,
  CheckCircle2,
  ChevronRight,
  Clock3,
  LayoutDashboard,
  Menu,
  Moon,
  RefreshCw,
  Search,
  Settings,
  Shield,
  ShieldAlert,
  Sun,
  Users,
  Video,
  X,
  XCircle,
} from "lucide-react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

// =========================================================
// HELPERS
// =========================================================

function formatEventName(type) {
  if (!type) return "Unknown";

  return String(type)
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatDuration(value) {
  if (
    value === null ||
    value === undefined ||
    value === "" ||
    value === "0" ||
    value === 0
  ) {
    return "-";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return value;
  }

  return `${number.toFixed(1)}s`;
}

function formatConfidence(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "-";
  }

  return `${(number * 100).toFixed(1)}%`;
}

function formatTimestamp(timestamp) {
  if (!timestamp) return "-";

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleString([], {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatTimeOnly(timestamp) {
  if (!timestamp) return "-";

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function getEventLevel(type) {
  switch (String(type || "").toUpperCase()) {
    case "REPEATED_VIOLATION":
      return "critical";

    case "LOITERING":
      return "warning";

    case "ENTER":
    case "EXIT":
      return "normal";

    default:
      return "normal";
  }
}

function getEventSummary(event) {
  const object = event.object_type || "Unknown object";
  const zone = event.zone_name || "the monitored zone";
  const duration = formatDuration(event.duration_sec);

  switch (String(event.event_type || "").toUpperCase()) {
    case "ENTER":
      return `${object} #${event.track_id || "-"} entered ${zone}.`;

    case "EXIT":
      return `${object} #${event.track_id || "-"} exited ${zone} after remaining for ${duration}.`;

    case "LOITERING":
      return `${object} #${event.track_id || "-"} remained inside ${zone} for ${duration}, triggering a loitering event.`;

    case "REPEATED_VIOLATION":
      return `${object} #${event.track_id || "-"} triggered a repeated violation after multiple entries into ${zone}.`;

    default:
      return `${object} #${event.track_id || "-"} generated a ${formatEventName(
        event.event_type
      )} event in ${zone}.`;
  }
}

// =========================================================
// REUSABLE COMPONENTS
// =========================================================

function EventBadge({ type }) {
  const level = getEventLevel(type);

  return (
    <span className={`event-badge ${level}`}>
      {level === "critical" && <ShieldAlert size={13} />}
      {level === "warning" && <AlertTriangle size={13} />}
      {level === "normal" && <Activity size={13} />}

      {formatEventName(type)}
    </span>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  description,
  tone = "blue",
}) {
  return (
    <div className={`stat-card ${tone}`}>
      <div className="stat-card-top">
        <div className="stat-icon">
          <Icon size={19} />
        </div>
      </div>

      <div className="stat-value">{value}</div>

      <div className="stat-title">{title}</div>

      {description && (
        <div className="stat-description">{description}</div>
      )}
    </div>
  );
}

function SectionHeader({
  eyebrow,
  title,
  description,
  action,
}) {
  return (
    <div className="section-header">
      <div>
        {eyebrow && (
          <div className="section-kicker">{eyebrow}</div>
        )}

        <h2>{title}</h2>

        {description && (
          <p className="section-description">{description}</p>
        )}
      </div>

      {action && (
        <div className="section-action">{action}</div>
      )}
    </div>
  );
}

function EmptyState({
  icon: Icon = Activity,
  title,
  description,
}) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        <Icon size={24} />
      </div>

      <h3>{title}</h3>

      <p>{description}</p>
    </div>
  );
}

// =========================================================
// MAIN APP
// =========================================================

function App() {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);

  const [activePage, setActivePage] = useState("dashboard");

  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("ALL");
  const [dateFilter, setDateFilter] = useState("");

  const [selectedEvent, setSelectedEvent] = useState(null);

  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState("");

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("rakshak-theme") || "dark";
  });

  const [autoRefresh, setAutoRefresh] = useState(() => {
    return localStorage.getItem("rakshak-auto-refresh") !== "false";
  });

  const [sidebarOpen, setSidebarOpen] = useState(false);

  // =======================================================
  // THEME
  // =======================================================

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("rakshak-theme", theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem(
      "rakshak-auto-refresh",
      String(autoRefresh)
    );
  }, [autoRefresh]);

  // =======================================================
  // LOAD DATA
  // =======================================================

  async function loadDashboard() {
    try {
      setError("");

      const eventUrl = dateFilter
        ? `${API_BASE}/api/events?limit=100&date=${dateFilter}`
        : `${API_BASE}/api/events?limit=100`;

      const [
        healthResponse,
        statsResponse,
        eventsResponse,
      ] = await Promise.all([
        fetch(`${API_BASE}/api/health`),
        fetch(`${API_BASE}/api/stats`),
        fetch(eventUrl),
      ]);

      if (
        !healthResponse.ok ||
        !statsResponse.ok ||
        !eventsResponse.ok
      ) {
        throw new Error(
          "Unable to connect to RakshakAI API."
        );
      }

      const healthData = await healthResponse.json();
      const statsData = await statsResponse.json();
      const eventsData = await eventsResponse.json();

      setHealth(healthData);
      setStats(statsData);
      setEvents(eventsData.events || []);
      setLastUpdated(new Date());
    } catch (err) {
      setError(
        err?.message ||
          "Unable to connect to RakshakAI API."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, [dateFilter]);

  useEffect(() => {
    if (!autoRefresh) return undefined;

    const interval = setInterval(() => {
      loadDashboard();
    }, 5000);

    return () => clearInterval(interval);
  }, [autoRefresh, dateFilter]);

  // =======================================================
  // NAVIGATION
  // =======================================================

  function navigateTo(page) {
    setActivePage(page);
    setSidebarOpen(false);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  // =======================================================
  // FILTERED EVENTS
  // =======================================================

  const filteredEvents = useMemo(() => {
    const searchText = search.toLowerCase().trim();

    return events.filter((event) => {
      const eventType = String(
        event.event_type || ""
      ).toUpperCase();

      const matchesType =
        filter === "ALL" || eventType === filter;

      const matchesSearch =
        !searchText ||
        eventType.toLowerCase().includes(searchText) ||
        String(event.object_type || "")
          .toLowerCase()
          .includes(searchText) ||
        String(event.track_id || "")
          .toLowerCase()
          .includes(searchText) ||
        String(event.zone_name || "")
          .toLowerCase()
          .includes(searchText);

      return matchesType && matchesSearch;
    });
  }, [events, filter, search]);

  // =======================================================
  // ANALYTICS
  // =======================================================

  const chartData = [
    {
      name: "Entry",
      value: stats?.enter_events ?? 0,
    },
    {
      name: "Exit",
      value: stats?.exit_events ?? 0,
    },
    {
      name: "Loitering",
      value: stats?.loitering_events ?? 0,
    },
    {
      name: "Repeated",
      value: stats?.repeated_violations ?? 0,
    },
  ];

  const objectData = useMemo(() => {
    const counts = {};

    events.forEach((event) => {
      const object = event.object_type || "Unknown";

      counts[object] =
        (counts[object] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([name, value]) => ({
        name,
        value,
      }))
      .sort((a, b) => b.value - a.value);
  }, [events]);

  const zoneData = useMemo(() => {
    const counts = {};

    events.forEach((event) => {
      const zone =
        event.zone_name || "Unknown Zone";

      counts[zone] =
        (counts[zone] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([name, value]) => ({
        name,
        value,
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6);
  }, [events]);

  const alerts = useMemo(() => {
    return events.filter((event) => {
      const level = getEventLevel(
        event.event_type
      );

      return (
        level === "critical" ||
        level === "warning"
      );
    });
  }, [events]);

  const criticalAlerts = alerts.filter(
    (event) =>
      getEventLevel(event.event_type) ===
      "critical"
  );

  const warningAlerts = alerts.filter(
    (event) =>
      getEventLevel(event.event_type) ===
      "warning"
  );

  // =======================================================
  // NAV ITEMS
  // =======================================================

  const navItems = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: LayoutDashboard,
    },
    {
      id: "monitoring",
      label: "Live Monitoring",
      icon: Video,
    },
    {
      id: "alerts",
      label: "Alerts",
      icon: Bell,
      badge:
        alerts.length > 0
          ? alerts.length
          : null,
    },
    {
      id: "events",
      label: "Detection Events",
      icon: Activity,
    },
    {
      id: "analytics",
      label: "Analytics",
      icon: BarChart3,
    },
    {
      id: "settings",
      label: "Settings",
      icon: Settings,
    },
  ];

  // =======================================================
  // DASHBOARD
  // =======================================================

  function renderDashboard() {
    return (
      <>
        <PageHeader
          eyebrow="SECURITY OVERVIEW"
          title="Security Dashboard"
          description="Real-time overview of restricted-zone activity and safety events."
        />

        <section className="stats-grid">
          <StatCard
            title="Total Events"
            value={stats?.total_events ?? 0}
            icon={Activity}
            description="Recorded system events"
          />

          <StatCard
            title="Zone Entries"
            value={stats?.enter_events ?? 0}
            icon={ArrowDownRight}
            description="Objects entering zone"
          />

          <StatCard
            title="Zone Exits"
            value={stats?.exit_events ?? 0}
            icon={ArrowUpRight}
            description="Objects leaving zone"
          />

          <StatCard
            title="Loitering"
            value={stats?.loitering_events ?? 0}
            icon={Clock3}
            description="Extended zone presence"
            tone="warning"
          />

          <StatCard
            title="Repeated Violations"
            value={stats?.repeated_violations ?? 0}
            icon={AlertTriangle}
            description="Repeated activity detected"
            tone="danger"
          />
        </section>

        <section className="dashboard-grid">
          <div className="panel monitoring-panel">
            <SectionHeader
              eyebrow="MONITORING"
              title="Live Camera Feed"
              description="Current restricted-zone camera stream."
              action={
                <button
                  className="text-button"
                  onClick={() =>
                    navigateTo("monitoring")
                  }
                >
                  Full monitoring
                  <ChevronRight size={14} />
                </button>
              }
            />

            <div className="camera-frame dashboard-camera">
              <img
                src={`${API_BASE}/api/video`}
                alt="RakshakAI live camera feed"
                className="live-camera-feed"
              />

              <div className="camera-overlay">
                <div className="camera-status">
                  <span className="live-dot" />
                  LIVE
                </div>

                <div className="camera-label">
                  RAKSHAK AI · CAMERA 01
                </div>
              </div>
            </div>
          </div>

          <div className="panel activity-panel">
            <SectionHeader
              eyebrow="ACTIVITY"
              title="Latest Events"
              description="Most recent detection activity."
              action={
                <span className="count-pill">
                  {events.length} recorded
                </span>
              }
            />

            <div className="recent-events">
              {events.slice(0, 6).map(
                (event, index) => (
                  <button
                    className="recent-event"
                    key={`${event.timestamp}-${event.track_id}-${index}`}
                    onClick={() =>
                      setSelectedEvent(event)
                    }
                  >
                    <div className="recent-event-icon">
                      {getEventLevel(
                        event.event_type
                      ) === "critical" ? (
                        <ShieldAlert size={16} />
                      ) : getEventLevel(
                          event.event_type
                        ) === "warning" ? (
                        <AlertTriangle size={16} />
                      ) : (
                        <Activity size={16} />
                      )}
                    </div>

                    <div className="recent-event-content">
                      <div className="recent-event-title">
                        {formatEventName(
                          event.event_type
                        )}
                      </div>

                      <div className="recent-event-meta">
                        {event.object_type ||
                          "Unknown object"}

                        {event.zone_name
                          ? ` · ${event.zone_name}`
                          : ""}
                      </div>
                    </div>

                    <div className="recent-event-right">
                      <EventBadge
                        type={event.event_type}
                      />

                      <span className="recent-event-time">
                        {formatTimeOnly(
                          event.timestamp
                        )}
                      </span>
                    </div>
                  </button>
                )
              )}

              {events.length === 0 && (
                <EmptyState
                  title="No events recorded"
                  description="Detection events will appear here when the monitoring pipeline records them."
                />
              )}
            </div>
          </div>

          <div className="panel analytics-panel">
            <SectionHeader
              eyebrow="ANALYTICS"
              title="Event Overview"
              description="Distribution of recorded detection events."
              action={
                <button
                  className="text-button"
                  onClick={() =>
                    navigateTo("analytics")
                  }
                >
                  View analytics
                  <ChevronRight size={14} />
                </button>
              }
            />

            <div className="chart-container">
              <ResponsiveContainer
                width="100%"
                height={300}
              >
                <BarChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    opacity={0.12}
                  />

                  <XAxis dataKey="name" />

                  <YAxis
                    allowDecimals={false}
                  />

                  <Tooltip />

                  <Bar
                    dataKey="value"
                    radius={[
                      6,
                      6,
                      0,
                      0,
                    ]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="status-strip">
          <div className="status-strip-item">
            <div className="status-strip-icon success">
              <CheckCircle2 size={17} />
            </div>

            <div>
              <span>Detection Engine</span>
              <strong>Operational</strong>
            </div>
          </div>

          <div className="status-strip-item">
            <div className="status-strip-icon blue">
              <Video size={17} />
            </div>

            <div>
              <span>Camera Stream</span>
              <strong>
                {health?.stream_frame_exists
                  ? "Available"
                  : "Waiting"}
              </strong>
            </div>
          </div>

          <div className="status-strip-item">
            <div className="status-strip-icon blue">
              <Activity size={17} />
            </div>

            <div>
              <span>Event Storage</span>
              <strong>
                {health?.events_file_exists
                  ? "Active"
                  : "Waiting"}
              </strong>
            </div>
          </div>
        </section>
      </>
    );
  }

  // =======================================================
  // MONITORING
  // =======================================================

  function renderMonitoring() {
    return (
      <>
        <PageHeader
          eyebrow="LIVE MONITORING"
          title="Restricted Zone Monitoring"
          description="Monitor the active camera feed and system status in real time."
        />

        <section className="monitoring-layout">
          <div className="panel camera-panel">
            <SectionHeader
              eyebrow="CAMERA 01"
              title="Live Video Stream"
              description="Real-time monitoring feed from the detection pipeline."
              action={
                <div className="live-status">
                  <span className="live-dot" />
                  System Online
                </div>
              }
            />

            <div className="camera-frame large-camera">
              <img
                src={`${API_BASE}/api/video`}
                alt="RakshakAI live camera feed"
                className="live-camera-feed"
              />

              <div className="camera-overlay">
                <div className="camera-status">
                  <span className="live-dot" />
                  LIVE
                </div>

                <div className="camera-label">
                  RAKSHAK AI · RESTRICTED ZONE
                </div>
              </div>
            </div>

            <div className="camera-footer">
              <div>
                <span>Stream</span>
                <strong>
                  {health?.stream_frame_exists
                    ? "Connected"
                    : "Waiting for frame"}
                </strong>
              </div>

              <div>
                <span>Detection</span>
                <strong>YOLO + ByteTrack</strong>
              </div>

              <div>
                <span>Events</span>
                <strong>
                  {events.length} loaded
                </strong>
              </div>
            </div>
          </div>

          <div className="panel monitoring-side-panel">
            <SectionHeader
              eyebrow="SYSTEM STATUS"
              title="Pipeline Health"
            />

            <div className="health-list">
              <HealthRow
                label="API Service"
                value={
                  health?.status === "ok"
                    ? "Operational"
                    : "Checking"
                }
                online={
                  health?.status === "ok"
                }
              />

              <HealthRow
                label="Event Storage"
                value={
                  health?.events_file_exists
                    ? "Available"
                    : "Waiting"
                }
                online={
                  health?.events_file_exists
                }
              />

              <HealthRow
                label="Camera Stream"
                value={
                  health?.stream_frame_exists
                    ? "Available"
                    : "Waiting"
                }
                online={
                  health?.stream_frame_exists
                }
              />

              <HealthRow
                label="Auto Refresh"
                value={
                  autoRefresh
                    ? "Enabled"
                    : "Paused"
                }
                online={autoRefresh}
              />
            </div>

            <div className="monitoring-note">
              <Shield size={18} />

              <div>
                <strong>
                  Restricted zone protection
                </strong>

                <p>
                  Detection events are monitored
                  continuously and recorded for
                  later review.
                </p>
              </div>
            </div>
          </div>
        </section>
      </>
    );
  }

  // =======================================================
  // ALERTS
  // =======================================================

  function renderAlerts() {
    return (
      <>
        <PageHeader
          eyebrow="SAFETY ALERTS"
          title="Alerts & Violations"
          description="Review warning and critical activity detected by the monitoring system."
        />

        <div className="alert-summary-grid">
          <div className="alert-summary critical">
            <ShieldAlert size={20} />

            <div>
              <span>Critical Alerts</span>
              <strong>
                {criticalAlerts.length}
              </strong>
            </div>
          </div>

          <div className="alert-summary warning">
            <AlertTriangle size={20} />

            <div>
              <span>Warnings</span>
              <strong>
                {warningAlerts.length}
              </strong>
            </div>
          </div>

          <div className="alert-summary normal">
            <Activity size={20} />

            <div>
              <span>Total Events</span>
              <strong>{events.length}</strong>
            </div>
          </div>
        </div>

        <div className="panel alerts-panel">
          <SectionHeader
            eyebrow="EVENT ALERTS"
            title="Recent Warnings & Critical Events"
            description="Select an alert to inspect the complete event details."
          />

          <div className="alerts-list">
            {alerts.map((event, index) => (
              <button
                key={`${event.timestamp}-${event.track_id}-${index}`}
                className={`alert-item ${getEventLevel(
                  event.event_type
                )}`}
                onClick={() =>
                  setSelectedEvent(event)
                }
              >
                <div className="alert-icon">
                  {getEventLevel(
                    event.event_type
                  ) === "critical" ? (
                    <ShieldAlert size={19} />
                  ) : (
                    <AlertTriangle size={19} />
                  )}
                </div>

                <div className="alert-content">
                  <div className="alert-title">
                    {formatEventName(
                      event.event_type
                    )}
                  </div>

                  <div className="alert-description">
                    {getEventSummary(event)}
                  </div>

                  <div className="alert-meta">
                    <span>
                      {formatTimestamp(
                        event.timestamp
                      )}
                    </span>

                    <span>
                      {event.zone_name ||
                        "Unknown zone"}
                    </span>

                    <span>
                      Track #
                      {event.track_id ||
                        "-"}
                    </span>
                  </div>
                </div>

                <ChevronRight size={18} />
              </button>
            ))}

            {alerts.length === 0 && (
              <EmptyState
                icon={CheckCircle2}
                title="No active alerts"
                description="No warning or critical events have been recorded."
              />
            )}
          </div>
        </div>
      </>
    );
  }

  // =======================================================
  // EVENTS
  // =======================================================

  function renderEvents() {
    return (
      <>
        <PageHeader
          eyebrow="EVENT LOG"
          title="Detection Events"
          description="Search, filter and inspect recorded security events."
        />

        <div className="panel events-panel">
          <div className="event-toolbar">
            <div className="search-box">
              <Search size={16} />

              <input
                type="text"
                placeholder="Search event, object, track ID or zone..."
                value={search}
                onChange={(e) =>
                  setSearch(e.target.value)
                }
              />
            </div>

            <select
              value={filter}
              onChange={(e) =>
                setFilter(e.target.value)
              }
            >
              <option value="ALL">
                All Events
              </option>

              <option value="ENTER">
                Entry
              </option>

              <option value="EXIT">
                Exit
              </option>

              <option value="LOITERING">
                Loitering
              </option>

              <option value="REPEATED_VIOLATION">
                Repeated Violation
              </option>
            </select>

            <div className="date-filter">
              <input
                type="date"
                value={dateFilter}
                onChange={(e) =>
                  setDateFilter(
                    e.target.value
                  )
                }
              />

              {dateFilter && (
                <button
                  className="clear-filter"
                  onClick={() =>
                    setDateFilter("")
                  }
                  title="Clear date"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            <button
              className="secondary-button"
              onClick={loadDashboard}
            >
              <RefreshCw size={15} />
              Refresh
            </button>
          </div>

          <div className="event-results-bar">
            <span>
              Showing{" "}
              <strong>
                {filteredEvents.length}
              </strong>{" "}
              event
              {filteredEvents.length !== 1
                ? "s"
                : ""}
              {dateFilter
                ? ` for ${dateFilter}`
                : ""}
            </span>

            {(search ||
              filter !== "ALL" ||
              dateFilter) && (
              <button
                className="clear-all"
                onClick={() => {
                  setSearch("");
                  setFilter("ALL");
                  setDateFilter("");
                }}
              >
                Clear filters
              </button>
            )}
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>TIME</th>
                  <th>EVENT</th>
                  <th>OBJECT</th>
                  <th>TRACK ID</th>
                  <th>ZONE</th>
                  <th>DURATION</th>
                  <th>CONFIDENCE</th>
                </tr>
              </thead>

              <tbody>
                {filteredEvents.map(
                  (event, index) => (
                    <tr
                      key={`${event.timestamp}-${event.track_id}-${index}`}
                      className="clickable-event-row"
                      onClick={() =>
                        setSelectedEvent(
                          event
                        )
                      }
                    >
                      <td>
                        <span className="event-time">
                          {formatTimestamp(
                            event.timestamp
                          )}
                        </span>
                      </td>

                      <td>
                        <EventBadge
                          type={
                            event.event_type
                          }
                        />
                      </td>

                      <td>
                        <div className="object-cell">
                          <div className="object-icon">
                            {event.object_type?.toLowerCase() ===
                            "person" ? (
                              <Users
                                size={15}
                              />
                            ) : (
                              <Car
                                size={15}
                              />
                            )}
                          </div>

                          <span>
                            {event.object_type ||
                              "-"}
                          </span>
                        </div>
                      </td>

                      <td>
                        <span className="track-id">
                          #
                          {event.track_id ||
                            "-"}
                        </span>
                      </td>

                      <td>
                        {event.zone_name ||
                          "-"}
                      </td>

                      <td>
                        {formatDuration(
                          event.duration_sec
                        )}
                      </td>

                      <td>
                        {formatConfidence(
                          event.confidence
                        )}
                      </td>
                    </tr>
                  )
                )}

                {filteredEvents.length ===
                  0 && (
                  <tr>
                    <td colSpan="7">
                      <EmptyState
                        title="No matching events"
                        description="Try changing your search, event type or date filter."
                      />
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </>
    );
  }

  // =======================================================
  // ANALYTICS
  // =======================================================

  function renderAnalytics() {
    return (
      <>
        <PageHeader
          eyebrow="ANALYTICS"
          title="Security Analytics"
          description="Understand event patterns, object activity and restricted-zone behavior."
        />

        <div className="analytics-stats">
          <StatCard
            title="Total Activity"
            value={events.length}
            icon={Activity}
            description="Events in current dataset"
          />

          <StatCard
            title="Critical Activity"
            value={criticalAlerts.length}
            icon={ShieldAlert}
            description="Repeated violations"
            tone="danger"
          />

          <StatCard
            title="Warning Activity"
            value={warningAlerts.length}
            icon={AlertTriangle}
            description="Loitering events"
            tone="warning"
          />
        </div>

        <section className="analytics-page-grid">
          <div className="panel analytics-chart-panel">
            <SectionHeader
              eyebrow="EVENT DISTRIBUTION"
              title="Event Types"
              description="Breakdown of recorded event categories."
            />

            <div className="chart-container tall">
              <ResponsiveContainer
                width="100%"
                height={340}
              >
                <BarChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    opacity={0.12}
                  />

                  <XAxis dataKey="name" />

                  <YAxis
                    allowDecimals={false}
                  />

                  <Tooltip />

                  <Bar
                    dataKey="value"
                    radius={[
                      6,
                      6,
                      0,
                      0,
                    ]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel analytics-chart-panel">
            <SectionHeader
              eyebrow="OBJECT ACTIVITY"
              title="Detected Objects"
              description="Objects associated with recorded events."
            />

            <div className="chart-container tall">
              {objectData.length > 0 ? (
                <ResponsiveContainer
                  width="100%"
                  height={340}
                >
                  <PieChart>
                    <Pie
                      data={objectData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={115}
                      label
                    >
                      {objectData.map(
                        (_, index) => (
                          <Cell
                            key={`cell-${index}`}
                          />
                        )
                      )}
                    </Pie>

                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState
                  title="No object data"
                  description="Object activity will appear after events are recorded."
                />
              )}
            </div>
          </div>
        </section>

        <div className="panel zone-panel">
          <SectionHeader
            eyebrow="ZONE ACTIVITY"
            title="Most Active Zones"
            description="Zones with the highest number of recorded events."
          />

          <div className="zone-list">
            {zoneData.map((zone) => {
              const maxZoneValue =
                Math.max(
                  ...zoneData.map(
                    (item) =>
                      item.value
                  )
                );

              return (
                <div
                  className="zone-row"
                  key={zone.name}
                >
                  <div className="zone-name">
                    <Shield size={15} />
                    {zone.name}
                  </div>

                  <div className="zone-bar-wrapper">
                    <div
                      className="zone-bar"
                      style={{
                        width: `${Math.min(
                          100,
                          (zone.value /
                            maxZoneValue) *
                            100
                        )}%`,
                      }}
                    />
                  </div>

                  <strong>
                    {zone.value}
                  </strong>
                </div>
              );
            })}

            {zoneData.length === 0 && (
              <EmptyState
                title="No zone activity"
                description="Zone statistics will appear once events are recorded."
              />
            )}
          </div>
        </div>
      </>
    );
  }

  // =======================================================
  // SETTINGS
  // =======================================================

  function renderSettings() {
    return (
      <>
        <PageHeader
          eyebrow="SYSTEM SETTINGS"
          title="Settings"
          description="Manage dashboard preferences and monitoring behavior."
        />

        <div className="settings-layout">
          <div className="panel settings-panel">
            <SectionHeader
              eyebrow="APPEARANCE"
              title="Dashboard Appearance"
              description="Customize how the RAKSHAK AI dashboard looks."
            />

            <div className="setting-row">
              <div className="setting-info">
                <div className="setting-icon">
                  {theme === "dark" ? (
                    <Moon size={17} />
                  ) : (
                    <Sun size={17} />
                  )}
                </div>

                <div>
                  <strong>Theme</strong>

                  <span>
                    Choose between dark and
                    light appearance.
                  </span>
                </div>
              </div>

              <div className="theme-switch">
                <button
                  className={
                    theme === "dark"
                      ? "theme-option active"
                      : "theme-option"
                  }
                  onClick={() =>
                    setTheme("dark")
                  }
                >
                  <Moon size={14} />
                  Dark
                </button>

                <button
                  className={
                    theme === "light"
                      ? "theme-option active"
                      : "theme-option"
                  }
                  onClick={() =>
                    setTheme("light")
                  }
                >
                  <Sun size={14} />
                  Light
                </button>
              </div>
            </div>
          </div>

          <div className="panel settings-panel">
            <SectionHeader
              eyebrow="MONITORING"
              title="Monitoring Preferences"
              description="Control how frequently the dashboard checks the API."
            />

            <div className="setting-row">
              <div className="setting-info">
                <div className="setting-icon">
                  <RefreshCw size={17} />
                </div>

                <div>
                  <strong>
                    Automatic Refresh
                  </strong>

                  <span>
                    Refresh dashboard data every
                    5 seconds.
                  </span>
                </div>
              </div>

              <button
                className={
                  autoRefresh
                    ? "toggle active"
                    : "toggle"
                }
                onClick={() =>
                  setAutoRefresh(
                    !autoRefresh
                  )
                }
                aria-label="Toggle automatic refresh"
              >
                <span />
              </button>
            </div>
          </div>

          <div className="panel settings-panel">
            <SectionHeader
              eyebrow="SYSTEM INFORMATION"
              title="RAKSHAK AI Status"
              description="Current connection and storage information."
            />

            <div className="system-info-grid">
              <InfoItem
                label="API Status"
                value={
                  health?.status === "ok"
                    ? "Online"
                    : "Unavailable"
                }
              />

              <InfoItem
                label="Events Storage"
                value={
                  health?.events_file_exists
                    ? "Available"
                    : "Unavailable"
                }
              />

              <InfoItem
                label="Camera Stream"
                value={
                  health?.stream_frame_exists
                    ? "Available"
                    : "Waiting"
                }
              />

              <InfoItem
                label="Events Loaded"
                value={events.length}
              />
            </div>
          </div>
        </div>
      </>
    );
  }

  // =======================================================
  // PAGE HEADER
  // =======================================================

  function PageHeader({
    eyebrow,
    title,
    description,
  }) {
    return (
      <header className="page-header">
        <div className="page-heading">
          <div className="page-eyebrow">
            {eyebrow}
          </div>

          <h1>{title}</h1>

          <p>{description}</p>
        </div>

        <div className="header-actions">
          <div className="header-status">
            <span
              className={`live-dot ${
                health?.status !== "ok"
                  ? "offline"
                  : ""
              }`}
            />

            <div>
              <span>System</span>

              <strong>
                {health?.status ===
                "ok"
                  ? "Online"
                  : "Checking"}
              </strong>
            </div>
          </div>

          <button
            className="refresh-button"
            onClick={loadDashboard}
            title="Refresh dashboard"
          >
            <RefreshCw size={15} />
            Refresh
          </button>

          <button
            className="theme-button"
            onClick={() =>
              setTheme(
                theme === "dark"
                  ? "light"
                  : "dark"
              )
            }
            title="Toggle theme"
          >
            {theme === "dark" ? (
              <Sun size={17} />
            ) : (
              <Moon size={17} />
            )}
          </button>
        </div>
      </header>
    );
  }

  // =======================================================
  // PAGE ROUTING
  // =======================================================

  function renderPage() {
    switch (activePage) {
      case "monitoring":
        return renderMonitoring();

      case "alerts":
        return renderAlerts();

      case "events":
        return renderEvents();

      case "analytics":
        return renderAnalytics();

      case "settings":
        return renderSettings();

      case "dashboard":
      default:
        return renderDashboard();
    }
  }

  // =======================================================
  // MAIN UI
  // =======================================================

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() =>
            setSidebarOpen(false)
          }
        />
      )}

      <aside
        className={`sidebar ${
          sidebarOpen
            ? "mobile-open"
            : ""
        }`}
      >
        <div className="brand">
          <div className="brand-mark">
            <ShieldAlert size={22} />
          </div>

          <div className="brand-copy">
            <div className="brand-name">
              RAKSHAK AI
            </div>

            <div className="brand-subtitle">
              Safety Monitoring
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-label">
            OVERVIEW
          </div>

          {navItems.slice(0, 1).map(
            (item) => (
              <NavItem
                key={item.id}
                item={item}
                activePage={activePage}
                navigateTo={navigateTo}
              />
            )
          )}

          <div className="nav-section-label">
            MONITORING
          </div>

          {navItems.slice(1, 4).map(
            (item) => (
              <NavItem
                key={item.id}
                item={item}
                activePage={activePage}
                navigateTo={navigateTo}
              />
            )
          )}

          <div className="nav-section-label">
            INSIGHTS
          </div>

          {navItems.slice(4).map(
            (item) => (
              <NavItem
                key={item.id}
                item={item}
                activePage={activePage}
                navigateTo={navigateTo}
              />
            )
          )}
        </nav>

        <div className="sidebar-bottom">
          <div className="system-card">
            <div className="system-card-top">
              <div className="system-icon">
                <Shield size={15} />
              </div>

              <span
                className={
                  health?.status ===
                  "ok"
                    ? "online-pill"
                    : "checking-pill"
                }
              >
                {health?.status ===
                "ok"
                  ? "ONLINE"
                  : "CHECKING"}
              </span>
            </div>

            <div className="system-title">
              Protection Active
            </div>

            <div className="system-description">
              Restricted-zone monitoring
              is running.
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <div className="mobile-topbar">
          <button
            className="menu-button"
            onClick={() =>
              setSidebarOpen(
                !sidebarOpen
              )
            }
          >
            <Menu size={20} />
          </button>

          <div className="mobile-brand">
            RAKSHAK AI
          </div>

          <button
            className="theme-button"
            onClick={() =>
              setTheme(
                theme === "dark"
                  ? "light"
                  : "dark"
              )
            }
          >
            {theme === "dark" ? (
              <Sun size={17} />
            ) : (
              <Moon size={17} />
            )}
          </button>
        </div>

        {error && (
          <div className="error-banner">
            <XCircle size={17} />

            <div>
              <strong>
                Connection issue
              </strong>

              <span>{error}</span>
            </div>
          </div>
        )}

        {loading && !health ? (
          <LoadingScreen />
        ) : (
          renderPage()
        )}

        <footer className="dashboard-footer">
          <span>
            RAKSHAK AI · Restricted Zone &
            Safety Monitoring
          </span>

          <span>
            {loading
              ? "Updating..."
              : lastUpdated
                ? `Last updated ${lastUpdated.toLocaleTimeString()}`
                : "Waiting for data"}
          </span>
        </footer>
      </main>

      {selectedEvent && (
        <EventModal
          event={selectedEvent}
          onClose={() =>
            setSelectedEvent(null)
          }
        />
      )}
    </div>
  );
}

// =========================================================
// NAV ITEM
// =========================================================

function NavItem({
  item,
  activePage,
  navigateTo,
}) {
  const Icon = item.icon;

  return (
    <button
      className={`nav-item ${
        activePage === item.id
          ? "active"
          : ""
      }`}
      onClick={() =>
        navigateTo(item.id)
      }
    >
      <Icon size={17} />

      <span>{item.label}</span>

      {item.badge && (
        <span className="nav-badge">
          {item.badge}
        </span>
      )}
    </button>
  );
}

// =========================================================
// HEALTH ROW
// =========================================================

function HealthRow({
  label,
  value,
  online,
}) {
  return (
    <div className="health-row">
      <div className="health-label">
        <span
          className={
            online
              ? "health-dot online"
              : "health-dot"
          }
        />

        {label}
      </div>

      <strong>{value}</strong>
    </div>
  );
}

// =========================================================
// INFO ITEM
// =========================================================

function InfoItem({
  label,
  value,
}) {
  return (
    <div className="info-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

// =========================================================
// EVENT MODAL
// =========================================================

function EventModal({
  event,
  onClose,
}) {
  useEffect(() => {
    function handleEscape(e) {
      if (e.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener(
      "keydown",
      handleEscape
    );

    return () =>
      document.removeEventListener(
        "keydown",
        handleEscape
      );
  }, [onClose]);

  return (
    <div
      className="event-modal-overlay"
      onClick={onClose}
    >
      <div
        className="event-modal"
        onClick={(e) =>
          e.stopPropagation()
        }
      >
        <div className="event-modal-header">
          <div>
            <div className="section-kicker">
              EVENT DETAILS
            </div>

            <h2>
              {formatEventName(
                event.event_type
              )}
            </h2>

            <span className="modal-timestamp">
              {formatTimestamp(
                event.timestamp
              )}
            </span>
          </div>

          <button
            className="modal-close"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>

        <div className="event-summary">
          <EventBadge
            type={event.event_type}
          />

          <p>
            {getEventSummary(event)}
          </p>
        </div>

        <div className="event-details-grid">
          <DetailItem
            label="DATE & TIME"
            value={formatTimestamp(
              event.timestamp
            )}
          />

          <DetailItem
            label="OBJECT"
            value={
              event.object_type ||
              "-"
            }
          />

          <DetailItem
            label="TRACK ID"
            value={`#${event.track_id || "-"}`}
          />

          <DetailItem
            label="ZONE"
            value={
              event.zone_name ||
              "-"
            }
          />

          <DetailItem
            label="DURATION"
            value={formatDuration(
              event.duration_sec
            )}
          />

          <DetailItem
            label="CONFIDENCE"
            value={formatConfidence(
              event.confidence
            )}
          />
        </div>
      </div>
    </div>
  );
}

// =========================================================
// DETAIL ITEM
// =========================================================

function DetailItem({
  label,
  value,
}) {
  return (
    <div className="detail-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

// =========================================================
// LOADING
// =========================================================

function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-spinner">
        <RefreshCw size={20} />
      </div>

      <h3>
        Connecting to RAKSHAK AI
      </h3>

      <p>
        Loading monitoring data...
      </p>
    </div>
  );
}

export default App;