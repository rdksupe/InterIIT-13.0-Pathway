import { useContext } from "react";
import { assets } from "../../assets/assets";
import "./main.css";
import { Context } from "../../context/Context";
import React, { useState, useEffect, useRef } from "react";
import Dropdown from "../dropdown/Dropdown";
import { TypeAnimation } from 'react-type-animation';
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import html2pdf from 'html2pdf.js';
import { marked } from 'marked';

const Main = () => {
	const {
		onSent,
		onRender,
		recentPrompt,
		showResults,
		setRecentPrompt,
		setShowResults,
		setResultData,
		setLoading,
		loading,
		resultData,
		setInput,
		input,
		evenData,
		setEvenData,
		graphData,
		setGraphData,
		downloadData,
		setDownloadData,
		socket,
		setSocket,
	} = useContext(Context);
	const [socket1, setSocket1] = useState(null);

	const resultDataRef = useRef(null); // Reference to the result-data container for auto scrolling

	const [markdownContent, setMarkdownContent] = useState('');


	const handleMarkdownChange = (e) => {
		setMarkdownContent(e.target.value);
	};

	const textAreaRef = useRef(null);

	const generatePDF = () => {
		// Send the raw Markdown content to the backend
		fetch('http://localhost:5000/convert', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ content: markdownContent }),
		})
		.then(response => {
			if (!response.ok) {
				throw new Error('Failed to send data to the backend');
			}
			return response.json();  // Expecting a JSON response
		})
		.then(data => {
			console.log('Markdown content sent successfully to backend:', data.message);
	
			// Now fetch the generated PDF from the backend after it's processed
			return fetch('http://localhost:5000/download-pdf', {
				method: 'GET',
			});
		})
		.then(response => {
			if (!response.ok) {
				throw new Error('Failed to fetch the generated PDF');
			}
			return response.blob(); // Convert the response to a blob
		})
		.then(blob => {
			// Create a download link and trigger the download
			const link = document.createElement('a');
			link.href = window.URL.createObjectURL(blob);
			link.download = 'generated_output.pdf'; // Specify the filename
			document.body.appendChild(link);
			link.click();
			link.remove();
		})
		.catch(error => {
			console.error('Error during the process:', error);
		});
	};

	// Auto-scrolling effect when resultData changes
	useEffect(() => {
		if (resultDataRef.current) {
			resultDataRef.current.scrollTop = resultDataRef.current.scrollHeight;
		}
	}, [resultData]);

	const handleCardClick = (promptText) => {
		setInput(promptText);
	};

	const handleClick = () => {
		setShowResults(true);
		setLoading(true);
		setRecentPrompt(input);
		let query = input;
		if (socket && socket.readyState === WebSocket.OPEN) {
			socket.send(JSON.stringify({ type: 'query', query }));
		}
		// try {
		// 	fetch('http://localhost:5000/query', {
		// 	  method: 'POST',
		// 	  headers: {
		// 		'Content-Type': 'application/json',
		// 	  },
		// 	  body: JSON.stringify({ query: input }), // Send input to the Flask backend
		// 	});
		
		// 	console.log('Query sent successfully!');
		// 	setLoading(false);
		//   } catch (error) {
		// 	console.error('Error sending query to backend:', error);
		// 	setLoading(false);
		//   }
	}

	// Adjust textarea height dynamically
	const adjustHeight = () => {
		const textArea = textAreaRef.current;

		// Reset the height to auto to shrink it before resizing
		textArea.style.height = 'auto';

		// Adjust the height based on scrollHeight
		textArea.style.height = `${textArea.scrollHeight}px`;

		// Move the textarea upwards by adjusting margin-top dynamically
		const diff = textArea.scrollHeight - textArea.clientHeight;
	};

	// Adjust height when input changes
	useEffect(() => {
		adjustHeight();
	}, [input]);

	const [files, setFiles] = useState([]);

	const handleFileChange = (event) => {
		setEvenData(event);
	};

	const triggerFileInput = () => {
		document.getElementById('hiddenFileInput').click(); // Programmatically trigger click on hidden input
	};

	useEffect(() => {
		const ws = new WebSocket('ws://localhost:8090');
		ws.onopen = () => {
			console.log('WebSocket connected to agent server');
		};
		ws.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);

				if (data.type === 'agents') {
					console.log("agents data", data);
					onRender(data.response);
					// console.log(data.response);
					setMarkdownContent(data.response);
				}
			} catch (error) {
				console.error('Error parsing WebSocket message:', error);
			}
		};
		ws.onclose = () => {
			console.log('WebSocket disconnected');
		};
		setSocket1(ws);
		return () => {
			ws.close();
		};
	}, []);

	useEffect(() => {
		const ws = new WebSocket('ws://localhost:8080');
		ws.onopen = () => {
			console.log('WebSocket connected');
		};
		ws.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);

				if (data.type === 'graph') {
					
					const graph = JSON.parse(data.response);
					console.log(graph);
					setGraphData(graph);
				
				} else if (data.type === 'response') {
					onRender(data.response);
					console.log(data.response);
					setMarkdownContent(data.response);
				} else if (data.type === 'agents') {
					console.log("agents data", data);
				}
			} catch (error) {
				console.error('Error parsing WebSocket message:', error);
			}
		};
		ws.onclose = () => {
			console.log('WebSocket disconnected');
		};
		setSocket(ws);
		return () => {
			ws.close();
		};
	}, []);

	return (
		<div className="main" tabIndex="0" onKeyDown={(e) => {
			if (e.key === 'Enter') {
				e.preventDefault();
				handleClick();
			}
		}}>
			<div className="nav">
				<img src={assets.pathway_icon} className="pway" alt="" />
				<div className="rightside">
					<Dropdown />
					<img src={assets.user} className="user" alt="" />
				</div>
			</div>
			<div className="main-content">
				<div className="main-container" >
					{!showResults ? (
						<>
							<div className="contain">
								<div className="greet">
									<TypeAnimation
										sequence={[
											'Hello, Team 30!',
										]}
										speed={{ type: 'keyStrokeDelayInMs', value: 100 }}
										style={{ fontSize: '1em' }}
									/>
									<p style={{ fontSize: '0.75em' }}>How can I help you today?</p>
								</div>
								<div className="cards">
									<div
										className="card"
										onClick={() =>
											handleCardClick("Give me a detailed report on the current state of Russian economy and the impacts of sanctions. I am Aramco and is will it br profitable for me to acquire Lukoil? Will the sanction pose any problem for my company in any prospect?")
										}
									>
										<p style={{ textAlign: "justify" }}>Give me a detailed report on the current state of Russian economy and the impacts of sanctions. I am Aramco and is will it br profitable for me to acquire Lukoil? Will the sanction pose any problem for my company in any prospect?</p>
										{/* <img src={assets.compass_icon} alt="" /> */}
									</div>
									<div
										className="card"
										onClick={() => {
											handleCardClick(
												"Analyze AT&T's financial performance post-acquisition of DirecTV, focusing on Return on Investment (ROI) and identifying any significant accounting adjustments related to the deal."
											);
										}}
									>
										<p style={{ textAlign: "justify" }}>Analyze AT&T's financial performance post-acquisition of DirecTV, focusing on Return on Investment (ROI) and identifying any significant accounting adjustments related to the deal.</p>
									</div>
									<div
										className="card"
										onClick={() =>
											handleCardClick(
												"Give me a detailed report on the current state of ed-tech sector in India and US. Can chegg acquire byju's, what would be the impact of such merger and acquisition on the market in every prospect?"
											)
										}
									>
										<p style={{ textAlign: "justify" }}>Give me a detailed report on the current state of ed-tech sector in India and US. Can chegg acquire byju's, what would be the impact of such merger and acquisition on the market in every prospect? </p>
										{/* <img src={assets.message_icon} alt="" /> */}
									</div>
									<div
										className="card"
										onClick={() =>
											handleCardClick("Analyze CoStar Group's and LoopNet's financial statements to identify potential areas of legal and financial risk associated with their overlapping business operations.")
										}
									>
										<p style={{ textAlign: "justify" }}>Analyze CoStar Group's and LoopNet's financial statements to identify potential areas of legal and financial risk associated with their overlapping business operations.</p>
									</div>
									{/* Your card elements here */}
								</div>
							</div>

						</>
					) : (
						<div className="result">
							<div className="result-title">
								<img src={assets.user} className="result-user" alt="" />
								<p>{recentPrompt}</p>
							</div>
							<div className="result-data" ref={resultDataRef} style={{ overflowY: 'auto', maxHeight: '400px' }}>
								<img src={assets.pway_icon} className="pway-res" alt="" />
								{loading ? (
									<div className="loader">
										<hr />
										<hr />
										<hr />
									</div>
								) : (
									<div className="markdown-content">
										<ReactMarkdown 
										rehypePlugins={[rehypeRaw]} 
										remarkPlugins={[remarkGfm]}
										components={{
											a: ({ href, children }) => (
											  <a href={href} target="_blank" rel="noopener noreferrer">
												{children}
											  </a>
											)
										  }}>{resultData}</ReactMarkdown>
									</div>
								)}
							</div>
							{downloadData && (
								<img src = {assets.download_icon} onClick={generatePDF} style={{width: '20px', margin:'10px 50px'}}>
								</img>
							)}
						</div>
					)}
				</div>
				<div className="main-bottom">
					<div className="search-box">
						<textarea
							ref={textAreaRef}
							onChange={(e) => setInput(e.target.value)}
							value={input}
							placeholder="Enter the Prompt Here"
							onKeyDown={(e) => {
								if (e.key === 'Enter') {
									e.preventDefault();
									handleClick();
								}
							}}
							rows={1} // Start with 1 row
							style={{
								position: 'relative',
								background: '#f0f4f9',
								outline: 'none',
								border: 'none',
								width: '100%',
								minHeight: '40px', // Minimum height for the textarea
								maxHeight: '100px',
								resize: 'none', // Disable manual resize by the user
								overflow: 'hidden', // Hide overflow to prevent scrollbars
								fontSize: '16px', // Adjust font size as needed
								borderRadius: '5px', // Rounded corners for style
								overflowY: 'auto'
							}}
						/>
						<div>
							<img src={assets.attach_icon} alt="Upload" onClick={triggerFileInput} />
							<input
								webkitdirectory="true"
								multiple
								id="hiddenFileInput"
								type="file"
								style={{ display: 'none' }} // Hide the input field
								onChange={handleFileChange}
							/>
							<img
								src={assets.send_icon}
								alt=""
								onClick={handleClick}
							/>
						</div>
					</div>
					<div className="bottom-info">
						<p></p>
					</div>
				</div>
			</div>
		</div>
	);
};

export default Main;
