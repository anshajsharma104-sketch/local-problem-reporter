# API Examples - Local Problem Reporter

Complete examples for testing the API using curl, Python, or JavaScript.

## Base URL
```
http://localhost:8000
```

---

## System Endpoints

### Get API Information
```bash
curl http://localhost:8000/
```

Response:
```json
{
  "message": "Local Problem Reporter API",
  "docs": "/docs",
  "version": "1.0.0"
}
```

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy"}
```

### System Information
```bash
curl http://localhost:8000/api/system/info
```

Response:
```json
{
  "api_version": "1.0.0",
  "ai_model": {
    "model": "YOLOv5s",
    "status": "loaded",
    "categories": ["road_damage", "garbage", ...]
  },
  "issue_categories": [...],
  "priority_levels": ["critical", "high", "medium", "low"]
}
```

### Get Scoring Information
```bash
curl http://localhost:8000/api/scoring-info
```

---

## Issue Management Endpoints

### 1. Upload a New Issue

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/issues/upload \
  -F "file=@/path/to/image.jpg" \
  -F "title=Large pothole on Main Street" \
  -F "description=Dangerous pothole causing safety concerns" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060" \
  -F "location_description=Main Street near Central Park"
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/api/issues/upload"
files = {"file": open("road_damage.jpg", "rb")}
data = {
    "title": "Road damage",
    "description": "Large crack in asphalt",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "location_description": "5th Avenue"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**Using JavaScript (Fetch API):**
```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("title", "Garbage in park");
formData.append("description", "Litter scattered around");
formData.append("latitude", 40.7128);
formData.append("longitude", -74.0060);
formData.append("location_description", "Central Park");

const response = await fetch("http://localhost:8000/api/issues/upload", {
  method: "POST",
  body: formData
});

const result = await response.json();
console.log(result);
```

**Response Example:**
```json
{
  "id": 1,
  "title": "Large pothole on Main Street",
  "description": "Dangerous pothole causing safety concerns",
  "issue_type": "road_damage",
  "priority_level": "high",
  "priority_score": 72.5,
  "status": "reported",
  "ai_detected_objects": ["pothole", "asphalt"],
  "ai_confidence": 0.87,
  "latitude": 40.7128,
  "longitude": -74.0060,
  "location_description": "Main Street near Central Park",
  "upvotes": 0,
  "created_at": "2024-03-26T10:30:45.123Z"
}
```

---

### 2. Get All Issues

**Basic request:**
```bash
curl "http://localhost:8000/api/issues/all"
```

**With filters:**
```bash
# By priority
curl "http://localhost:8000/api/issues/all?priority=high"

# By status
curl "http://localhost:8000/api/issues/all?status=reported"

# By type
curl "http://localhost:8000/api/issues/all?issue_type=road_damage"

# Combined filters with pagination
curl "http://localhost:8000/api/issues/all?priority=critical&status=reported&skip=0&limit=20"
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/api/issues/all"
params = {
    "priority": "high",
    "status": "reported",
    "skip": 0,
    "limit": 50
}

response = requests.get(url, params=params)
issues = response.json()

for issue in issues:
    print(f"#{issue['id']}: {issue['title']} ({issue['priority_level']})")
```

**Response Example:**
```json
[
  {
    "id": 1,
    "title": "Large pothole on Main Street",
    "issue_type": "road_damage",
    "priority_level": "high",
    "priority_score": 72.5,
    "status": "reported",
    "created_at": "2024-03-26T10:30:45Z",
    "upvotes": 5
  },
  {
    "id": 2,
    "title": "Water leaking from main pipe",
    "issue_type": "water_leak",
    "priority_level": "critical",
    "priority_score": 85.0,
    "status": "reported",
    "created_at": "2024-03-26T11:15:30Z",
    "upvotes": 12
  }
]
```

---

### 3. Get Issue Details

```bash
curl "http://localhost:8000/api/issues/1"
```

**Using Python:**
```python
import requests

issue_id = 1
response = requests.get(f"http://localhost:8000/api/issues/{issue_id}")
issue = response.json()

print(f"Title: {issue['title']}")
print(f"Type: {issue['issue_type']}")
print(f"Status: {issue['status']}")
print(f"Priority: {issue['priority_level']} ({issue['priority_score']}/100)")
```

---

### 4. Upvote an Issue

```bash
curl -X POST "http://localhost:8000/api/issues/1/upvote"
```

**Using Python:**
```python
import requests

issue_id = 1
response = requests.post(f"http://localhost:8000/api/issues/{issue_id}/upvote")
result = response.json()

print(f"New upvotes: {result['upvotes']}")
print(f"New priority score: {result['priority_score']}")
```

**Response:**
```json
{
  "upvotes": 6,
  "priority_score": 75.2
}
```

---

### 5. Update Issue Status (Authority Only)

**Investigation:**
```bash
curl -X PATCH "http://localhost:8000/api/issues/1/status" \
  -G \
  --data-urlencode "new_status=investigating" \
  --data-urlencode "notes=Sent inspection team to location"
```

**Resolved:**
```bash
curl -X PATCH "http://localhost:8000/api/issues/1/status" \
  -G \
  --data-urlencode "new_status=resolved" \
  --data-urlencode "notes=Pothole filled and repaired"
```

**Using Python:**
```python
import requests

issue_id = 1
response = requests.patch(
    f"http://localhost:8000/api/issues/{issue_id}/status",
    params={
        "new_status": "resolved",
        "notes": "Completed repairs today"
    }
)

print(response.json())
```

---

### 6. Get Issues by Type

```bash
curl "http://localhost:8000/api/issues/by-type/road_damage"
```

Response:
```json
[
  {
    "id": 1,
    "title": "Large pothole",
    "priority_level": "high",
    "status": "reported",
    "location": {"lat": 40.7128, "lon": -74.0060}
  }
]
```

---

## Analytics Endpoints

### 1. Dashboard Overview

```bash
curl "http://localhost:8000/api/analytics/dashboard"
```

**Using Python:**
```python
import requests

response = requests.get("http://localhost:8000/api/analytics/dashboard")
dashboard = response.json()

print(f"Total Issues: {dashboard['total_issues']}")
print(f"Critical: {dashboard['critical_issues']}")
print(f"High: {dashboard['high_issues']}")
print(f"Resolved: {dashboard['resolved_issues']}")
print(f"Pending: {dashboard['pending_issues']}")
```

**Response Example:**
```json
{
  "total_issues": 25,
  "critical_issues": 3,
  "high_issues": 8,
  "medium_issues": 10,
  "low_issues": 4,
  "resolved_issues": 12,
  "pending_issues": 13,
  "issue_types": {
    "road_damage": 10,
    "garbage": 5,
    "water_leak": 6,
    "traffic": 4
  },
  "priority_distribution": {
    "critical": 3,
    "high": 8,
    "medium": 10,
    "low": 4
  },
  "status_distribution": {
    "reported": 8,
    "investigating": 5,
    "resolved": 12
  },
  "recent_issues": [...],
  "top_locations": [...]
}
```

---

### 2. Statistics by Type

```bash
curl "http://localhost:8000/api/analytics/stats/by-type"
```

Response:
```json
{
  "road_damage": {
    "total": 10,
    "avg_priority_score": 72.5,
    "resolved": 4,
    "pending": 6,
    "resolution_rate": 40.0
  },
  "water_leak": {
    "total": 6,
    "avg_priority_score": 81.2,
    "resolved": 3,
    "pending": 3,
    "resolution_rate": 50.0
  }
}
```

---

### 3. Resolution Rate

```bash
curl "http://localhost:8000/api/analytics/stats/resolution-rate"
```

Response:
```json
{
  "total_issues": 25,
  "resolved": 12,
  "pending": 13,
  "overall_resolution_rate": 48.0,
  "avg_resolution_time_hours": "72:45:30",
  "by_type": {
    "road_damage": {
      "total": 10,
      "resolved": 4,
      "rate": 40.0
    }
  }
}
```

---

### 4. Priority Timeline

```bash
# Last 30 days
curl "http://localhost:8000/api/analytics/stats/priority-timeline?days=30"

# Last 7 days
curl "http://localhost:8000/api/analytics/stats/priority-timeline?days=7"
```

---

### 5. Top Priority Issues

```bash
# Top 20 unresolved issues
curl "http://localhost:8000/api/analytics/stats/top-priority?limit=20"
```

Response:
```json
[
  {
    "id": 1,
    "title": "Water leaking from main pipe",
    "issue_type": "water_leak",
    "priority_score": 92.3,
    "priority_level": "critical",
    "location": "Downtown - 5th Avenue",
    "upvotes": 18,
    "ai_confidence": 0.95,
    "created_at": "2024-03-25T08:30:00Z"
  }
]
```

---

### 6. Export to CSV

```bash
curl "http://localhost:8000/api/analytics/export/csv" > issues_export.csv

# Or in Python:
import requests

response = requests.get("http://localhost:8000/api/analytics/export/csv")
with open("issues.csv", "wb") as f:
    f.write(response.content)
```

---

## Complete Example: End-to-End Flow

```bash
#!/bin/bash

# 1. Upload an issue
echo "1. Uploading issue..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/issues/upload \
  -F "file=@./test_image.jpg" \
  -F "title=Dangerous pothole" \
  -F "description=Large hole in the road" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060" \
  -F "location_description=Main Street")

ISSUE_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
echo "Issue created with ID: $ISSUE_ID"

# 2. Get issue details
echo -e "\n2. Getting issue details..."
curl -s "http://localhost:8000/api/issues/$ISSUE_ID" | jq .

# 3. Upvote the issue
echo -e "\n3. Upvoting issue..."
curl -s -X POST "http://localhost:8000/api/issues/$ISSUE_ID/upvote" | jq .

# 4. Get dashboard
echo -e "\n4. Getting dashboard..."
curl -s "http://localhost:8000/api/analytics/dashboard" | jq .total_issues

# 5. Update status (authority)
echo -e "\n5. Updating status..."
curl -s -X PATCH "http://localhost:8000/api/issues/$ISSUE_ID/status" \
  -G --data-urlencode "new_status=investigating" | jq .

echo -e "\n✓ Complete end-to-end test finished!"
```

---

## Testing with Postman

Import this into Postman as a collection:

```json
{
  "info": {
    "name": "Local Problem Reporter API",
    "version": "1.0"
  },
  "item": [
    {
      "name": "Upload Issue",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/api/issues/upload",
        "body": {
          "mode": "formdata",
          "formdata": [
            {"key": "file", "type": "file"},
            {"key": "title", "value": "Test Issue"},
            {"key": "latitude", "value": "40.7128"}
          ]
        }
      }
    },
    {
      "name": "Get All Issues",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/api/issues/all?limit=50"
      }
    },
    {
      "name": "Dashboard",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/api/analytics/dashboard"
      }
    }
  ]
}
```

---

## Error Handling

### Example Error Response:

```json
{
  "detail": "Invalid file type. Only jpg, jpeg, png, gif allowed"
}
```

### Common Status Codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Server Error

---

Happy testing! 🚀
