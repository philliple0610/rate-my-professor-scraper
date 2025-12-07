import { useState } from "react";
import styles from "./SearchBar.module.css";

interface SearchBarProps {
  onSearch: (query: string) => void;
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim() !== "") {
      onSearch(searchTerm);
    }
  };

  return (
    <form onSubmit={handleSubmit} role="search" className={styles.form}>
      <label htmlFor="search" className={styles.label}>
        Search
      </label>
      <input
        id="search"
        type="search"
        placeholder="Search..."
        value={searchTerm}
        onChange={handleInputChange}
        className={styles.input}
        autoFocus
        required
        autoComplete="off"
      />
      <button type="submit" className={styles.button}>
        Go
      </button>
    </form>
  );
}
