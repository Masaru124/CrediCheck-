import { useState } from 'react'
import './App.css'

function App() {
  const [text, setText] = useState('')
  const [response, setResponse] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    const res = await fetch('http://localhost:8000/api/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
    const data = await res.json()
    setResponse(data)
  }

  return (
    <div className="App">
      <h1>CrediCheck AI</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          rows="6"
          placeholder="Paste a social media post or article snippet here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button type="submit">Verify</button>
      </form>
      {response && (
        <div>
          <h2 className={`badge ${response.badge.toLowerCase()}`}>Credibility Score: {response.credibility_score} ({response.badge})</h2>
          <p>{response.explanation}</p>
          <h3>Claims:</h3>
          {response.claims.map((claim, index) => (
            <div key={index} className="claim">
              <p><strong>Claim:</strong> {claim.claim}</p>
              <p className={`status ${claim.status.toLowerCase()}`}><strong>Status:</strong> {claim.status}</p>
              <p><strong>Explanation:</strong> {claim.explanation}</p>
              <h4>Sources:</h4>
              <ul>
                {claim.sources.map((source, i) => (
                  <li key={i}><a href={source.link} target="_blank" rel="noopener noreferrer">{source.title}</a>: {source.summary}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App
