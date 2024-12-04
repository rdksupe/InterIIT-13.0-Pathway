import { createContext, useState, useRef } from "react";
import runChat from "../config/Gemini";

export const Context = createContext();

const ContextProvider = (props) => {
	const [input, setInput] = useState("");
	const [recentPrompt, setRecentPrompt] = useState("");
	const [prevPrompts, setPrevPrompts] = useState([]);
	const [showResults, setShowResults] = useState(false);
	const [loading, setLoading] = useState(false);
	const [resultData, setResultData] = useState("");
	const [graphData, setGraphData] = useState();
	const [socket, setSocket] = useState(null);
	const [evenData, setEvenData] = useState();
	const [downloadData, setDownloadData] = useState(false);
	const [chatNo, setChatNo] = useState(0);
	const displayedCharsRef = useRef(0); // Use a ref to track displayed characters count
	const totalCharsRef = useRef(0); // Use a ref for total characters

	// Helper function to update displayed characters and check if all have been shown
	const delayPara = (index, nextWord) => {
		setTimeout(function () {
			setResultData((prev) => prev + nextWord); // Append nextWord to resultData

			// Increment the displayed character count
			displayedCharsRef.current += 1; 

			// Check if all characters are displayed
			if (displayedCharsRef.current === totalCharsRef.current) {
				// All characters are shown, so set downloadData to true
				console.log('All characters displayed. Setting downloadData to true');
				setDownloadData(true);
			}
		}, 1 * index); // Slower pace for better visibility
	};

	// Function to reset the states for a new chat
	const newChat = () => {
		setLoading(false);
		setShowResults(false);
		setDownloadData(false);
		setChatNo(0);
		displayedCharsRef.current = 0; // Reset ref for displayed characters
	};

	// Function to handle sending the prompt
	const onSent = async (prompt, isAgent) => {
		setResultData("");
		setLoading(true);
		setShowResults(true);
		let response;
		if (isAgent === undefined) {
			if (prompt !== undefined) {
				response = await runChat(prompt);
				setRecentPrompt(prompt);
			} else {
				setPrevPrompts((prev) => [...prev, input]);
				setRecentPrompt(input);
				response = await runChat(input);
			}
		}

		try {
			let responseArray = response.split("**");
			let newResponse = "";
			for (let i = 0; i < responseArray.length; i++) {
				if (i === 0 || i % 2 !== 1) {
					newResponse += responseArray[i];
				} else {
					newResponse += "<b>" + responseArray[i] + "</b>";
				}
			}
			let newResponse2 = newResponse.split("*").join("<br/>");
			totalCharsRef.current = newResponse2.length; // Set the total chars to be displayed
			let newResponseArray = newResponse2.split("");
			for (let i = 0; i < newResponseArray.length; i++) {
				const nextWord = newResponseArray[i];
				delayPara(i, nextWord + "");
			}
		} catch (error) {
			console.error("Error while running chat:", error);
		} finally {
			setLoading(false);
			setInput("");
		}
	};

	// Function to render a pre-existing response
	const onRender = async (data) => {
		setResultData("");
		let response = data;
		try {
			let responseArray = response.split("**");
			let newResponse = "";
			for (let i = 0; i < responseArray.length; i++) {
				if (i === 0 || i % 2 !== 1) {
					newResponse += responseArray[i];
				} else {
					newResponse += "<b>" + responseArray[i] + "</b>";
				}
			}
			let newResponse2 = newResponse.split("*").join("<br/>");
			totalCharsRef.current = newResponse2.length; // Set the total chars to be displayed
			let newResponseArray = newResponse2.split("");
			for (let i = 0; i < newResponseArray.length; i++) {
				const nextWord = newResponseArray[i];
				delayPara(i, nextWord + "");
			}
		} catch (error) {
			console.error("Error while running chat:", error);
		} finally {
			// Check if all characters have been displayed
			setLoading(false);
			setInput("");
		}
	};

	const contextValue = {
		prevPrompts,
		setPrevPrompts,
		onSent,
		setShowResults,
		setRecentPrompt,
		setResultData,
		recentPrompt,
		input,
		onRender,
		setInput,
		showResults,
		setLoading,
		loading,
		resultData,
		newChat,
		graphData,
		setGraphData,
		evenData,
		setEvenData,
		socket,
		setSocket,
		downloadData,
		setDownloadData,
		chatNo,
		setChatNo
	};

	return <Context.Provider value={contextValue}>{props.children}</Context.Provider>;
};

export default ContextProvider;
