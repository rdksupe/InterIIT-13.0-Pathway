import React, { useEffect, useState, useContext } from "react";
import { FaFolder, FaFileAlt, FaChevronRight, FaChevronDown } from "react-icons/fa";
import { Context } from "../../context/Context";

// Recursive function to create folder tree
const createFolderStructure = (pathParts, fileName) => {
  // Initialize root folder with the first part of the path
  let currentFolder = pathParts[0];

  // Defining folder schema
  let folderStructure = {
    title: currentFolder,
    isFile: false,
    children: [],
  };

  let currentFolderNode = folderStructure;

  // Loop through the remaining path parts
  for (let i = 1; i < pathParts.length; i++) {
    const folderName = pathParts[i];
    let existingFolder = currentFolderNode.children.find(
      (folder) => folder.title === folderName
    );

    if (!existingFolder) {
      existingFolder = {
        title: folderName,
        isFile: false,
        children: [],
      };
      currentFolderNode.children.push(existingFolder);
    }

    currentFolderNode = existingFolder;
  }

  // If the last part of the path is the fileName, set isFile to true
  if (pathParts[pathParts.length - 1] === fileName) {
    currentFolderNode.isFile = true;
  }

  // Return the root folder structure
  return folderStructure;
};


// Component to render each folder or file node
const FolderNode = ({ node, expandedFolders, toggleExpand }) => {
  const isExpanded = expandedFolders.includes(node.title);
  if(node.children.length == 0){
    node.isFile = true;
  }

  return (
    <div>
      <div className="folderNodeStyle">
        {node.children.length > 0 && (
          <span
            style={{ cursor: "pointer", marginRight: 10 }}
            onClick={() => toggleExpand(node.title)}
          >
            {isExpanded ? <FaChevronDown /> : <FaChevronRight />}
          </span>
        )}
        <FaFolder style={{ marginRight: "8px", color: "#2c3e50" }} />
        <span>{node.title}</span>
      </div>

      {isExpanded && (
        <div style={{ paddingLeft: 20 }}>
          {node.children.map((child, idx) => {
            if (child.isFile) {
              return (
                <div key={idx} className="fileNodeStyle">
                  <FaFileAlt style={{ marginRight: "8px", color: "#2980b9" }} />
                  <span>{child.title}</span>
                </div>
              );
            } else {
              return (
                <FolderNode
                  key={idx}
                  node={child}
                  expandedFolders={expandedFolders}
                  toggleExpand={toggleExpand}
                />
              );
            }
          })}
        </div>
      )}
    </div>
  );
};

// Component to manage the tree view
const TreeView = ({ treeData, expandedFolders, toggleExpand }) => {
  return (
    <div>
      {treeData.map((node, index) => (
        <FolderNode
          key={index}
          node={node}
          expandedFolders={expandedFolders}
          toggleExpand={toggleExpand}
        />
      ))}
    </div>
  );
};

// Main App Component
const Viewer = () => {
  const [treeData, setTreeData] = useState([]);
  const [expandedFolders, setExpandedFolders] = useState([]);
  const {
    evenData,
    setEvenData
	} = useContext(Context);

  useEffect(() => {
    if (treeData.length > 0) {
      console.log("Tree data updated:", treeData);
    }
  }, [treeData]);
  

  useEffect(() => {
    if(evenData !== undefined){
      console.log("Used it when undefined")
      handleFileUpload(evenData)
    }
	}, [evenData]);

  // Handle file upload event
  const handleFileUpload = (event) => {
    const files = event.target.files;

    const fileData = [];
  
    Array.from(files).forEach((file) => {
      const pathParts = file.webkitRelativePath
        ? file.webkitRelativePath.split("/") // For folder uploads
        : [file.name]; // For single files
  
      const folderStructure = createFolderStructure(pathParts, file.name);
      fileData.push(folderStructure);
    });
  
    // Update the tree structure by merging new folder data
    const mergedData = mergeFolderStructures(fileData, treeData);
  
    if (mergedData) {
      setTreeData(mergedData);
    } else {
      console.error("Error merging folder structures");
    }
  };

  // Merge new folder structures into the existing tree data
  const mergeFolderStructures = (newStructure, existingStructure) => {
    const merged = [...existingStructure];

    newStructure.forEach((newFolder) => {
      let existingFolder = findFolderByTitle(merged, newFolder.title);
      if (!existingFolder) {
        merged.push(newFolder);
      } else {
        existingFolder.children = mergeFolderStructures(
          newFolder.children,
          existingFolder.children
        );
      }
    });

    return merged;
  };

  // Find a folder by its title in the current structure
  const findFolderByTitle = (folders, title) => {
    return folders.find((folder) => folder.title === title);
  };

  // Toggle expand/collapse of folders
  const toggleExpand = (folderName) => {
    setExpandedFolders((prevExpandedFolders) => {
      if (prevExpandedFolders.includes(folderName)) {
        return prevExpandedFolders.filter((folder) => folder !== folderName);
      } else {
        return [...prevExpandedFolders, folderName];
      }
    });
  };

  return (
    <div className="App">
      <h2>File Explorer</h2>
      {treeData.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <TreeView
            treeData={treeData}
            expandedFolders={expandedFolders}
            toggleExpand={toggleExpand}
          />
        </div>
      )}
    </div>
  )
};

export default Viewer;