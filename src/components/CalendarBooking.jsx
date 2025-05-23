import React, { useState, useEffect } from 'react';
import styles from './CalendarBooking.module.css';

// API URL - change for production
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const CalendarBooking = ({ onClose, onSuccess }) => {
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [bookingForm, setBookingForm] = useState({
    name: '',
    email: '',
    reason: ''
  });
  const [step, setStep] = useState(1); // 1: Select slot, 2: Fill form, 3: Confirmation
  const [bookingResult, setBookingResult] = useState(null);

  // Fetch available slots
  useEffect(() => {
    const fetchAvailability = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/calendar/availability`);
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        // Group slots by day
        const slots = data.available_slots || [];
        const groupedSlots = groupSlotsByDay(slots);
        setAvailableSlots(groupedSlots);
      } catch (err) {
        console.error('Error fetching availability:', err);
        setError('Could not load available time slots. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchAvailability();
  }, []);

  // Group slots by day for better UI organization
  const groupSlotsByDay = (slots) => {
    const grouped = {};
    slots.forEach(slot => {
      const date = new Date(slot.start);
      const day = date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
      
      if (!grouped[day]) {
        grouped[day] = [];
      }
      
      const startTime = new Date(slot.start).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
      const endTime = new Date(slot.end).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
      
      grouped[day].push({
        ...slot,
        displayTime: `${startTime} - ${endTime}`
      });
    });
    
    return grouped;
  };

  const handleSlotSelection = (slot) => {
    setSelectedSlot(slot);
    setStep(2);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setBookingForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleBooking = async (e) => {
    e.preventDefault();
    
    if (!selectedSlot || !bookingForm.name || !bookingForm.email) {
      setError('Please fill out all required fields');
      return;
    }
    
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/calendar/book`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          start_time: selectedSlot.start,
          end_time: selectedSlot.end,
          name: bookingForm.name,
          email: bookingForm.email,
          reason: bookingForm.reason || 'Meeting with Mohammed Noushir'
        })
      });
      
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || 'Failed to book appointment');
      }
      
      setBookingResult(result);
      setStep(3);
    } catch (err) {
      console.error('Error booking appointment:', err);
      setError(err.message || 'Failed to book appointment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (step === 3 && onSuccess) {
      onSuccess(bookingResult);
    }
    onClose();
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderSlotSelection = () => (
    <div className={styles.slotSelection}>
      <h3>Select a time slot</h3>
      {Object.keys(availableSlots).length === 0 && !loading && !error && (
        <p className={styles.noSlots}>No available time slots found.</p>
      )}
      
      {Object.entries(availableSlots).map(([day, slots]) => (
        <div key={day} className={styles.dayGroup}>
          <h4>{day}</h4>
          <div className={styles.slotGrid}>
            {slots.map((slot, index) => (
              <button
                key={index}
                className={styles.slotButton}
                onClick={() => handleSlotSelection(slot)}
              >
                {slot.displayTime}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  const renderBookingForm = () => (
    <form className={styles.bookingForm} onSubmit={handleBooking}>
      <h3>Book your appointment</h3>
      <p className={styles.selectedTime}>
        Selected time: {selectedSlot?.displayTime}
      </p>
      
      <div className={styles.formGroup}>
        <label htmlFor="name">Your Name *</label>
        <input
          type="text"
          id="name"
          name="name"
          value={bookingForm.name}
          onChange={handleFormChange}
          required
        />
      </div>
      
      <div className={styles.formGroup}>
        <label htmlFor="email">Your Email *</label>
        <input
          type="email"
          id="email"
          name="email"
          value={bookingForm.email}
          onChange={handleFormChange}
          required
        />
      </div>
      
      <div className={styles.formGroup}>
        <label htmlFor="reason">Reason for Meeting</label>
        <textarea
          id="reason"
          name="reason"
          value={bookingForm.reason}
          onChange={handleFormChange}
          placeholder="Briefly describe what you'd like to discuss"
          rows={3}
        />
      </div>
      
      <div className={styles.formActions}>
        <button 
          type="button" 
          className={styles.backButton}
          onClick={() => setStep(1)}
        >
          Back
        </button>
        <button 
          type="submit" 
          className={styles.bookButton} 
          disabled={loading}
        >
          {loading ? 'Booking...' : 'Book Appointment'}
        </button>
      </div>
    </form>
  );

  const renderConfirmation = () => (
    <div className={styles.confirmation}>
      <div className={styles.successIcon}>✓</div>
      <h3>Appointment Booked!</h3>
      <p>
        Your meeting with Mohammed Noushir has been scheduled for:<br />
        <strong>{formatDate(selectedSlot.start)}</strong>
      </p>
      <p>
        A confirmation has been sent to:<br />
        <strong>{bookingForm.email}</strong>
      </p>
      <p className={styles.bookingId}>
        Booking Reference: {bookingResult?.event_id || 'N/A'}
      </p>
      <button 
        className={styles.doneButton} 
        onClick={handleClose}
      >
        Done
      </button>
    </div>
  );

  return (
    <div className={styles.calendarContainer}>
      <div className={styles.calendarHeader}>
        <h2>Schedule a Meeting with Mohammed</h2>
        <button className={styles.closeButton} onClick={handleClose}>×</button>
      </div>
      
      {loading && step === 1 && (
        <div className={styles.loadingState}>
          <div className={styles.spinner}></div>
          <p>Loading available time slots...</p>
        </div>
      )}
      
      {error && (
        <div className={styles.errorState}>
          <p>{error}</p>
          <button 
            className={styles.retryButton} 
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      )}
      
      {!loading && !error && (
        <>
          {step === 1 && renderSlotSelection()}
          {step === 2 && renderBookingForm()}
          {step === 3 && renderConfirmation()}
        </>
      )}
    </div>
  );
};

export default CalendarBooking; 