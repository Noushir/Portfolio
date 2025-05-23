import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './ChatAssistant.module.css';
import CalendarBooking from './CalendarBooking';

const initialMessages = [
  { from: 'assistant', text: "Hi! I am Noushir's Agentic assistant. Ask me anything about Mohammed Noushir, Give feedback for him or type \"book meeting\" to schedule an appointment!" }
];

// API URL - change for production
const API_URL = 'https://backend-api-687202216907.europe-west2.run.app';

const ChatAssistant = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState({ connected: true, message: "" });
  const [isMobile, setIsMobile] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatBodyRef = useRef(null);

  // Check for calendar keywords
  const checkForCalendarIntent = (message) => {
    const calendarKeywords = [
      'book meeting', 'schedule meeting', 'book appointment', 'schedule appointment',
      'book a meeting', 'schedule a meeting', 'book a call', 'schedule a call',
      'book time', 'schedule time', 'book a slot', 'schedule a slot'
    ];
    
    return calendarKeywords.some(keyword => 
      message.toLowerCase().includes(keyword.toLowerCase())
    );
  };

  // Check if device is mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    // Initial check
    checkMobile();
    
    // Add event listener for window resize
    window.addEventListener('resize', checkMobile);
    
    // Cleanup
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Fix iOS vh bug (100vh includes address bar)
  useEffect(() => {
    const fixIOSVh = () => {
      if (isMobile && open) {
        // Calculate real viewport height
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
      }
    };
    
    fixIOSVh();
    window.addEventListener('resize', fixIOSVh);
    
    return () => window.removeEventListener('resize', fixIOSVh);
  }, [isMobile, open]);

  useEffect(() => {
    if (open && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, open]);

  // Check API connection when chat is opened
  useEffect(() => {
    if (open) {
      checkApiConnection();
      
      // Focus input when opened on non-mobile
      if (!isMobile && inputRef.current) {
        inputRef.current.focus();
      }
    }
  }, [open, isMobile]);

  // Handle keyboard issues on mobile
  useEffect(() => {
    if (isMobile && open) {
      const handleKeyboardOpen = () => {
        setTimeout(() => {
          if (chatBodyRef.current && chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
          }
        }, 300);
      };
      
      inputRef.current?.addEventListener('focus', handleKeyboardOpen);
      
      return () => {
        inputRef.current?.removeEventListener('focus', handleKeyboardOpen);
      };
    }
  }, [isMobile, open, messages]);

  const checkApiConnection = async () => {
    try {
      // Use the backend API URL directly for the health check
      const response = await fetch(`${API_URL}/`);
      if (response.ok) {
        setApiStatus({ connected: true, message: "" });
      } else {
        setApiStatus({ 
          connected: false, 
          message: "API server is not responding correctly. Some features may not work."
        });
      }
    } catch (error) {
      console.error('API connection check failed:', error);
      setApiStatus({ 
        connected: false, 
        message: "Cannot connect to the assistant's backend server."
      });
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Check for calendar booking intent
    const isCalendarRequest = checkForCalendarIntent(input);
    
    // Add user message to chat
    setMessages([...messages, { from: 'user', text: input }]);
    setIsLoading(true);
    
    // Store the current message to use in the local fallback
    const currentMessage = input;
    setInput('');
    
    // Handle calendar booking intent
    if (isCalendarRequest) {
      setIsLoading(false);
      
      // Add assistant response
      setMessages(msgs => [...msgs, { 
        from: 'assistant', 
        text: "I'd be happy to help you schedule a meeting with Mohammed. Let me show you the available time slots."
      }]);
      
      // Show calendar booking component
      setTimeout(() => {
        setShowCalendar(true);
      }, 500);
      
      return;
    }
    
    try {
      // Call the backend API
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: currentMessage }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        // Check for API key configuration errors
        if (data.content && data.content.includes("API configuration error")) {
          throw new Error("API key not configured");
        }
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      // Add assistant response to chat
      setMessages(msgs => [...msgs, { from: 'assistant', text: data.content }]);
      setApiStatus({ connected: true, message: "" });
    } catch (error) {
      console.error('Error calling API:', error);
      
      let fallbackResponse = "Sorry, I couldn't connect to my knowledge base. Please try again later.";
      
      // Special message for API key issues
      if (error.message === "API key not configured") {
        fallbackResponse = "The AI assistant is not properly configured. The API key is missing. Please contact the site administrator.";
        setApiStatus({ 
          connected: false, 
          message: "Backend API key not configured. Please set up a Groq API key."
        });
      } else if (apiStatus.connected === false) {
        // If we already know we're disconnected, provide a more specific message
        fallbackResponse = "I'm currently offline. My backend server isn't connected. Please try again later.";
      } else {
        // Update the API status for other errors
        setApiStatus({ 
          connected: false, 
          message: "Lost connection to the assistant's backend server."
        });
      }
      
      setMessages(msgs => [...msgs, { from: 'assistant', text: fallbackResponse }]);
    } finally {
      setIsLoading(false);
      // Focus back on input after sending
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };
  
  const handleCalendarSuccess = (bookingResult) => {
    // Add a message about the successful booking
    setMessages(msgs => [...msgs, { 
      from: 'assistant', 
      text: `Great! I've booked your meeting with Mohammed for ${new Date(bookingResult.start_time).toLocaleString()}. You'll receive a confirmation at ${bookingResult.email}. Your booking reference is ${bookingResult.event_id}.`
    }]);
    setShowCalendar(false);
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
              initial={isMobile ? { y: "100%" } : { y: 100, opacity: 0 }}
              animate={isMobile ? { y: 0 } : { y: 0, opacity: 1 }}
              exit={isMobile ? { y: "100%" } : { y: 100, opacity: 0 }}
              transition={{ type: 'spring', stiffness: isMobile ? 300 : 200 }}
              style={isMobile ? { height: 'calc(var(--vh, 1vh) * 100)' } : {}}
            >
              <div className={styles.chatHeader}>
                <span>
                  Agentic Personal Assistant 
                  {!apiStatus.connected && (
                    <span className={styles.offlineIndicator}> (Offline)</span>
                  )}
                </span>
                <button className={styles.closeBtn} onClick={() => setOpen(false)}>&times;</button>
              </div>
              {!apiStatus.connected && apiStatus.message && (
                <div className={styles.apiWarning}>
                  {apiStatus.message}
                </div>
              )}
              
              {showCalendar ? (
                <div className={styles.calendarWrapper}>
                  <CalendarBooking 
                    onClose={() => setShowCalendar(false)} 
                    onSuccess={handleCalendarSuccess} 
                  />
                </div>
              ) : (
                <>
                  <div className={styles.chatBody} ref={chatBodyRef}>
                    {messages.map((msg, i) => (
                      <div
                        key={i}
                        className={msg.from === 'assistant' ? styles.assistantMsg : styles.userMsg}
                      >
                        {msg.text}
                      </div>
                    ))}
                    {isLoading && (
                      <div className={styles.assistantMsg}>
                        <div className={styles.typingIndicator}>
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    )}
                    <div ref={chatEndRef} />
                  </div>
                  <form className={styles.chatInputBar} onSubmit={handleSend}>
                    <input
                      type="text"
                      value={input}
                      onChange={e => setInput(e.target.value)}
                      placeholder="Type your message..."
                      className={styles.chatInput}
                      disabled={isLoading}
                      ref={inputRef}
                      autoComplete="off"
                    />
                    <button type="submit" className={styles.sendBtn} disabled={isLoading}>
                      {isLoading ? '...' : 'Send'}
                    </button>
                  </form>
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatAssistant; 