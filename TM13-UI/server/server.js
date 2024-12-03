// server.mjs (or server.js if your package.json has "type": "module")
import express from 'express';
import { mdToPdf } from 'md-to-pdf';
import path from 'path';
import cors from 'cors';

const app = express();
const port = 5000;

// Middleware
app.use(cors()); // Enable Cross-Origin Requests for React frontend

// Body parser middleware
app.use(express.json());

// Endpoint to convert markdown to PDF
app.post('/convert', async (req, res) => {
    const { markdownContent } = req.body;

    try {
        const { path: pdfPath } = await mdToPdf({ content: markdownContent }).then((result) => result);
        res.download(pdfPath); // Send the generated PDF back to the client
    } catch (error) {
        console.error('Error generating PDF:', error);
        res.status(500).send('Error generating PDF');
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
