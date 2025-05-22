import React from 'react';
import { motion } from 'framer-motion';
import styles from './SkillsSection.module.css';

const cardVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.2 } })
};

const SkillsSection = ({ profile }) => {
  return (
    <section className={styles.skillsSection}>
      <h2 className={styles.heading}>Skills</h2>
      <div className={styles.skillsGrid}>
        {profile.skills.map((skill, i) => (
          <motion.div
            key={skill.name}
            className={styles.skillCard}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.6 }}
            custom={i}
            variants={cardVariants}
          >
            <span className={styles.skillName}>{skill.name}</span>
            <span className={styles.skillLevel}>{skill.level}</span>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default SkillsSection; 