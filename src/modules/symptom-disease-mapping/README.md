# Module M7: Symptom-Disease Mapping Database

**Category:** B - Symptom-Disease Diagnosis Support  
**Team:** [Add your team member names]

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MongoDB Atlas

Edit `.streamlit/secrets.toml` with your MongoDB Atlas connection string:
```toml
MONGO_URI = "<connection_string>"
```


## Project Structure

```
symptom-disease-mapping/
├── database/
│   └── connection.py      # MongoDB Atlas connection
├── .streamlit/
│   └── secrets.toml       # MongoDB credentials 
├── requirements.txt       # Python dependencies
└── README.md             # This file
```



