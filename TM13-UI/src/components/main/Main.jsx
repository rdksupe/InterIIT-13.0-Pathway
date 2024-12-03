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
		socket,
		setSocket,
		downloadData,
		setDownloadData,
	} = useContext(Context);
	// const [socket, setSocket] = useState(null);

	const resultDataRef = useRef(null); // Reference to the result-data container for auto scrolling
	
	const [markdownContent, setMarkdownContent] = useState('');


  const handleMarkdownChange = (e) => {
    setMarkdownContent(e.target.value);
  };

  const generatePDF = () => {
    //console.log(resultData);
    // Convert Markdown to HTML using 'marked'
    const htmlContent = marked(markdownContent);

    // Create a div element to temporarily hold the HTML content
    const element = document.createElement('div');
    element.innerHTML = htmlContent;

    // Apply custom styles to adjust line gap and make it look nice
    const style = document.createElement('style');
    style.innerHTML = `
      div {
        font-family: Arial, sans-serif;
        font-size: 14px;
        line-height: 1.8; /* Adjust this value to set the line gap */
        text-align: justify;
      }
      h1, h2, h3, h4 {
        font-weight: bold;
        margin-top: 10px;
      }
      p {
        margin-bottom: 15px;
      }
    `;
    element.appendChild(style);

    // Use html2pdf.js to convert the HTML to a PDF with margins and line gap
    html2pdf()
      .from(element)
      .set({
        margin: 20, // Set margin for all sides (top, bottom, left, right)
        filename: 'response.pdf',
        html2canvas: { scale: 5 },  // Increase the scale for better resolution
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      })
      .save()
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
	}

	const [files, setFiles] = useState([]);

	const handleFileChange = (event) => {
		setEvenData(event);
	};

	const triggerFileInput = () => {
		document.getElementById('hiddenFileInput').click(); // Programmatically trigger click on hidden input
	};

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
		<div className="main">
			<div className="nav">
				<img src={assets.pathway_icon} className="pway" alt="" />
				<div className="rightside">
					<Dropdown />
					<img src={assets.user} className="user" alt="" />
				</div>
			</div>
			<div className="main-content">
				<div className="main-container">
					{!showResults ? (
						<>
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
									<p style={{textAlign: "justify"}}>Analyze AT&T's financial performance post-acquisition of DirecTV, focusing on Return on Investment (ROI) and identifying any significant accounting adjustments related to the deal.</p>
								</div>
								<div
									className="card"
									onClick={() =>
										handleCardClick(
											"Give me a detailed report on the current state of ed-tech sector in India and US. Can chegg acquire byju's, what would be the impact of such merger and acquisition on the market in every prospect?"
										)
									}
								>
									<p style={{textAlign: "justify"}}>Give me a detailed report on the current state of ed-tech sector in India and US. Can chegg acquire byju's, what would be the impact of such merger and acquisition on the market in every prospect? </p>
									{/* <img src={assets.message_icon} alt="" /> */}
								</div>
								<div
									className="card"
									onClick={() =>
										handleCardClick("Analyze CoStar Group's and LoopNet's financial statements to identify potential areas of legal and financial risk associated with their overlapping business operations.")
									}
								>
									<p style={{textAlign: "justify"}}>Analyze CoStar Group's and LoopNet's financial statements to identify potential areas of legal and financial risk associated with their overlapping business operations.</p>
								</div>
								{/* Your card elements here */}
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
										<ReactMarkdown rehypePlugins={[rehypeRaw]} remarkPlugins={[remarkGfm]}>{resultData}</ReactMarkdown>
									</div>
								)}
							</div>
							{downloadData && (
								<button className="download" onClick={generatePDF}>
									Download
								</button>
							)}
						</div>
					)}
				</div>
				<div className="main-bottom">
					<div className="search-box">
						<input
							onChange={(e) => {
								setInput(e.target.value);
							}}
							value={input}
							type="text"
							placeholder="Enter the Prompt Here"
							onKeyDown={(e) => {
								if (e.key === 'Enter') {
									e.preventDefault();
									handleClick();
								}
							}}
						/>
						<div>
							<img src={assets.gallery_icon} alt="Upload" onClick={triggerFileInput} />
							<input
								webkitdirectory="true"
								multiple
								id="hiddenFileInput"
								type="file"
								style={{ display: 'none' }} // Hide the input field
								onChange={handleFileChange}
							/>
							<img src={assets.mic_icon} alt="" />
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
