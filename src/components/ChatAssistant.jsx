import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './ChatAssistant.module.css';

const initialMessages = [
  { from: 'assistant', text: 'Hi! I am your digital assistant. Ask me anything about Mohammed Noushir, or book a meeting!' }
];

const ChatAssistant = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (open && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, open]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages([...messages, { from: 'user', text: input }]);
    // Placeholder: Simulate assistant reply
    setTimeout(() => {
      setMessages(msgs => [...msgs, { from: 'assistant', text: 'I will answer that soon! (Backend coming soon)' }]);
    }, 800);
    setInput('');
  };

  return (
    <>
      <motion.button
        className={styles.launcher}
        onClick={() => setOpen(true)}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        transition={{ type: 'spring', stiffness: 300 }}
        aria-label="Open chat assistant"
        style={{ display: open ? 'none' : 'flex' }}
      >
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="16" r="16" fill="#6a82fb" />
          <path d="M10 22V10h12v12H10zm2-2h8v-8h-8v8z" fill="#fff" />
        </svg>
      </motion.button>
      <AnimatePresence>
        {open && (
          <motion.div
            className={styles.chatOverlay}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className={styles.chatWindow}
              initial={{ y: 100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 100, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 200 }}
            >
              <div className={styles.chatHeader}>
                <span>Assistant</span>
                <button className={styles.closeBtn} onClick={() => setOpen(false)}>&times;</button>
              </div>
              <div className={styles.chatBody}>
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={msg.from === 'assistant' ? styles.assistantMsg : styles.userMsg}
                  >
                    {msg.text}
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
              <form className={styles.chatInputBar} onSubmit={handleSend}>
                <input
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="Type your message..."
                  className={styles.chatInput}
                  autoFocus
                />
                <button type="submit" className={styles.sendBtn}>Send</button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatAssistant; 