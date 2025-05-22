import React from 'react';
import { motion } from 'framer-motion';
import styles from './NarrativeScroll.module.css';

const sections = [
  {
    id: 1,
    text: 'No? You need to know about me?'
  },
  {
    id: 2,
    text: 'What am I good at?'
  },
  {
    id: 3,
    text: 'How did I learn all this?'
  }
];

const sectionVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.5 } })
};

const NarrativeScroll = () => {
  return (
    <div className={styles.narrativeScroll}>
      {sections.map((section, i) => (
        <motion.section
          key={section.id}
          className={styles.storySection}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.7 }}
          custom={i}
          variants={sectionVariants}
        >
          <h2>{section.text}</h2>
        </motion.section>
      ))}
    </div>
  );
};

export default NarrativeScroll; 