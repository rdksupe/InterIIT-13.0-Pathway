import React, { useEffect, useState, useContext } from "react";
import { FaFolder, FaFileAlt, FaChevronRight, FaChevronDown } from "react-icons/fa";
import { Context } from "../../context/Context";

// Viewer component
const Viewer = () => {
  const { fileHistory, setFileHistory } = useContext(Context);
  return (
    <div className="App">
      <h2>File Explorer</h2>
        <div style={{ marginTop: "20px" }}>
          <p className="fileHistory">
        {fileHistory.length > 0
          ? fileHistory.map((file, index) => (
              <span key={index}>
                {file.fileName}
                <br />
              </span>
            ))
          : "No files uploaded."}
      </p>
        </div>
    </div>
  );
};

export default Viewer;
