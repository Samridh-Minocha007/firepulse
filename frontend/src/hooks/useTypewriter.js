import { useState, useEffect } from 'react';

// A "Custom Hook" is a reusable piece of logic that uses React's built-in hooks.
// Its name must start with "use". This hook creates a typewriter effect for any text.
export const useTypewriter = (text, speed = 50) => {
  const [displayText, setDisplayText] = useState('');

  useEffect(() => {
    let i = 0;
    // Clear the text when the input text changes
    setDisplayText(''); 
    
    if (text) {
      const typingInterval = setInterval(() => {
        if (i < text.length) {
          setDisplayText(prevText => prevText + text.charAt(i));
          i++;
        } else {
          clearInterval(typingInterval);
        }
      }, speed);

      // Cleanup function to clear the interval if the component unmounts
      return () => {
        clearInterval(typingInterval);
      };
    }
  }, [text, speed]); // The effect re-runs whenever the `text` or `speed` props change

  return displayText;
};