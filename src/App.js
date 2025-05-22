import React from 'react';
import HeroSection from './components/HeroSection';
import NarrativeScroll from './components/NarrativeScroll';
import SkillsSection from './components/SkillsSection';
import EducationSection from './components/EducationSection';
import AchievementsSection from './components/AchievementsSection';
import ProjectsSection from './components/ProjectsSection';
import ResearchSection from './components/ResearchSection';
import ChatAssistant from './components/ChatAssistant';
import profile from './data/profile.json';
import styles from './App.module.css';

function App() {
  return (
    <div className={styles.appContainer}>
      <HeroSection profile={profile} />
      <NarrativeScroll />
      <SkillsSection profile={profile} />
      <EducationSection profile={profile} />
      <AchievementsSection profile={profile} />
      <ProjectsSection profile={profile} />
      <ResearchSection profile={profile} />
      <ChatAssistant profile={profile} />
    </div>
  );
}

export default App;
