const appStyles = {
  minHeight: '100vh',
  margin: 0,
  padding: '1.25rem',
  boxSizing: 'border-box',
  fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif',
  backgroundColor: '#f8fafc',
  color: '#0f172a'
};

const shellStyles = {
  display: 'flex',
  gap: '1rem',
  height: 'calc(100vh - 2.5rem)'
};

const panelStyles = {
  backgroundColor: '#ffffff',
  border: '1px solid #e2e8f0',
  borderRadius: '0.75rem',
  padding: '1rem',
  boxSizing: 'border-box',
  overflow: 'auto'
};

export default function App() {
  return (
    <main style={appStyles}>
      <section style={shellStyles}>
        <aside style={{ ...panelStyles, flex: '0 0 40%' }}>
          <h1 style={{ marginTop: 0 }}>Prayog-Shala</h1>
          <p style={{ marginBottom: 0 }}>Experiment input and history panel (40%).</p>
        </aside>
        <section style={{ ...panelStyles, flex: '1 1 60%' }}>
          <h2 style={{ marginTop: 0 }}>Visualization Workspace</h2>
          <p style={{ marginBottom: 0 }}>Simulation visualization, equation, and explanation panel (60%).</p>
        </section>
      </section>
    </main>
  );
}
