import React, { useState } from 'react';
import { marked } from 'marked';
import html2pdf from 'html2pdf.js';

const MarkdownToPDF = () => {
  const [markdownContent, setMarkdownContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleMarkdownChange = (e) => {
    setMarkdownContent(e.target.value);
  };

  const generatePDF = () => {
    setIsGenerating(true);

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
        font-size: 12px;
        line-height: 1.5; /* Adjust this value to set the line gap */
        margin: 20px;
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
        filename: 'converted-markdown.pdf',
        html2canvas: { scale: 2 },  // Increase the scale for better resolution
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      })
      .save()
      .finally(() => setIsGenerating(false));
  };

  return (
    <div className="markdown-to-pdf">
      <h1>Markdown to PDF</h1>
      <textarea
        rows="10"
        cols="50"
        value={markdownContent}
        onChange={handleMarkdownChange}
        placeholder="Enter your Markdown content here..."
      ></textarea>
      <br />
      <button onClick={generatePDF} disabled={isGenerating}>
        {isGenerating ? 'Generating PDF...' : 'Generate PDF'}
      </button>
    </div>
  );
};

export default MarkdownToPDF;
