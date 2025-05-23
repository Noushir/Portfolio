import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './EducationSection.module.css';

const EducationSection = ({ profile }) => {
  const [openIndex, setOpenIndex] = useState(null);
  
  // Additional learning resources with icons
  const selfLearningResources = [
    { name: 'YouTube', icon: 'youtube' },
    { name: 'ChatGPT', icon: 'chatgpt' },
    { name: 'Coursera', icon: 'coursera' },
    { name: 'Udemy', icon: 'udemy' },
    { name: 'Stack Overflow', icon: 'stackoverflow' }
  ];

  return (
    <section className={styles.educationSection} id="education">
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

      <motion.div
        className={styles.selfLearningSection}
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <h3>Self-Learning Resources</h3>
        <div className={styles.resourcesGrid}>
          {selfLearningResources.map((resource, index) => (
            <motion.div
              key={resource.name}
              className={styles.resourceCard}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <div className={styles.resourceIcon}>
                {resource.icon === 'youtube' && (
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                  </svg>
                )}
                {resource.icon === 'chatgpt' && (
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.5093-2.6067-1.4998z" />
                  </svg>
                )}
                {resource.icon === 'coursera' && (
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M11.7 16.7c-3.6 0-5.8-2.8-5.8-6.4s2.2-6.4 5.8-6.4c1.8 0 3.3.7 4.3 1.9l1.9-2.2C16.3 1.8 14.1.9 11.7.9 6.7.9 3 4.5 3 10.3s3.7 9.4 8.7 9.4c2.4 0 4.6-.9 6.1-2.7l-1.9-2.2c-1 1.2-2.5 1.9-4.2 1.9zM21 5.3h-4.2v2h4.2v4.1h-4.2v2h4.2v4.3h-4.2v2H21c1.4 0 2.5-1.1 2.5-2.5v-9.5c0-1.3-1.1-2.4-2.5-2.4z" />
                  </svg>
                )}
                {resource.icon === 'udemy' && (
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0L5.81 3.573v3.574l6.189-3.574 6.191 3.574V3.573zM5.81 10.148v8.144c0 1.85.589 3.243 1.741 4.234S10.178 24 11.973 24s3.269-.482 4.448-1.474c1.179-.991 1.768-2.439 1.768-4.314v-8.064h-3.242v7.85c0 2.036-1.509 3.055-2.948 3.055-1.428 0-2.947-.991-2.947-3.027v-7.878z" />
                  </svg>
                )}
                {resource.icon === 'stackoverflow' && (
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.986 21.865v-6.404h2.134V24H1.844v-8.539h2.13v6.404h15.012zM6.111 19.731H16.85v-2.137H6.111v2.137zm.259-4.852l10.48 2.189.451-2.07-10.478-2.187-.453 2.068zm1.359-5.056l9.705 4.53.903-1.95-9.706-4.53-.902 1.95zm2.715-4.785l8.217 6.855 1.359-1.62-8.216-6.853-1.36 1.618zM15.751 0l-1.746 1.294 6.405 8.604 1.746-1.294L15.749 0z"/>
                  </svg>
                )}
              </div>
              <div className={styles.resourceName}>{resource.name}</div>
            </motion.div>
          ))}
        </div>
        <p className={styles.selfLearningText}>
          Beyond formal education, I continuously expand my knowledge through these platforms.
        </p>
      </motion.div>
    </section>
  );
};

export default EducationSection; 