import React from 'react';
import { motion } from 'framer-motion';
import styles from './ProjectsSection.module.css';

const ProjectsSection = ({ profile }) => {
  return (
    <section className={styles.projectsSection}>
      <h2 className={styles.heading}>Projects</h2>
      <div className={styles.projectsGrid}>
        {profile.projects.map((proj, i) => (
          <motion.div
            key={proj.title}
            className={styles.projectCard}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.7 }}
            transition={{ delay: i * 0.2 }}
          >
            <div className={styles.projectHeader}>
              <span className={styles.projectTitle}>{proj.title}</span>
              <span className={styles.projectPeriod}>{proj.period}</span>
            </div>
            <ul className={styles.projectDetails}>
              {proj.details.map((d, j) => (
                <li key={j}>{d}</li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default ProjectsSection; 