# Google Sheets Backend Setup Instructions

Please share this document with the person responsible for creating the Google Sheet.

## Overview
We are setting up a Google Sheet to act as a database for the Entrology application form. A "Google Apps Script" will be attached to this sheet to receive data from the website in real-time.

## Steps to Setup

### 1. Create the Google Sheet
1.  Go to [sheets.google.com](https://sheets.google.com) and create a **Blank Spreadsheet**.
2.  Name it (e.g., "Entrology Application Responses").
3.  **Important**: You do NOT need to create the headers manually. The script will automatically create the correct headers when the first user submits data.

### 2. Add the Script
1.  In the Google Sheet, click on **Extensions** in the top menu -> **Apps Script**.
2.  A new tab will open with a code editor.
3.  Delete any code currently in the `Code.gs` file (usually `function myFunction() {...}`).
4.  **Copy and Paste** the following code completely:

```javascript
/*
 * Entrology Backend Script
 * Handle Basic Details and Incremental Aptitude Updates
 */

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    // Wait for up to 10 seconds for other requests to finish
    lock.waitLock(10000); 
  } catch (e) {
    return ContentService.createTextOutput(JSON.stringify({ "result": "error", "message": "Server busy" })).setMimeType(ContentService.MimeType.JSON);
  }

  try {
    // 1. Parse Data
    const params = JSON.parse(e.postData.contents);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    // 2. Setup Headers if not exists
    setupHeaders(sheet);

    // 3. Handle Actions
    if (params.type === 'basic_details') {
      return handleBasicDetails(sheet, params);
    } else if (params.type === 'answer_update') {
      return handleAnswerUpdate(sheet, params);
    } else {
      return ContentService.createTextOutput(JSON.stringify({ "result": "error", "message": "Unknown type" })).setMimeType(ContentService.MimeType.JSON);
    }

  } catch (e) {
    return ContentService.createTextOutput(JSON.stringify({ "result": "error", "error": e.toString() })).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

// Ensure columns exist
function setupHeaders(sheet) {
  const headers = [
    "Timestamp", 
    "Submission ID", 
    "Full Name", 
    "Email", 
    "Mobile", 
    "City", 
    "Qualification", 
    "Selected Course",
    "Status"
  ];
  
  // We assume questions might be Q1 to Q20. Let's pre-populate some or add them dynamically.
  // For safety, let's ensure the first row has these basic headers.
  const lastCol = sheet.getLastColumn();
  if (lastCol === 0) {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold");
    sheet.setFrozenRows(1);
  }
}

function handleBasicDetails(sheet, data) {
  const timestamp = new Date();
  
  // 1. Validations
  if (!data.submissionId || !data.email) {
     return jsonResponse({ "result": "error", "message": "Missing ID or Email" });
  }

  // 2. Initial Status
  const status = "Step 1 Completed";

  // 3. Append Row
  // Order must match setupHeaders: Timestamp, ID, Name, Email, Mobile, City, Qual, Course, Status
  sheet.appendRow([
    timestamp,
    data.submissionId,
    data.fullName,
    data.email,
    data.mobile,
    data.city,
    data.qualification,
    data.selectedCourse,
    status
  ]);

  return jsonResponse({ "result": "success", "message": "User created" });
}

function handleAnswerUpdate(sheet, data) {
  // data = { submissionId, questionId: "q1", answer: "Option B" }
  
  const submissionId = data.submissionId;
  const questionId = data.questionId; // e.g., "q1", "q2"...
  const answer = data.answer;

  // 1. Find the Row by Submission ID
  // We search Column B (Index 2) because that's where Submission ID is.
  const dataRange = sheet.getDataRange();
  const values = dataRange.getValues();
  let rowIndex = -1;

  // Start from row 1 (skipping header row 0)
  for (let i = 1; i < values.length; i++) {
    if (values[i][1] === submissionId) {
      rowIndex = i + 1; // 1-based index
      break;
    }
  }

  if (rowIndex === -1) {
    // If user not found (rare case), you could append or return error. 
    // We will return success to not block frontend, but log it.
    return jsonResponse({ "result": "error", "message": "ID not found" });
  }

  // 2. Find or Create Column for Question
  let colIndex = -1;
  const headers = values[0]; // Row 1 headers
  
  // Try to find the header (e.g., "q1")
  for (let j = 0; j < headers.length; j++) {
    if (headers[j].toString().toLowerCase() === questionId.toLowerCase()) {
      colIndex = j + 1; // 1-based index
      break;
    }
  }

  // If column doesn't exist (e.g., first time answering Q1), create it
  if (colIndex === -1) {
    colIndex = headers.length + 1;
    sheet.getRange(1, colIndex).setValue(questionId); // Add header
  }

  // 3. Update the Cell
  sheet.getRange(rowIndex, colIndex).setValue(answer);
  
  // 4. Update Status if it's the last question (Optional logic handled by frontend sending a 'completed' type? 
  // For now just updating answer is enough. Step 1 handles the 'Status' column initially)
  
  return jsonResponse({ "result": "success" });
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
```

### 3. Save and Deploy
1.  Click the **Save** icon (floppy disk) on the toolbar. Name the project "Entrology Backend".
2.  Click the **Deploy** button (blue button top right) -> **New Deployment**.
3.  In the "Select type" gear icon, choose **Web app**.
4.  Fill in the details:
    *   **Description**: Production v1
    *   **Execute as**: **Me** (your email) -> *Crucial!*
    *   **Who has access**: **Anyone** -> *Crucial! This allows the website to send data without user login.*
5.  Click **Deploy**.
6.  You might be asked to **Authorize Access**. Click "Review Permissions", select your account.
    *   *Note: If you see "Google hasn’t verified this app", click **Advanced** -> **Go to Entrology Backend (unsafe)**. This is safe because it is your own code.*
7.  Copy the **Web App URL**. It will look like `https://script.google.com/macros/s/.../exec`.

### 4. Final Step
Send the **Web App URL** to the developer (me).
