import React, {useState} from 'react'

export default function App(){
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [selected, setSelected] = useState(null)
  const [suggestion, setSuggestion] = useState(null)

  async function doSearch(){
    const resp = await fetch('http://localhost:8000/search', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: query, top_k: 10})
    })
    const data = await resp.json()
    setResults(data.results || [])
  }

  async function loadIncident(id){
    const resp = await fetch(`http://localhost:8000/incidents/${id}`)
    const data = await resp.json()
    setSelected(data)
    setSuggestion(null)
  }

  async function getSuggestion(id){
    const resp = await fetch(`http://localhost:8000/incidents/${id}/suggest`)
    const data = await resp.json()
    setSuggestion(data.suggestion)
  }

  return (
    <div style={{padding:20,fontFamily:'sans-serif'}}>
      <h2>Hindsight — Incident Search</h2>
      <div>
        <input style={{width:400}} value={query} onChange={e=>setQuery(e.target.value)} placeholder="Describe the incident" />
        <button onClick={doSearch}>Search</button>
      </div>
      <div style={{display:'flex',gap:20, marginTop:20}}>
        <div style={{width:360}}>
          <h3>Results</h3>
          <ul>
            {results.map((r,i)=> (
              <li key={i} style={{marginBottom:6}}>
                <button onClick={()=>loadIncident(r[0])} style={{marginRight:8}}>Open</button>
                {r[0]} — score: {r[1].toFixed(3)}
              </li>
            ))}
          </ul>
        </div>
        <div style={{flex:1}}>
          <h3>Incident</h3>
          {selected ? (
            <div>
              <h4>{selected.title}</h4>
              <p>{selected.description}</p>
              <p><b>Root cause:</b> {selected.root_cause || '—'}</p>
              <p><b>Resolution:</b> {selected.resolution || '—'}</p>
              <div style={{marginTop:10}}>
                <button onClick={()=>getSuggestion(selected.id)}>Suggest runbook / resolution</button>
              </div>
              {suggestion && (
                <div style={{marginTop:12,borderTop:'1px solid #ddd',paddingTop:12}}>
                  <h4>Suggestion</h4>
                  <pre style={{whiteSpace:'pre-wrap'}}>{suggestion.summary}</pre>
                  {suggestion.runbook && (<>
                    <h5>Runbook</h5>
                    <pre style={{whiteSpace:'pre-wrap'}}>{suggestion.runbook}</pre>
                  </>)}
                </div>
              )}
            </div>
          ) : (
            <div>Select an incident from results to view details.</div>
          )}
        </div>
      </div>
    </div>
  )
}
