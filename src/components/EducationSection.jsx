import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './EducationSection.module.css';

const EducationSection = ({ profile }) => {
  const [openIndex, setOpenIndex] = useState(null);

  return (
    <section className={styles.educationSection}>
      <h2 className={styles.heading}>Education & Certifications</h2>
      <div className={styles.timeline}>
        {profile.education.map((edu, i) => (
          <motion.div
            key={edu.title}
            className={styles.eduCard}
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.7 }}
            transition={{ delay: i * 0.2 }}
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
          >
            <div className={styles.eduHeader}>
              <span className={styles.eduTitle}>{edu.title}</span>
              <span className={styles.eduInstitution}>{edu.institution}</span>
              <span className={styles.eduYear}>{edu.year}</span>
            </div>
            <AnimatePresence>
              {openIndex === i && (
                <motion.div
                  className={styles.eduDetails}
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <p>{edu.details}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default EducationSection; 