import React, { useContext, useState } from 'react';
import { Context } from '../../context/Context';

const Dropdown = () => {
  // Initialize state for selectedOption and modelName
  const [selectedOption, setSelectedOption] = useState('gpt-4o');  // Default selected value
  const [modelName, setModelName] = useState('gpt-4o'); // Default modelName

  const {
    socket, 
    setSocket
  } = useContext(Context)

  const handleChange = (event) => {
    const selectedValue = event.target.value;  // Get the selected option value
    setSelectedOption(selectedValue);  // Update selectedOption state
    setModelName(selectedValue);  // Update modelName state

    event.preventDefault();  // Prevent default form submission (if applicable)

    console.log(selectedValue);  // Log the selected value for debugging

    // WebSocket logic
    if (socket && socket.readyState === WebSocket.OPEN) {
      const model = { MODEL_NAME : selectedValue}

      socket.send(JSON.stringify({ type: 'llm', model }));
    }
  };

  return (
    <div style={styles.container}>
      <select value={selectedOption} onChange={handleChange} style={styles.dropdown}>
        <option style={styles.opt} value="gpt-4o">GPT 4-o</option>
        <option style={styles.opt} value="gpt-4o-mini">GPT 4-o mini</option>
      </select>
    </div>
  );
};

// Inline styles for simplicity
const styles = {
  container: {
    textAlign: "center",
    margin: "10px",
    // backgroundColor: "#f9f9f9",
    maxWidth: "1200px",
  },

  header: {
    fontSize: "18px",
    marginBottom: "10px",
  },
  dropdown: {
    padding: "10px",
    fontSize: "16px",
    width: "100%",
    borderRadius: "5px",
    border: "1px solid #ddd",
    outline: "none",
  },

  result: {
    marginTop: "20px",
    fontSize: "16px",
    color: "#333",
  },
};

export default Dropdown;
