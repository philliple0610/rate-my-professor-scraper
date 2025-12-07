// import { professors } from "../mockData";
import type { Professor } from "../types/Professor";
import { useEffect, useState } from "react";
import SearchBar from "./SearchBar/SearchBar";
import ProfessorItem from "./ProfessorItem/ProfessorItem";
import ProfessorModal from "./ProfessorModal/ProfessorModal";

function ProfessorList() {
  const [professors, setProfessors] = useState<Professor[]>([]);
  const [filtered, setFiltered] = useState<Professor[]>(professors);
  const [selected, setSelected] = useState<Professor | null>(null);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  // Fetch professors from Flask backend
  const fetchProfessors = () => {
    setLoading(true);
    fetch("http://127.0.0.1:5001/api/professors")
      .then((res) => res.json())
      .then((data) => {
        setProfessors(data);
        setFiltered(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching professors:", err);
        setMessage({ type: "error", text: "Failed to fetch professors" });
        setLoading(false);
      });
  };

  // Initial load
  useEffect(() => {
    fetchProfessors();
  }, []);

  // Trigger scrape from RateMyProf
  const handleRefreshFromRateMyProf = async () => {
    setScraping(true);
    setMessage(null);
    try {
      const response = await fetch(
        "http://127.0.0.1:5001/api/scrape-professors",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            school_id: "1581", // Foothill College
            testing: false,
          }),
        }
      );

      const data = await response.json();

      if (data.success) {
        setMessage({
          type: "success",
          text: `✓ Successfully scraped ${data.count} professors!`,
        });
        // Refresh the professor list
        setTimeout(() => fetchProfessors(), 1000);
      } else {
        setMessage({
          type: "error",
          text: `✗ Scrape failed: ${data.message}`,
        });
      }
    } catch (err) {
      console.error("Scrape error:", err);
      setMessage({
        type: "error",
        text: "Error triggering RateMyProf scrape",
      });
    } finally {
      setScraping(false);
    }
  };

  const handleSearch = (query: string) => {
    const result = professors.filter(
      (professor) =>
        professor.class.toLowerCase().includes(query.toLowerCase()) ||
        professor.name.toLowerCase().includes(query.toLowerCase()) ||
        professor.department.toLowerCase().includes(query.toLowerCase())
    );
    setFiltered(result);
  };

  return (
    <div>
      <SearchBar onSearch={handleSearch} />

      {/* Refresh button */}
      <div style={{ marginBottom: "1rem" }}>
        <button
          onClick={handleRefreshFromRateMyProf}
          disabled={scraping}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#0066cc",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: scraping ? "not-allowed" : "pointer",
            opacity: scraping ? 0.6 : 1,
          }}
        >
          {scraping ? "Scraping..." : "Refresh from RateMyProf"}
        </button>

        {/* Message display */}
        {message && (
          <div
            style={{
              marginTop: "0.5rem",
              padding: "0.5rem",
              backgroundColor:
                message.type === "success" ? "#d4edda" : "#f8d7da",
              color: message.type === "success" ? "#155724" : "#721c24",
              borderRadius: "4px",
              fontSize: "0.9rem",
            }}
          >
            {message.text}
          </div>
        )}
      </div>

      <ul className="professor-list">
        {loading && <li>Loading professors...</li>}
        {filtered.length === 0 && !loading && <li>No professors found.</li>}
        {filtered.map((p) => (
          <ProfessorItem
            key={p.id}
            professor={p}
            onClick={() => setSelected(p)}
          />
        ))}
      </ul>
      {selected && (
        <ProfessorModal
          professor={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}

export default ProfessorList;
