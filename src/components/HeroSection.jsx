import React from 'react';
import { TypeAnimation } from 'react-type-animation';
import { motion } from 'framer-motion';
import styles from './HeroSection.module.css';

const HeroSection = ({ profile }) => {
  return (
    <section className={styles.hero}>
      <div className={styles.greetings}>
        {profile.greetings.map((greet, i) => (
          <motion.span
            key={greet}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.3 }}
            className={styles.greeting}
          >
            {greet}
          </motion.span>
        ))}
      </div>
      <motion.h1
        className={styles.name}
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
      >
        I'm {profile.name}
        <motion.span
          className={styles.sideComment}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 0.7, x: 0 }}
          transition={{ delay: 2 }}
        >
          ({profile.sideComment})
        </motion.span>
      </motion.h1>
      <div className={styles.roles}>
        <TypeAnimation
          sequence={profile.roles.flatMap(role => [role, 2000])}
          wrapper="span"
          speed={40}
          repeat={Infinity}
          className={styles.roleText}
        />
      </div>
      <motion.div
        className={styles.scrollIndicator}
        animate={{ y: [0, 15, 0] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
      >
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <path d="M16 8V24M16 24L8 16M16 24L24 16" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </motion.div>
    </section>
  );
};

export default HeroSection; 