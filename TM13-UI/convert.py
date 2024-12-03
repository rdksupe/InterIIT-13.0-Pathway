from markdown_pdf import Section, MarkdownPdf


def convert(content):

    pdf = MarkdownPdf()

    # Updated CSS with reduced font size, horizontal line, and blue first row
    css = """
    /* General styling for the entire document */
    body {
        font-family: 'Arial', sans-serif;
        margin: 20px;
        line-height: 1.4;
        font-size: 12px; /* Reduced font size */
    }


    /* Horizontal line below the title */
    h1 + hr {
        border: 0;
        border-top: 1px solid #ddd;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    p {
        margin-bottom: 8px; /* Reduced paragraph spacing */
        font-size: 12px; /* Consistent font size for paragraphs */
    }

    /* Table styling */
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    th, td {
        padding: 8px; /* Reduced padding */
        text-align: left;
        border: 1px solid #ddd;
        font-size: 12px; /* Reduced font size for table text */
    }



    tr:first-child {
        background-color: blue; /* Make the first row blue */
        color: blue; /* Text color in the first row */
    }

    tr:nth-child(even) {
        background-color: blue; /* Light gray background for even rows */
    }

    tr:hover {
        background-color: #f1f1f1; /* Hover effect on rows */
    }
    """

    # Add section with the custom CSS
    pdf.add_section(Section(content), user_css=css)

    # Save the generated PDF
    pdf.save("generated_output.pdf")

