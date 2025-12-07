import { motion, AnimatePresence } from "framer-motion";
import styles from "./ProfessorModal.module.css";
import type { Professor } from "../../types/Professor";

interface ProfessorModalProps {
  professor: Professor;
  onClose: () => void;
}

export default function ProfessorModal({
  professor,
  onClose,
}: ProfessorModalProps) {
  return (
    <AnimatePresence>
      <div className={styles.overlay} onClick={onClose}>
        <motion.div
          className={styles.modal}
          onClick={(e: React.MouseEvent) => e.stopPropagation()}
          initial={{ opacity: 0, scale: 0.8, y: 50 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 50 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        >
          <button className={styles.closeBtn} onClick={onClose}>
            ✕
          </button>
          <h2>{professor.name}</h2>
          <p>
            <strong>Class:</strong> {professor.class}
          </p>
          <p>
            <strong>Department:</strong> {professor.department}
          </p>
          <p>
            <strong>Average Grade:</strong> {professor.avgGrade}
          </p>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
