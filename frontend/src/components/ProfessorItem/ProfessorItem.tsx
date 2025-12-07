import type { Professor } from "../../types/Professor";
import styles from "./ProfessorItem.module.css";

interface ProfessorItemProps {
  professor: Professor;
  onClick: () => void;
}

export default function ProfessorItem({
  professor,
  onClick,
}: ProfessorItemProps) {
  return (
    <li className={styles.item} onClick={onClick}>
      <div className={styles.header}>
        <h3 className={styles.name}>{professor.name}</h3>
        <span className={styles.className}>{professor.class}</span>
      </div>
      <p className={styles.department}>{professor.department}</p>
      
      {/* Display RateMyProf rating if available */}
      {professor.overallRating !== undefined && professor.overallRating > 0 && (
        <p className={styles.rating}>
          ⭐ RateMyProf: {professor.overallRating.toFixed(1)}/5.0 
          {professor.numRatings && ` (${professor.numRatings} ratings)`}
        </p>
      )}
    </li>
  );
}
