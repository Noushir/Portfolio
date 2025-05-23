import React, { useRef } from 'react';
import HeroSection from './components/HeroSection';
import SkillsSection from './components/SkillsSection';
import EducationSection from './components/EducationSection';
import AchievementsSection from './components/AchievementsSection';
import ProjectsSection from './components/ProjectsSection';
import ResearchSection from './components/ResearchSection';
import ConnectSection from './components/ConnectSection';
import ChatAssistant from './components/ChatAssistant';
import { motion } from 'framer-motion';
import profile from './data/profile.json';
import styles from './App.module.css';

function App() {
  // References to sections for scrolling functionality
  const skillsRef = useRef(null);
  const educationRef = useRef(null);
  const achievementsRef = useRef(null);
  const projectsRef = useRef(null);
  const researchRef = useRef(null);
  const calendarRef = useRef(null);
  const feedbackRef = useRef(null);
  const connectRef = useRef(null);

  // Animation variants for narrative questions
  const questionVariants = {
    hidden: { opacity: 0, y: 40 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  // Scroll to section function
  const scrollToSection = (ref) => {
    if (ref && ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className={styles.appContainer}>
      <HeroSection profile={profile} />
      
      {/* Initial Narrative Question */}
      <motion.div 
        className={styles.narrativeQuestion}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.7 }}
        variants={questionVariants}
        onClick={() => scrollToSection(skillsRef)}
      >
        <h2>Need to know more about me?</h2>
        <div className={styles.scrollDown}>
          <div className={styles.arrow}></div>
        </div>
      </motion.div>
      
      {/* Skills Section with Question */}
      <motion.div 
        className={styles.narrativeQuestion}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.7 }}
        variants={questionVariants}
        onClick={() => scrollToSection(educationRef)}
      >
        <h2>What am I good at?</h2>
        <div className={styles.scrollDown}>
          <div className={styles.arrow}></div>
        </div>
      </motion.div>
      <div ref={skillsRef} id="skills">
        <SkillsSection profile={profile} />
      </div>
      
      {/* Education Section with Question */}
      <motion.div 
        className={styles.narrativeQuestion}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.7 }}
        variants={questionVariants}
        onClick={() => scrollToSection(achievementsRef)}
      >
        <h2>Where did I learn this from?</h2>
        <div className={styles.scrollDown}>
          <div className={styles.arrow}></div>
        </div>
      </motion.div>
      <div ref={educationRef} id="education">
        <EducationSection profile={profile} />
      </div>
      
      {/* Achievements Section with Question */}
      <motion.div 
        className={styles.narrativeQuestion}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.7 }}
        variants={questionVariants}
        onClick={() => scrollToSection(projectsRef)}
      >
        <h2>What have I achieved so far?</h2>
        <div className={styles.scrollDown}>
          <div className={styles.arrow}></div>
        </div>
      </motion.div>
      <div ref={achievementsRef} id="achievements">
        <AchievementsSection profile={profile} />
      </div>
      
      {/* Projects Section with Question */}
      <motion.div 
        className={styles.narrativeQuestion}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.7 }}
        variants={questionVariants}
        onClick={() => scrollToSection(researchRef)}
      >
        <h2>What projects have I done so far (or doing right now)?</h2>
        <div className={styles.scrollDown}>
          <div className={styles.arrow}></div>
        </div>
      </motion.div>
      <div ref={projectsRef} id="projects">
        <ProjectsSection profile={profile} />
      </div>
      
      {/* Research Section with Question */}
      <motion.div 
        className={styles.narrativeQuestion}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.7 }}
        variants={questionVariants}
        onClick={() => scrollToSection(calendarRef)}
      >
        <h2>Research Scientist you said, Any publications?</h2>
        <div className={styles.scrollDown}>
          <div className={styles.arrow}></div>
        </div>
      </motion.div>
      <div ref={researchRef} id="research">
        <ResearchSection profile={profile} />
      </div>
      
      {/* Calendar Section with Question */}
      <motion.div 
        className={styles.narrativeQuestion}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.7 }}
        variants={questionVariants}
        onClick={() => scrollToSection(feedbackRef)}
      >
        <h2>Am I available anytime soon?</h2>
        <div className={styles.scrollDown}>
          <div className={styles.arrow}></div>
        </div>
      </motion.div>
      <div ref={calendarRef} id="calendar" className={styles.calendarSection}>
        <p className={styles.calendarText}>
          You can check my availability and book a meeting through my Personal Assistant.
          Just click the chat icon in the bottom right corner and type "book meeting".
        </p>
      </div>
      
      {/* Feedback Section with Question */}
      <motion.div 
        className={styles.narrativeQuestion}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.7 }}
        variants={questionVariants}
        ref={feedbackRef}
        onClick={() => scrollToSection(connectRef)}
      >
        <h2>Any feedback for me? It only takes a sec, helps me a lot to improve. Thanks!</h2>
        <div className={styles.scrollDown}>
          <div className={styles.arrow}></div>
        </div>
      </motion.div>
      <div className={styles.feedbackSection}>
        <p className={styles.feedbackText}>
          Just click the chat icon and share your feedback with my Personal Assistant.
        </p>
      </div>
      
      {/* Connect Section with Question */}
      <motion.div 
        className={styles.narrativeQuestion}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.7 }}
        variants={questionVariants}
      >
        <h2>Connect with me?</h2>
      </motion.div>
      <div ref={connectRef} id="connect">
        <ConnectSection profile={profile} />
      </div>
      
      {/* Chat assistant for booking meetings and providing feedback */}
      <ChatAssistant profile={profile} />
    </div>
  );
}

export default App;
