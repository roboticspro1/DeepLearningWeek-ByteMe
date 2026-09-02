# Ledgerly

A polished, self-contained startup finance tracker for expenses, invoices, receipts, approvals, and employee reimbursements.

## Run locally

From this directory, run:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

Data added through the interface is saved in the browser's local storage. Uploaded document metadata is tracked locally; a production deployment should connect file uploads to secure object storage and add authentication.

## Google automation

Open **Integrations** in the app and follow [GOOGLE_SETUP.md](GOOGLE_SETUP.md) to connect your own Google account. Once connected, new expenses automatically append to Google Sheets and uploaded invoices or receipts are stored in Google Drive.
