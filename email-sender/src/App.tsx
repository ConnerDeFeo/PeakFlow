import { useState } from 'react'

function App() {
  const [status, setStatus] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const sendEmail = async () => {
    setLoading(true)
    setStatus(null)
    try {
      const res = await fetch('https://0izcoe58s6.execute-api.us-east-2.amazonaws.com/auto-email-send', {
        method: 'POST',
      })
      setStatus(res.ok ? 'Email sent successfully!' : `Error: ${res.status} ${res.statusText}`)
    } catch (err) {
      setStatus(`Failed to send: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '100px', gap: '16px' }}>
      <button onClick={sendEmail} disabled={loading} style={{ padding: '12px 24px', fontSize: '16px', cursor: loading ? 'not-allowed' : 'pointer' }}>
        {loading ? 'Sending...' : 'Send Email'}
      </button>
      {status && <p>{status}</p>}
    </div>
  )
}

export default App
