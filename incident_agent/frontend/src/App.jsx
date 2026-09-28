import React, {useState} from 'react'

export default function App(){
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  async function doSearch(){
    const resp = await fetch('http://localhost:8000/search', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: query, top_k: 5})
    })
    const data = await resp.json()
    setResults(data.results || [])
  }

  return (
    <div style={{padding:20,fontFamily:'sans-serif'}}>
      <h2>Hindsight — Incident Search</h2>
      <div>
        <input style={{width:400}} value={query} onChange={e=>setQuery(e.target.value)} placeholder="Describe the incident" />
        <button onClick={doSearch}>Search</button>
      </div>
      <div style={{marginTop:20}}>
        <h3>Results</h3>
        <ul>
          {results.map((r,i)=> (
            <li key={i}>{r[0]} — score: {r[1].toFixed(3)}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
