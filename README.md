# LinkedIn Profiles API

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### 1. Get All Profiles (Paginated)

**URL:** `/profiles`

**Method:** `GET`

**Query Parameters:**

- `page` (int, default: 1): Page number
- `per_page` (int, default: 10): Items per page

**Response:**

```json
{
  "data": [
    {
      "_id": "profile_id_123",
      "name": "John Doe",
      "position": "Software Engineer",
      "location": "San Francisco, CA",
      "open_to_work": true,
      "about": "Passionate about coding...",
      "url": "https://www.linkedin.com/in/johndoe/"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 100
}
```

---

### 2. Get Profile Details by ID

**URL:** `/profiles/<profile_id>`

**Method:** `GET`

**Response:**

```json
{
  "profile": {
    "_id": "profile_id_123",
    "name": "John Doe",
    "position": "Software Engineer",
    "location": "San Francisco, CA",
    "open_to_work": true,
    "about": "Passionate about coding...",
    "url": "https://www.linkedin.com/in/johndoe/"
  },
  "experiences": [
    {
      "company_page": "https://www.companyxyz.com",
      "role": "Software Developer",
      "work_at": "Company XYZ",
      "duration": "Jul 2022 - Present · 30 mos.",
      "location": "San Francisco, CA",
      "role_summery": "Developed and maintained web applications..."
    }
  ],
  "educations": [
    {
      "university_url": "https://www.universityxyz.edu",
      "university_name": "University XYZ",
      "degree": "Bachelor's Degree",
      "field_of_study": "Computer Science",
      "start_date": "Sep 2016",
      "end_date": "May 2020",
      "grade": "3.8",
      "skills": "Python, Java, Data Structures, Algorithms"
    }
  ]
}
```

### 3. Search Profiles

**URL:** `/profiles/search`

**Method:** `GET`

**Query Parameters:**

- `name` (string): Filter by profile name
- `location` (string): Filter by location
- `headline` (string): Filter by headline/position
- `company` (string): Filter by company name in experiences
- `university` (string): Filter by university name in education
- `jobTitle` (string): Filter by job title in experiences
- `industry` (string): Filter by industry
- `page` (int, default: 1): Page number
- `per_page` (int, default: 10): Items per page

**Response:**

```json
{
  "data": [
    {
      "_id": "profile_id_123",
      "name": "John Doe",
      "position": "Software Engineer",
      "location": "San Francisco, CA",
      "open_to_work": true,
      "about": "Passionate about coding...",
      "url": "https://www.linkedin.com/in/johndoe/"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 100
}

---

## Example Requests

### Get Profiles (Page 2, 5 items per page)

```bash
curl -X GET "http://localhost:5000/api/profiles?page=1&per_page=5"
```

### Get Profile Details

```bash
curl -X GET "http://localhost:5000/api/profiles/{your_profile_id}"
```

### Search Profiles

```bash
curl -X GET "http://localhost:5000/api/profiles/search?query=Delhi
```