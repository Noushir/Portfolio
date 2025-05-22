import React from 'react';
import { motion } from 'framer-motion';
import styles from './ResearchSection.module.css';

const ResearchSection = ({ profile }) => {
  return (
    <section className={styles.researchSection}>
      <h2 className={styles.heading}>Research & Publications</h2>
      <div className={styles.researchGrid}>
        {profile.research.map((item, i) => (
          <motion.div
            key={item.title}
            className={styles.researchCard}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.7 }}
            transition={{ delay: i * 0.2 }}
          >
            <div className={styles.researchHeader}>
              <span className={styles.researchTitle}>{item.title}</span>
              <span className={styles.researchDate}>{item.date}</span>
            </div>
            <ul className={styles.researchDetails}>
              {item.details.map((d, j) => (
                <li key={j}>{d}</li>
              ))}
            </ul>
            {item.doi && (
              <a
                href={item.doi.startsWith('http') ? item.doi : `https://doi.org/${item.doi}`}
                className={styles.doiLink}
                target="_blank"
                rel="noopener noreferrer"
              >
                {item.doi}
              </a>
            )}
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default ResearchSection; 