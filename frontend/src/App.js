
import { useEffect, useState } from "react";

function App() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/jobs")
      .then(res => res.json())
      .then(setJobs);
  }, []);

  const loadJobDetail = async (job) => {
    setLoading(true);

    const res = await fetch(`http://localhost:8000/jobs/${job.id}`);
    const data = await res.json();

    setSelectedJob(data);

    const matchRes = await fetch(
      `http://localhost:8000/jobs/${job.id}/matches?top_k=5`
    );

    const matchData = await matchRes.json();
    setMatches(matchData);

    setLoading(false);
  };

  return (
    <div style={{padding:20}}>
      <h1>Job Matching App</h1>

      <h2>Jobs List</h2>

      {jobs.map(job => (
        <div key={job.id} style={{border:"1px solid #ddd", padding:10, margin:10}}>
          <h3 onClick={() => loadJobDetail(job)} style={{cursor:"pointer"}}>
            {job.title}
          </h3>
        </div>
      ))}

      {loading && <p>Loading...</p>}

      {selectedJob && (
        <div style={{marginTop:20}}>
          <h2>Job Details</h2>
          <h3>{selectedJob.title}</h3>
          <p>{selectedJob.description}</p>

          <h2>Top Matches</h2>
          <table border="1" cellPadding="8">
            <thead>
              <tr>
                <th>Name</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {matches.map(m => (
                <tr key={m.id}>
                  <td>{m.name}</td>
                  <td>{m.score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
