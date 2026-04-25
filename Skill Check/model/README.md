# Resume Analyzer - NLP-Based CV Analysis System

An intelligent resume/CV analysis system that uses Natural Language Processing (NLP) to parse, extract, and provide actionable feedback on student CVs. Built with spaCy for NLP and FastAPI for the REST API.

## Features

- **Automatic Section Detection**: Intelligently identifies sections like Contact Info, Summary, Education, Experience, Skills, Projects, Certifications, Awards, Languages, and References
- **Named Entity Recognition**: Extracts names, organizations, locations, and dates using spaCy's NER
- **Skill Extraction**: Identifies technical skills and technologies mentioned in the CV
- **Contact Information Parsing**: Extracts email, phone numbers, and social media links
- **Smart Suggestions**: Provides actionable feedback for improving your CV
- **Comprehensive Analytics**: Returns word count, character count, and detailed section analysis
- **CORS Support**: API supports cross-origin requests from frontend applications

## Tech Stack

- **Backend**: FastAPI (Python web framework)
- **NLP Engine**: spaCy (Named Entity Recognition & linguistic analysis)
- **Server**: Uvicorn (ASGI server)
- **Data Validation**: Pydantic (data validation and serialization)
- **Testing**: pytest (unit testing framework)
- **HTTP Client**: httpx (for testing and requests)

## Project Structure

```
Skill Check/
├── README.md              # Project documentation
├── backend/               # Frontend/backend files
├── frontend/              # Frontend files
└── model/                 # NLP Model and API
    ├── api.py             # FastAPI application and endpoints
    ├── nlp_analyzer.py    # Core NLP pipeline
    ├── requirements.txt   # Python dependencies
    ├── assets/            # Sample CV files for testing
    │   └── sample_cvs/
    │       ├── good_cv.txt
    │       ├── missing_sections_cv.txt
    │       └── poor_cv.txt
    ├── schemas/           # Pydantic data models
    │   ├── __init__.py
    │   └── cv_schema.py   # Request/Response schemas
    └── tests/             # Unit tests
        └── test_analyzer.py
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository** (if applicable)
   ```bash
   cd "Skill Check/model"
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

### Running the API Server

```bash
cd model
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
- **GET** `/health`
  - Returns server status and loaded model info
  - Response: `{"status": "ok", "model": "spaCy en_core_web_sm"}`

#### Root Info
- **GET** `/`
  - Returns service information and usage instructions

#### Analyze CV
- **POST** `/analyze`
  - Analyzes a CV/resume text
  - **Request body**:
    ```json
    {
      "cv_text": "Your CV content as a string..."
    }
    ```
  - **Response**:
    ```json
    {
      "sections_found": ["contact", "summary", "education", "experience", "skills"],
      "skills": ["Python", "FastAPI", "spaCy"],
      "contact_info": {"email": "user@example.com", "phone": "+1-234-567-8900"},
      "named_entities": [
        {"text": "Cairo University", "label": "ORG"},
        {"text": "Ahmed Hassan", "label": "PERSON"}
      ],
      "suggestions": ["Add more technical skills", "Include certifications"],
      "word_count": 245,
      "character_count": 1523
    }
    ```

#### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Example Usage with Python

```python
import httpx

# Initialize client
client = httpx.Client()

# Prepare CV text
cv_text = """
John Doe
john@example.com | +1-234-567-8900

Summary
Software engineer with 3 years of experience in backend development.

Experience
Senior Developer at TechCorp (2022-Present)
- Led development of microservices architecture
- Mentored 5 junior developers

Skills
Python, FastAPI, PostgreSQL, Docker, Kubernetes
"""

# Send request
response = client.post(
    "http://localhost:8000/analyze",
    json={"cv_text": cv_text}
)

# Print results
print(response.json())
```

### Running Tests

```bash
cd model
pytest tests/
```

## CV Analysis Features

### Section Detection
The analyzer detects the following sections:
- **Contact**: Phone, email, LinkedIn, GitHub
- **Summary**: Professional summary or objective
- **Education**: Degrees, universities, GPA
- **Experience**: Work history and internships
- **Skills**: Technical skills and tools
- **Projects**: Portfolio projects and demonstrations
- **Certifications**: Professional certifications and courses
- **Awards**: Honors and achievements
- **Languages**: Spoken languages and fluency levels
- **References**: Professional references

### Named Entity Recognition
Uses spaCy's pretrained models to identify:
- **PERSON**: Names of people
- **ORG**: Organization names
- **GPE**: Geopolitical entities (locations)
- **DATE**: Temporal expressions
- **PRODUCT**: Products and tools

### Smart Suggestions
The analyzer provides suggestions for CV improvement including:
- Missing important sections
- Lack of quantified achievements
- Weak action verbs
- Missing contact information
- Insufficient technical depth

## API Constraints

- **Maximum CV Length**: 50,000 characters
- **Minimum CV Length**: Must not be empty
- **Timeout**: Default request timeout depends on server configuration

## Configuration

The application uses environment defaults:
- **Host**: 0.0.0.0 (accessible from all interfaces)
- **Port**: 8000
- **CORS**: Enabled for all origins (`*`)

To customize, modify `api.py` or pass parameters to `uvicorn`.

## Future Enhancements

- [ ] Support for multiple languages
- [ ] PDF/DOCX file upload support
- [ ] ATS (Applicant Tracking System) compatibility checking
- [ ] Comparative analysis with job descriptions
- [ ] Machine learning-based quality scoring
- [ ] Export analysis results to PDF
- [ ] Batch CV analysis processing



