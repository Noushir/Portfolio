import React from 'react';
import { motion } from 'framer-motion';
import styles from './AchievementsSection.module.css';

const AchievementsSection = ({ profile }) => {
  return (
    <section className={styles.achievementsSection}>
      <h2 className={styles.heading}>Achievements</h2>
      <ul className={styles.achievementsList}>
        {profile.achievements.map((ach, i) => (
          <motion.li
            key={i}
            className={styles.achievement}
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.7 }}
            transition={{ delay: i * 0.15 }}
          >
            {ach}
          </motion.li>
        ))}
      </ul>
    </section>
  );
};

export default AchievementsSection; 